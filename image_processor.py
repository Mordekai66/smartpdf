import io
import math

import fitz
import numpy as np
from PIL import Image


BACKGROUND = (28, 31, 38)
FOREGROUND = (232, 235, 241)
NEUTRAL_THRESHOLD = 28
DARKNESS_CURVE = 0.85


def get_image_rectangles(page, padding=0.5):
    """Find displayed image areas on a PDF page."""
    rectangles = []

    try:
        for info in page.get_image_info(xrefs=True):
            bbox = info.get("bbox")
            if not bbox:
                continue

            rect = fitz.Rect(bbox) & page.rect
            if rect.is_empty or rect.is_infinite:
                continue

            rect = fitz.Rect(
                rect.x0 - padding,
                rect.y0 - padding,
                rect.x1 + padding,
                rect.y1 + padding,
            ) & page.rect

            if not rect.is_empty:
                rectangles.append(rect)

    except Exception as error:
        print(f"Warning: image detection failed: {error}")

    return rectangles


def restore_original_image_regions(
    original_image,
    processed_image,
    rectangles,
    page_rect,
    scale,
    pix_x=0,
    pix_y=0,
):
    """Restore the original rendered pixels inside image bounding boxes."""
    for rect in rectangles:
        x0 = max(0, math.floor((rect.x0 - page_rect.x0) * scale - pix_x))
        y0 = max(0, math.floor((rect.y0 - page_rect.y0) * scale - pix_y))
        x1 = min(original_image.width, math.ceil((rect.x1 - page_rect.x0) * scale - pix_x))
        y1 = min(original_image.height, math.ceil((rect.y1 - page_rect.y0) * scale - pix_y))

        if x1 <= x0 or y1 <= y0:
            continue

        processed_image.paste(original_image.crop((x0, y0, x1, y1)), (x0, y0))

    return processed_image


def smart_dark_mapping(
    image,
    background=BACKGROUND,
    foreground=FOREGROUND,
    neutral_threshold=NEUTRAL_THRESHOLD,
    darkness_curve=DARKNESS_CURVE,
):
    """Map neutral page colors to a dark palette; leave colored pixels alone."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0

    max_channel = np.max(rgb, axis=2)
    min_channel = np.min(rgb, axis=2)
    chroma = (max_channel - min_channel) * 255.0
    neutral_mask = chroma <= neutral_threshold

    luminance = (
        0.2126 * rgb[..., 0]
        + 0.7152 * rgb[..., 1]
        + 0.0722 * rgb[..., 2]
    )

    bg = np.asarray(background, dtype=np.float32) / 255.0
    fg = np.asarray(foreground, dtype=np.float32) / 255.0

    darkness = np.power(np.clip(luminance, 0.0, 1.0), darkness_curve)
    mapped = bg + (fg - bg) * (1.0 - darkness[..., None])

    result = np.where(neutral_mask[..., None], mapped, rgb)
    result = np.clip(result * 255.0, 0, 255).astype(np.uint8)

    return Image.fromarray(result, mode="RGB")


def encode_page(image, output_format="PNG", quality=90):
    """
    Encode one processed page.

    PNG is lossless and is the default to protect image quality.
    JPEG is smaller but lossy, so image pixels will not remain identical.
    """
    output_format = output_format.upper()
    buffer = io.BytesIO()

    if output_format == "PNG":
        image.save(buffer, format="PNG", optimize=True, compress_level=6)

    elif output_format in ("JPG", "JPEG"):
        image.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
            subsampling=0,
        )

    else:
        raise ValueError("output_format must be PNG or JPEG.")

    return buffer.getvalue()
