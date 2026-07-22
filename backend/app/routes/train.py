"""Rota 1: treinar o modelo YOLO11."""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas import TrainRequest, TrainResponse, TrainStatus
from app.services import training
from app.config import settings

router = APIRouter(tags=["training"])


@router.post("/model/yolo11/train/start", response_model=TrainResponse)
def start_training(request: TrainRequest = None) -> TrainResponse:
    """Start YOLO11 model training in background (uses config.py values)."""
    if training.get_status().state in {"preparing_dataset", "training"}:
        return TrainResponse(
            accepted=False,
            message="Ja existe um treino em andamento.",
            status=training.get_status(),
        )

    params = {
        "epochs": settings.epochs,
        "batch": settings.batch,
        "imgsz": settings.train_imgsz,
        "train_images": settings.train_images,
        "val_images": settings.val_images,
        "regenerate_dataset": True,
        "device": settings.device,
        "use_old_trained_model": request.use_old_trained_model if request else False,
    }
    status = training.start_training(params)
    return TrainResponse(
        accepted=True,
        message="Treino iniciado em background. Consulte GET /model/yolo11/train/status.",
        status=status,
    )


@router.get("/model/yolo11/train/status", response_model=TrainStatus)
def get_training_status() -> TrainStatus:
    """Get YOLO11 training status."""
    return training.get_status()
