"""Route 2: analyze images with YOLO11.

Two endpoints:
  - POST /model/yolo11/trained  -> uses TRAINED model (AWS icons).
  - POST /model/yolo11/base     -> uses YOLO11 BASE (COCO), no training (baseline).

Both return annotated image with bounding boxes.
"""
from __future__ import annotations

import io
import cv2
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas import DetectResponse
from app.services import detection
from app.config import settings

router = APIRouter(tags=["analysis"])

_ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp"}


async def _read_image(file: UploadFile) -> bytes:
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de arquivo nao suportado: {file.content_type}",
        )
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    return image_bytes


async def _analyse_with_image(model, image_bytes: bytes, conf: Optional[float], iou: Optional[float]):
    """Analisa imagem e retorna imagem com boxes desenhados."""
    from PIL import Image
    
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    results = model.predict(
        source=image,
        conf=conf if conf is not None else settings.conf_threshold,
        iou=iou if iou is not None else settings.iou_threshold,
        verbose=False,
    )
    
    # 1. O annotated_frame vem do YOLO no formato BGR
    annotated_frame = results[0].plot()
    
    # 2. Converte de BGR para RGB antes de mandar para o PIL
    annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    
    # 3. Cria a imagem PIL com as cores corretas (RGB)
    annotated_image = Image.fromarray(annotated_frame_rgb)
    
    # 4. Guarda no buffer de memória
    img_byte_arr = io.BytesIO()
    annotated_image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)
    
    return StreamingResponse(img_byte_arr, media_type="image/png")


@router.post("/model/yolo11/trained")
async def analyse_with_trained_model(
    file: UploadFile = File(..., description="Architecture diagram image."),
    conf: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence threshold."),
    iou: Optional[float] = Query(None, ge=0.0, le=1.0, description="IoU threshold for NMS."),
):
    """Detect AWS services using trained YOLO11 model and return annotated image with bounding boxes."""
    from app.config import settings
    from app.services import detection
    
    image_bytes = await _read_image(file)
    try:
        model, _ = detection._load_trained_model()
        return await _analyse_with_image(model, image_bytes, conf, iou)
    except detection.ModelNotTrainedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Falha na inferencia: {exc}") from exc


@router.post("/model/yolo11/base")
async def analyse_with_base_model(
    file: UploadFile = File(..., description="Image to analyze."),
    conf: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence threshold."),
    iou: Optional[float] = Query(None, ge=0.0, le=1.0, description="IoU threshold for NMS."),
):
    """Analyze with YOLO11 base (COCO) and return annotated image with bounding boxes."""
    from app.config import settings
    from app.services import detection
    
    image_bytes = await _read_image(file)
    try:
        model, _ = detection._load_base_model()
        return await _analyse_with_image(model, image_bytes, conf, iou)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Falha na inferencia: {exc}") from exc
