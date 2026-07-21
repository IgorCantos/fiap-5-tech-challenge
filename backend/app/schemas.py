"""Modelos Pydantic de entrada/saida das rotas."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class TrainRequest(BaseModel):
    """Parametros opcionais para disparar um treino."""

    epochs: Optional[int] = Field(default=None, ge=1, le=2000)
    batch: Optional[int] = Field(default=None, ge=1, le=256)
    imgsz: Optional[int] = Field(default=None, ge=320, le=2048)
    train_images: Optional[int] = Field(default=None, ge=20)
    val_images: Optional[int] = Field(default=None, ge=5)
    regenerate_dataset: bool = Field(
        default=True,
        description="Se True, regenera o dataset sintetico antes de treinar.",
    )
    device: Optional[str] = Field(
        default=None,
        description="'' (auto), 'cpu', '0', '0,1' ...",
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
