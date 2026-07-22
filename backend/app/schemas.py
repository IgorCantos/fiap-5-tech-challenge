"""Modelos Pydantic de entrada/saida das rotas."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    """Parametros para disparar um treino."""

    use_old_trained_model: bool = Field(
        default=False,
        description="Se True, treina em cima do modelo atual (best.pt) em vez do modelo base.",
    )


class TrainStatus(BaseModel):
    state: str  # idle | preparing_dataset | training | completed | failed
    message: str = ""
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    epochs: Optional[int] = None
    classes: List[str] = []
    best_weights: Optional[str] = None
    metrics: Optional[dict] = None
    error: Optional[str] = None


class TrainResponse(BaseModel):
    accepted: bool
    message: str
    status: TrainStatus


class Detection(BaseModel):
    service: str
    confidence: float
    box_xyxy: List[float]  # [x1, y1, x2, y2] em pixels


class DetectResponse(BaseModel):
    model_used: str
    image_width: int
    image_height: int
    count: int
    detections: List[Detection]
    services_summary: dict  # {classe: quantidade}
