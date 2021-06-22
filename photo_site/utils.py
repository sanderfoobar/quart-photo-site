import re
import json
import asyncio
import os
import random
from datetime import datetime
from typing import List, Union
from io import BytesIO

from PIL import Image

import settings


def image_resize(filepath: str, max_bounding_box: int = 1200, quality: int = 90) -> bytes:
    image = Image.open(filepath)
    image = image.convert('RGB')

    if max([image.height, image.width]) > max_bounding_box:
        image.thumbnail((max_bounding_box, max_bounding_box), Image.BICUBIC)

    data = list(image.getdata())
    image_without_exif = Image.new(image.mode, image.size)
    image_without_exif.putdata(data)

    buffer = BytesIO()
    image_without_exif.save(buffer, "JPEG", quality=quality)
    buffer.seek(0)

    return buffer.read()
