"""Rota 1: treinar o modelo YOLO11."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter

from app.schemas import TrainRequest, TrainResponse, TrainStatus
from app.services import training

router = APIRouter(tags=["treino"])


@router.post("/train", response_model=TrainResponse)
def train(request: Optional[TrainRequest] = None) -> TrainResponse:
    """Dispara o treino em background (gera dataset sintetico e treina)."""
    request = request or TrainRequest()

    if training.get_status().state in {"preparing_dataset", "training"}:
        return TrainResponse(
            accepted=False,
            message="Ja existe um treino em andamento.",
            status=training.get_status(),
        )

    status = training.start_training(request.model_dump(exclude_none=True))
    return TrainResponse(
        accepted=True,
        message="Treino iniciado em background. Consulte GET /train/status.",
        status=status,
    )


@router.get("/train/status", response_model=TrainStatus)
def train_status() -> TrainStatus:
    """Consulta o status do treino atual/anterior."""
    return training.get_status()
