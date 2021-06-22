## Quart Photo Site

A photo site made using Python3 asyncio with the Quart framework.

Made as an alternative for people who want to self-host their photos without relying on
BigTech™ like flickr or instagram.

Hacked together in 2 days so code quality is questionable at times (but it is secure).

[Live example](https://photo.sanderf.nl/)

### Features

This project aims to be minimalistic.:

- No javascript
- SQLite based backend
- Few dependencies
- Admin interface for adding photos / albums
- Add metadata to photos (limited)
- Automatic resizing of images (thumbnail generation)

### Installation

```
apt install -y python3-virtualenv libjpeg-dev libpng-dev
```

1. Clone project
2. Create virtualenv
3. `pip install -r requirements.txt`
4. copy `settings.py_example` to `settings.py`, change the passwords
5. run `run.py` and call it a day
6. Optionally put it behind nginx

### Screenshots

![](https://raw.githubusercontent.com/sferdi0/quart-photo-site/master/photo_site/static/example2.png)
![](https://raw.githubusercontent.com/sferdi0/quart-photo-site/master/photo_site/static/example1.png)
![](https://raw.githubusercontent.com/sferdi0/quart-photo-site/master/photo_site/static/example3.png)

### License

WTFPL