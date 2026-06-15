"""
Image persistence: originals and WebP thumbnails (FR-25, architecture §3.2).

``save_original(data, ext, garment_id, images_dir)``
    Write raw bytes to ``data/images/{garment_id}.{ext}``.

``generate_thumbnail(src_path, thumbnails_dir, garment_id)``
    Derive a WebP thumbnail with longest edge ≤ 320 px using Pillow.

Storage imports nothing from matcher/detection/services/api (contract 4).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

_THUMBNAIL_MAX_PX: int = 320


def save_original(
    data: bytes,
    ext: str,
    garment_id: str,
    images_dir: Path,
) -> str:
    """
    Write *data* to ``images_dir/{garment_id}.{ext}`` and return the filename.

    The original format is preserved as-is (FR-25).
    """
    filename = f"{garment_id}.{ext}"
    (images_dir / filename).write_bytes(data)
    return filename


def generate_thumbnail(
    src_path: Path,
    thumbnails_dir: Path,
    garment_id: str,
) -> str:
    """
    Generate a WebP thumbnail at ``thumbnails_dir/{garment_id}.webp``.

    The longest edge is scaled to at most ``_THUMBNAIL_MAX_PX`` pixels;
    aspect ratio is preserved.  Returns the thumbnail filename.
    """
    with Image.open(src_path) as img:
        img = img.convert("RGBA") if img.mode in ("P", "LA") else img.convert(img.mode)
        img.thumbnail((_THUMBNAIL_MAX_PX, _THUMBNAIL_MAX_PX), Image.LANCZOS)
        out_name = f"{garment_id}.webp"
        img.save(thumbnails_dir / out_name, "WEBP")
    return out_name
