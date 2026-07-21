"""Route 3: preview synthetic dataset generation.

Generates sample synthetic images to visualize the dataset before training.
"""
from __future__ import annotations

import io
import random
import zipfile
from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.config import settings
from app.services import dataset as ds
from app.services import layout_engine as le
from PIL import ImageFont

router = APIRouter(tags=["preview"])


def _generate_preview_images(n: int, boxes: bool) -> bytes:
    """Generate n preview images and return as zip file."""
    icons_by_class = ds.discover_icons(settings.icons_dir)
    class_names = list(icons_by_class.keys())
    
    seed = settings.seed if settings.seed is not None else random.randrange(1, 2 ** 31 - 1)
    rng = random.Random(seed)
    random.seed(seed)
    
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
    
    icon_cache: dict = {}
    balancer = le.ClassBalancer(class_names)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for i in range(n):
            isolated = rng.random() < settings.isolated_ratio
            image, placements = ds._generate_one(
                icons_by_class, class_names, icon_cache, rng, font,
                isolated=isolated, balancer=balancer,
            )
            
            if boxes:
                draw = ds.ImageDraw.Draw(image)
                for p in placements:
                    draw.rectangle([p.x1, p.y1, p.x2, p.y2], outline=(255, 0, 0), width=2)
                    draw.text((p.x1, max(0, p.y1 - 14)), class_names[p.class_id],
                              fill=(255, 0, 0), font=font)
            
            img_buffer = io.BytesIO()
            image.save(img_buffer, format="JPEG", quality=90)
            img_buffer.seek(0)
            zip_file.writestr(f"preview_{i:02d}.jpg", img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


@router.get("/model/yolo11/dataset/preview")
async def preview_dataset(
    n: int = Query(5, ge=1, le=20, description="Number of preview images to generate."),
    boxes: bool = Query(False, description="Draw bounding boxes on images."),
):
    """Generate synthetic dataset preview images and return as zip file."""
    try:
        zip_data = _generate_preview_images(n, boxes)
        return StreamingResponse(
            io.BytesIO(zip_data),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=dataset_preview.zip"}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate preview: {exc}") from exc
