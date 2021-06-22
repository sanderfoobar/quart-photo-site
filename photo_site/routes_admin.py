import re
from typing import List
from datetime import datetime
import os
import tempfile

import magic
import aiofiles
from PIL import Image
from quart import render_template, request, redirect, url_for, jsonify, Blueprint, abort, flash
from quart_auth import AuthUser, login_user, login_required, logout_user, current_user

import settings
from photo_site.utils import image_resize

bp_routes_admin = Blueprint('routes_admin', __name__, url_prefix='/admin')


@bp_routes_admin.route('/')
@login_required
async def admin():
    from photo_site.models import Album, PhotoAlbumAssoc, Photo, Settings

    q = Album.select().order_by(Album.date_added.desc())
    albums = [a for a in q]

    about_text = Settings.by_key("about")
    return await render_template("admin.html", albums=albums, about_text=about_text)


@bp_routes_admin.route('/p/add', methods=['POST'])
@login_required
async def photos_add():
    from photo_site.models import Photo

    request_files = await request.files
    files = request_files.getlist("photos")

    photos = []
    for f in files:
        tmp_name = next(tempfile._get_candidate_names())
        fn = f.filename
        filename, file_extension = os.path.splitext(fn)
        filename = f"{tmp_name}{file_extension}"
        filename_thumb = f"{tmp_name}_thumb{file_extension}"
        filepath = os.path.join(settings.photos_dir, filename)
        filepath_thumb = os.path.join(settings.photos_dir, filename_thumb)
        await f.save(filepath)

        # create thumbnail version
        thumb = image_resize(filepath, max_bounding_box=900, quality=85)
        async with aiofiles.open(filepath_thumb, mode="wb") as f:
            await f.write(thumb)

        image = Image.open(filepath)
        image = image.convert('RGB')
        width = image.width
        height = image.height

        # resize image if it is too big
        if max([height, width]) > settings.image_max_bounding_box:
            resized = image_resize(filepath, max_bounding_box=settings.image_max_bounding_box, quality=95)
            async with aiofiles.open(filepath, mode="wb") as f:
                await f.write(resized)

            image = Image.open(filepath)
            image = image.convert('RGB')
            width = image.width
            height = image.height

        # determine format
        landscape = True
        if width < height:
            landscape = False

        photo = Photo.create(filename=filename, landscape=landscape, height=height, width=width)
        photos.append(photo)

    if len(photos) == 1:
        return redirect(url_for('routes.photo_view', photo_id=photos[0].id))

    p_ids = [p.id for p in photos]
    p_ids = ','.join(map(str, p_ids))
    url = url_for('routes_admin.photos_edit', p_ids=p_ids)
    url = url.replace("%2C", ",")
    return redirect(url)


@bp_routes_admin.route('/p/delete/<int:photo_id>')
@login_required
async def photo_delete(photo_id: int):
    from photo_site.models import Photo, Album, PhotoAlbumAssoc
    photo = Photo.select().where(Photo.id == photo_id).get()
    os.remove(os.path.join(settings.photos_dir, photo.filename))
    os.remove(os.path.join(settings.photos_dir, photo.thumb))

    PhotoAlbumAssoc.delete().where(PhotoAlbumAssoc.photo == photo_id).execute()
    Photo.delete().where(Photo.id == photo_id).execute()
    return redirect(url_for('routes_admin.admin'))


@bp_routes_admin.route('/p/edit/<path:p_ids>', methods=['GET', 'POST'])
@login_required
async def photos_edit(p_ids):
    from photo_site.models import Photo, Album, PhotoAlbumAssoc
    pids = list(map(int, p_ids.split(",")))

    q = Photo.select().where(Photo.id.in_(pids))
    photos: List[Photo] = [p for p in q]

    q = Album.select().order_by(Album.date_added.desc())
    albums = [a for a in q]

    if request.method == "POST":
        blob = await request.form
        try:
            album_ids = list(map(int, blob.getlist('albums')))
        except:
            album_ids = []

        data = dict(blob)
        data['albums'] = album_ids
        for p in photos:
            edit_photo(photo=p, albums=albums, data=data, batch=len(photos) > 1)

    if len(photos) > 1:
        return await render_template("photos_edit.html", photos=photos, albums=albums, p_ids=p_ids)
    else:
        return redirect(url_for("routes.photo_view", photo_id=photos[0].id))


def edit_photo(photo, albums, data: dict, batch=False):
    from photo_site.models import Photo, Album, PhotoAlbumAssoc
    albums_lookup = {a.id: a for a in albums}

    date_taken = None
    try:
        from dateutil.parser import parse as dateutil_parse
        date_taken = data.get('date_taken')
        date_taken = dateutil_parse(date_taken)
    except:
        pass

    if isinstance(date_taken, datetime):
        photo.date_taken = date_taken

    camera = data.get('camera_model', '')
    optics = data.get('optics', '')
    location = data.get('location', '')
    description = data.get('description', '')
    title = data.get('title', '')

    if batch and camera:
        photo.camera = camera
    elif not batch:
        photo.camera = camera

    if batch and optics:
        photo.optics = optics
    elif not batch:
        photo.optics = optics

    if batch and location:
        photo.location = location
    elif not batch:
        photo.location = location

    if batch and description:
        photo.description = description
    elif not batch:
        photo.description = description

    if batch and title:
        photo.title = title
    elif not batch:
        photo.title = title

    PhotoAlbumAssoc.delete().where(PhotoAlbumAssoc.photo == photo.id).execute()
    for aid in data['albums']:
        try:
            PhotoAlbumAssoc.create(album=albums_lookup[aid], photo=photo)
        except Exception as ex:
            pass

    photo.save()


@bp_routes_admin.route('/a/add', methods=['GET', 'POST'])
@login_required
async def album_add():
    from photo_site.models import Album

    if request.method == "POST":
        blob = await request.form
        name = blob.get('name')
        desc = blob.get('description')
        Album.create(name=name, description=desc)
        await flash("album created")
        return redirect(url_for('routes_admin.admin'))

    return await render_template("album_add.html")


@bp_routes_admin.route('/a/<int:album_id>/edit', methods=['GET', 'POST'])
@login_required
async def album_edit(album_id):
    from photo_site.models import Album
    album = Album.select().where(Album.id == album_id).get()

    if request.method == "POST":
        blob = await request.form
        album.name = blob.get('name')
        album.description = blob.get('description')
        album.save()

        await flash("album edited")
        return redirect(url_for('routes_admin.admin'))

    return await render_template("album_edit.html", album=album)


@bp_routes_admin.route('/a/<int:album_id>/delete', methods=['GET'])
@login_required
async def album_delete(album_id):
    from photo_site.models import Album, PhotoAlbumAssoc

    try:
        PhotoAlbumAssoc.delete().where(PhotoAlbumAssoc.album == album_id).execute()
    except:
        pass

    Album.delete().where(Album.id == album_id).execute()
    await flash("album removed")
    return redirect(url_for('routes_admin.admin'))


@bp_routes_admin.route('/about/edit', methods=['POST'])
@login_required
async def about_edit():
    from photo_site.models import Settings

    blob = await request.form
    about_text = blob['about_text']

    try:
        setting = Settings.select().where(Settings.key == "about").get()
        setting.value = about_text
        setting.save()
    except:
        setting = Settings.create(key="about", value=about_text)

    await flash("about text edited")
    return redirect(url_for('routes_admin.admin'))


@bp_routes_admin.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "POST":
        blob = await request.form
        pwd = blob.get("pwd")
        if settings.password == pwd:
            login_user(AuthUser(1))
            return redirect(url_for('routes_admin.admin'))
        else:
            await flash("bad password")

    return await render_template("login.html")


@bp_routes_admin.route("/logout")
async def logout():
    logout_user()
    return redirect(url_for('routes.index'))
