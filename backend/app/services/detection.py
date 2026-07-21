
"""Servico de inferencia.

Suporta dois modos:
  - "trained": usa o modelo customizado treinado (models/best.pt) que reconhece
    os icones de servicos AWS.
  - "base": usa o YOLO11 pre-treinado (COCO). NAO reconhece icones AWS; serve
    como baseline/comparacao. As classes detectadas sao as do COCO.
"""
from __future__ import annotations

import io
from collections import Counter
from threading import Lock
from typing import Optional

from PIL import Image

from app.config import settings
from app.schemas import Detection, DetectResponse

# Cache de modelos: identificador -> {"model": YOLO, "mtime": float | None}
_model_cache: dict = {}
_lock = Lock()


class ModelNotTrainedError(RuntimeError):
    """Levantado quando ainda nao existe um modelo treinado."""


def _get_model(identifier: str, mtime: Optional[float]):
    """Carrega um modelo YOLO com cache. Recarrega se `mtime` mudar."""
    with _lock:
        entry = _model_cache.get(identifier)
        if entry is None or entry["mtime"] != mtime:
            from ultralytics import YOLO

            entry = {"model": YOLO(identifier), "mtime": mtime}
            _model_cache[identifier] = entry
        return entry["model"]


def _load_trained_model():
    weights = settings.best_weights_path
    if not weights.exists():
        raise ModelNotTrainedError(
            "Nenhum modelo treinado encontrado (models/best.pt). "
            "Treine primeiro via POST /train."
        )
    return _get_model(str(weights), weights.stat().st_mtime), weights.name


def _load_base_model():
    # settings.base_weights (ex.: 'yolo11n.pt') e baixado pela ultralytics se
    # ainda nao existir localmente.
    return _get_model(settings.base_weights, None), settings.base_weights


def _run(model, model_label: str, image_bytes: bytes,
         conf: Optional[float], iou: Optional[float]) -> DetectResponse:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    results = model.predict(
        source=image,
        conf=conf if conf is not None else settings.conf_threshold,
        iou=iou if iou is not None else settings.iou_threshold,
        verbose=False,
    )

    detections: list[Detection] = []
    result = results[0]
    names = result.names  # dict {id: nome}

    if result.boxes is not None:
        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())
            x1, y1, x2, y2 = (float(v) for v in box.xyxy[0].tolist())
            detections.append(
                Detection(
                    service=names.get(cls_id, str(cls_id)),
                    confidence=round(confidence, 4),
                    box_xyxy=[round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                )
            )

    summary = dict(Counter(d.service for d in detections))

    return DetectResponse(
        model_used=model_label,
        image_width=width,
        image_height=height,
        count=len(detections),
        detections=detections,
        services_summary=summary,
    )


def analyse_with_trained(
    image_bytes: bytes,
    conf: Optional[float] = None,
    iou: Optional[float] = None,
) -> DetectResponse:
    """Analisa a imagem com o modelo TREINADO (reconhece icones AWS)."""
    model, label = _load_trained_model()
    return _run(model, label, image_bytes, conf, iou)


def analyse_with_base(
    image_bytes: bytes,
    conf: Optional[float] = None,
    iou: Optional[float] = None,
) -> DetectResponse:
    """Analisa a imagem com o YOLO11 BASE (COCO). Baseline sem treino."""
    model, label = _load_base_model()
    return _run(model, label, image_bytes, conf, iou)


def model_available() -> bool:
    return settings.best_weights_path.exists()
