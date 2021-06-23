from quart import render_template, request, redirect, url_for, jsonify, Blueprint, abort, flash, send_from_directory

import settings

bp_routes = Blueprint('routes', __name__)


@bp_routes.route('/')
@bp_routes.route('/<int:page>')
async def index(page: int = 1):
    from photo_site.models import Photo, PhotoAlbumAssoc, Album
    limit = 100
    offset = (page - 1) * limit
    photos = Photo.select(Photo).order_by(Photo.date_added.desc()).limit(limit).offset(offset)

    page_previous = None
    if page > 1:
        page_previous = url_for('routes.index', page=page - 1)

    page_next = url_for('routes.index', page=page + 1)
    return await render_template("index.html", photos=photos, page_next=page_next, page_previous=page_previous)


@bp_routes.route('/about')
async def about():
    from photo_site.models import Settings
    about_text = Settings.by_key("about")
    return await render_template("about.html", about_text=about_text)


@bp_routes.route('/a/')
async def albums_view():
    from photo_site.models import Album
    albums = Album.select().order_by(Album.date_added.desc())
    return await render_template("albums.html", albums=albums)


@bp_routes.route('/a/<int:album_id>')
@bp_routes.route('/a/<int:album_id>/<int:page>')
async def album_view(album_id, page: int = 1):
    from photo_site.models import Photo, PhotoAlbumAssoc, Album
    limit = 100
    offset = (page - 1) * limit

    album = Album.select().where(Album.id == album_id).get()
    photos = Photo.select(Photo).join(PhotoAlbumAssoc)\
        .where(PhotoAlbumAssoc.album == album_id).\
        order_by(Photo.date_added.desc())\
        .limit(limit).offset(offset)

    page_next = url_for("routes.album_view", album_id=album_id, page=page+1)
    page_previous = url_for("routes.album_view", album_id=album_id, page=page - (1 if page > 1 else 0))

    return await render_template("index_album.html", album=album, photos=photos, page_next=page_next, page_previous=page_previous)


@bp_routes.route('/a/<int:album_id>/p/<int:photo_id>')
async def album_photo_view(album_id: int, photo_id: int):
    from photo_site.models import Photo, PhotoAlbumAssoc, Album
    album = Album.select().where(Album.id == album_id).get()
    assoc = PhotoAlbumAssoc.select().where((PhotoAlbumAssoc.photo == photo_id),
                                           (PhotoAlbumAssoc.album == album.id)).get()
    albums = Album.select().order_by(Album.date_added.desc())

    q = Photo.select(Photo).join(PhotoAlbumAssoc)\
        .where(PhotoAlbumAssoc.album == album_id).\
        order_by(Photo.date_added.desc())
    photos = [p for p in q]

    # pagination stuff
    next_photo = ""
    previous_photo = ""
    for i, p in enumerate(photos):
        if p.id == photo_id:
            try:
                _p = photos[i + 1]
                next_photo = url_for("routes.album_photo_view", album_id=album.id, photo_id=_p.id)
            except:
                pass

            try:
                if i <= 0:
                    raise Exception("")
                _p = photos[i - 1]
                previous_photo = url_for("routes.album_photo_view", album_id=album.id, photo_id=_p.id)
            except:
                pass

    photo = Photo.select().where(Photo.id == photo_id).get()
    photo.albums = [a for a in Album.select().join(PhotoAlbumAssoc).where(PhotoAlbumAssoc.photo == photo)]

    return await render_template(
        "photo_view.html",
        album=album,
        albums=albums,
        photo=photo,
        next_photo=next_photo,
        previous_photo=previous_photo)


@bp_routes.route('/p/<int:photo_id>')
async def photo_view(photo_id):
    from photo_site.models import Photo, PhotoAlbumAssoc, Album

    photo = Photo.select().where(Photo.id == photo_id).get()

    # slow query ... whatever
    stream = Photo.select(Photo.id, Photo.date_added).order_by(Photo.date_added.desc())
    stream = [i.id for i in stream]

    # pagination stuff
    previous_photo = None
    next_photo = None
    for i, p_id in enumerate(stream):
        if p_id == photo_id:
            try:
                _p = stream[i + 1]
                next_photo = url_for("routes.photo_view", photo_id=_p)
            except:
                pass

            try:
                if i <= 0:
                    raise Exception("")
                _p = stream[i - 1]
                previous_photo = url_for("routes.photo_view", photo_id=_p)
            except:
                pass

    # :(
    photo.albums = [a for a in Album.select().join(PhotoAlbumAssoc).where(PhotoAlbumAssoc.photo == photo)]
    albums = [a for a in Album.select()]

    return await render_template(
        "photo_view.html",
        photo=photo,
        previous_photo=previous_photo,
        next_photo=next_photo,
        albums=albums
    )


@bp_routes.route('/p/static/<path:filename>')
async def photo_src(filename):
    from photo_site.models import Photo
    photo = Photo.select().where(Photo.filename == filename.replace("_thumb", "")).get()
    photo.views += 1
    photo.save()
    return await send_from_directory(settings.photos_dir, filename)


@bp_routes.errorhandler(404)
@bp_routes.errorhandler(500)
async def error(e):
    msg = str(e)
    try:
        if e.description:
            msg = f"{msg} - {e.description}"
    except:
        pass

    return await render_template("error.html", message=msg)


@bp_routes.route("/favicon.ico")
async def favicon():
    return "ok", 200
