"""Rota 2: analisar uma imagem com o YOLO.

Dois endpoints para JSON:
  - POST /analyse/trained  -> usa o modelo TREINADO (icones AWS).
  - POST /analyse/base     -> usa o YOLO11 BASE (COCO), sem treino (baseline).

Dois endpoints para imagem com boxes:
  - POST /analyse/trained/image  -> usa o modelo TREINADO (icones AWS).
  - POST /analyse/base/image     -> usa o YOLO11 BASE (COCO), sem treino (baseline).
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

router = APIRouter(tags=["analise"])

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


@router.post("/analyse/trained")
async def analyse_trained(
    file: UploadFile = File(..., description="Imagem do diagrama de arquitetura."),
    conf: Optional[float] = Query(None, ge=0.0, le=1.0, description="Confianca minima."),
    iou: Optional[float] = Query(None, ge=0.0, le=1.0, description="IoU do NMS."),
):
    """Identifica os servicos AWS usando o modelo treinado e retorna imagem com boxes."""
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


@router.post("/analyse/base")
async def analyse_base(
    file: UploadFile = File(..., description="Imagem para analisar."),
    conf: Optional[float] = Query(None, ge=0.0, le=1.0, description="Confianca minima."),
    iou: Optional[float] = Query(None, ge=0.0, le=1.0, description="IoU do NMS."),
):
    """Analisa com o YOLO11 base (COCO) e retorna imagem com boxes."""
    from app.config import settings
    from app.services import detection
    
    image_bytes = await _read_image(file)
    try:
        model, _ = detection._load_base_model()
        return await _analyse_with_image(model, image_bytes, conf, iou)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Falha na inferencia: {exc}") from exc


@router.post("/analyse/base/json", response_model=DetectResponse)
async def analyse_base_json(
    file: UploadFile = File(..., description="Imagem para analisar."),
    conf: Optional[float] = Query(None, ge=0.0, le=1.0, description="Confianca minima."),
    iou: Optional[float] = Query(None, ge=0.0, le=1.0, description="IoU do NMS."),
) -> DetectResponse:
    """Analisa com o YOLO11 base (COCO), sem treino. Baseline/comparacao.

    Obs.: o modelo base NAO reconhece icones AWS; ele detecta as classes do
    COCO (pessoa, carro, etc.).
    """
    image_bytes = await _read_image(file)
    try:
        return detection.analyse_with_base(image_bytes, conf=conf, iou=iou)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Falha na inferencia: {exc}") from exc
