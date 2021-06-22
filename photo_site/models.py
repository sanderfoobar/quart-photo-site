import os
import re
import random
from typing import Optional, List
from datetime import datetime

from peewee import SqliteDatabase, SQL, ForeignKeyField
import peewee as pw

import settings

db = SqliteDatabase(f"{settings.cwd}/data/db.sqlite3")


class Settings(pw.Model):
    id = pw.AutoField()
    key = pw.CharField(index=True, unique=True)
    value = pw.CharField()

    @staticmethod
    def by_key(key: str):
        try:
            setting = Settings.select().where(Settings.key == key).get()
            return setting.value
        except:
            return ""

    class Meta:
        database = db


class Album(pw.Model):
    id = pw.AutoField()
    date_added = pw.DateTimeField(default=datetime.now)
    name = pw.CharField(index=True, unique=True)
    description = pw.CharField(index=True)

    @property
    def random_img(self):
        assocs = PhotoAlbumAssoc.select().join(Photo).where((PhotoAlbumAssoc.album == self.id), (Photo.landscape == True))
        e = 1
        # assocs: List[PhotoAlbumAssoc] = PhotoAlbumAssoc.select().where(PhotoAlbumAssoc.album == self.id)
        try:
            assoc = random.choice(assocs)
            return assoc.photo
        except:
            pass

    class Meta:
        database = db


class Photo(pw.Model):
    id = pw.AutoField()
    date_added = pw.DateTimeField(default=datetime.now)

    title = pw.CharField(index=True, null=True, default="")
    filename: str = pw.CharField(index=True)
    camera = pw.CharField(index=True, null=True, default="")
    optics = pw.CharField(index=True, null=True, default="")
    date_taken = pw.DateTimeField(null=True)
    description = pw.CharField(default="", null=True)
    views = pw.IntegerField(default=0)
    location = pw.IntegerField(default='')
    height = pw.IntegerField()
    width = pw.IntegerField()
    landscape = pw.BooleanField(default=True)

    @property
    def album_ids(self):
        return [a.id for a in self.albums]

    @property
    def thumb(self):
        filename, ext = os.path.splitext(self.filename)
        return f"{filename}_thumb{ext}"

    class Meta:
        database = db


class PhotoAlbumAssoc(pw.Model):
    album = ForeignKeyField(Album, backref='photos', index=True)
    photo = ForeignKeyField(Photo, backref='albums', index=True)

    class Meta:
        database = db
        indexes = (
            (('album_id', 'photo_id'), True),
        )
