## Quart Photo Site

A photo site made using Python3 asyncio with the Quart framework.

Made as an alternative for people who want to self-host their photos without relying on
BigTech™ like flickr or instagram.

Hacked together in 2 days so code quality is questionable at times (but it is secure).

### Features

This project aims to be minimalistic.:

- No javascript
- SQLite based backend
- Few dependencies
- Admin interface for adding photos / albums
- Add metadata to photos (limited)
- Automatic resizing of images (thumbnail generation)

### Installation

1. Clone project
2. Create virtualenv
3. copy `settings.py_example` to `settings.py`, change the passwords
4. run `run.py` and call it a day
5. Optionally put it behind nginx

### Screenshots

![](https://raw.githubusercontent.com/sferdi0/quart-photo-site/master/photo_site/static/example2.png)
![](https://raw.githubusercontent.com/sferdi0/quart-photo-site/master/photo_site/static/example1.png)
![](https://raw.githubusercontent.com/sferdi0/quart-photo-site/master/photo_site/static/example3.png)

### License

WTFPL