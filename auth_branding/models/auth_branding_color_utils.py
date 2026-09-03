import base64
import colorsys
from collections import Counter
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from odoo import _
from odoo.exceptions import ValidationError


MAX_LOGO_BYTES = 5 * 1024 * 1024


def _rgb_to_hex(color):
    return "#%02X%02X%02X" % color


def _color_score(item):
    color, frequency = item
    red, green, blue = (channel / 255 for channel in color)
    _hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    return frequency * (0.4 + saturation) * (0.65 + value)


def extract_logo_palette(image_data, color_count=2):
    """Return prominent opaque colors from a base64-encoded logo."""
    if not image_data:
        return []
    try:
        raw = base64.b64decode(image_data, validate=True)
    except (ValueError, TypeError) as error:
        raise ValidationError(_("The uploaded logo is not a valid image.")) from error
    if len(raw) > MAX_LOGO_BYTES:
        raise ValidationError(_("Logo images must be smaller than 5 MB."))

    try:
        with Image.open(BytesIO(raw)) as image:
            image.thumbnail((160, 160))
            rgba = image.convert("RGBA")
            pixels = [
                (red, green, blue)
                for red, green, blue, alpha in rgba.getdata()
                if alpha >= 96
            ]
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ValidationError(_("The uploaded logo could not be processed.")) from error

    if not pixels:
        return []

    buckets = Counter(
        ((red // 16) * 16 + 8, (green // 16) * 16 + 8, (blue // 16) * 16 + 8)
        for red, green, blue in pixels
    )
    useful = [
        item
        for item in buckets.items()
        if not (all(channel >= 240 for channel in item[0]))
        and not (all(channel <= 16 for channel in item[0]))
    ]
    ranked = sorted(useful or buckets.items(), key=_color_score, reverse=True)

    selected = []
    for color, _frequency in ranked:
        if all(sum(abs(a - b) for a, b in zip(color, other)) >= 96 for other in selected):
            selected.append(color)
        if len(selected) == color_count:
            break
    return [_rgb_to_hex(color) for color in selected]
