# siderequest.py

from flask import request, send_file
from PIL import Image
import io
import json

# -------- PNG encoder (dict -> image) --------
def encode_siderequest_image(json_data: dict, width=16, height=16):
    json_str = json.dumps(json_data)
    data_bytes = json_str.encode("utf-8") + b'\x00' * (width * height * 3 - len(json_str))

    img = Image.new("RGB", (width, height), (0, 0, 0))
    pixels = img.load()
    index = 0
    for y in range(height):
        for x in range(width):
            if index < len(data_bytes):
                r = data_bytes[index]
                g = data_bytes[index+1] if index+1 < len(data_bytes) else 0
                b = data_bytes[index+2] if index+2 < len(data_bytes) else 0
                pixels[x, y] = (r, g, b)
                index += 3
            else:
                break

    img_io = io.BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return img_io

# -------- decorator that handles d/s params --------
def siderequest(func):
    """
    Wrap a normal Flask endpoint so it reads ?d=?s= and returns a PNG.
    The wrapped function should simply return a Python dict.
    """
    def wrapper(*args, **kwargs):
        json_str = request.args.get("d", "{}")
        size_str = request.args.get("s", "16")

        try:
            size = int(size_str)
            if size <= 0: raise ValueError
        except ValueError:
            return "Invalid size 's'", 400

        try:
            incoming_data = json.loads(json_str)
        except json.JSONDecodeError:
            return "Invalid JSON in 'd'", 400

        response_dict = func(incoming_data)

        img_io = encode_siderequest_image(response_dict, width=size, height=size)
        response = send_file(img_io, mimetype='image/png')
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Expires"] = "0"
        response.headers["Pragma"] = "no-cache"
        return response

    wrapper.__name__ = func.__name__
    return wrapper
