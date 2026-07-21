
"""Servico de treino do YOLO11.

Roda o treino em uma thread de background e mantem um status consultavel.
Fluxo: gera dataset sintetico -> treina YOLO11 -> copia melhor peso para
`models/best.pt` (usado na inferencia).
"""
from __future__ import annotations

import shutil
import threading
from datetime import datetime, timezone
from typing import Optional

from app.config import settings
from app.schemas import TrainStatus
from app.services import dataset as dataset_service


class _TrainingState:
    """Estado compartilhado do job de treino (thread-safe)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._status = TrainStatus(state="idle", message="Nenhum treino executado ainda.")
        self._thread: Optional[threading.Thread] = None

    def snapshot(self) -> TrainStatus:
        with self._lock:
            return self._status.model_copy(deep=True)

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def update(self, **kwargs) -> None:
        with self._lock:
            data = self._status.model_dump()
            data.update(kwargs)
            self._status = TrainStatus(**data)

    def set_thread(self, thread: threading.Thread) -> None:
        self._thread = thread


state = _TrainingState()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_training(params: dict) -> None:
    try:
        state.update(
            state="preparing_dataset",
            message="Gerando dataset sintetico a partir dos icones...",
            started_at=_now(),
            finished_at=None,
            error=None,
            metrics=None,
        )

        if params.get("regenerate_dataset", True) or not settings.data_yaml_path.exists():
            def _progress(split, done, total):
                state.update(message=f"Gerando dataset ({split}): {done}/{total} imagens")

            data_yaml, class_names = dataset_service.generate_dataset(
                train_images=params.get("train_images"),
                val_images=params.get("val_images"),
                on_progress=_progress,
            )
        else:
            import yaml
            data_yaml = settings.data_yaml_path
            class_names = yaml.safe_load(data_yaml.read_text(encoding="utf-8")).get("names", [])

        state.update(
            state="training",
            message="Treinando YOLO11...",
            classes=class_names,
        )

        # Importa aqui para nao pagar o custo de carregar torch no import da API.
        from ultralytics import YOLO

        epochs = params.get("epochs") or settings.epochs
        batch = params.get("batch") or settings.batch
        imgsz = params.get("imgsz") or settings.train_imgsz
        device = params.get("device")
        if device is None:
            device = settings.device

        model = YOLO(settings.base_weights)
        results = model.train(
            data=str(data_yaml),
            epochs=epochs,
            batch=batch,
            imgsz=imgsz,
            patience=settings.patience,
            device=device or None,
            project=str(settings.runs_dir),
            name="aws_icons",
            exist_ok=True,
            verbose=True,
        )

        # Localiza e copia o melhor peso.
        best = getattr(getattr(results, "save_dir", None), "__str__", lambda: "")()
        run_dir = settings.runs_dir / "aws_icons"
        best_src = run_dir / "weights" / "best.pt"
        if not best_src.exists():
            # fallback: procura o best.pt mais recente em runs/
            candidates = sorted(
                settings.runs_dir.glob("**/weights/best.pt"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            best_src = candidates[0] if candidates else None

        metrics = None
        try:
            if getattr(results, "results_dict", None):
                metrics = {k: float(v) for k, v in results.results_dict.items()}
        except Exception:  # noqa: BLE001
            metrics = None

        if best_src and best_src.exists():
            settings.models_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(best_src, settings.best_weights_path)
            state.update(
                state="completed",
                message="Treino concluido. Modelo salvo em models/best.pt.",
                finished_at=_now(),
                epochs=epochs,
                best_weights=str(settings.best_weights_path),
                metrics=metrics,
            )
        else:
            state.update(
                state="failed",
                message="Treino finalizou mas o peso 'best.pt' nao foi encontrado.",
                finished_at=_now(),
                error="best.pt nao encontrado",
            )

    except Exception as exc:  # noqa: BLE001
        state.update(
            state="failed",
            message="Falha durante o treino.",
            finished_at=_now(),
            error=f"{type(exc).__name__}: {exc}",
        )


def start_training(params: dict) -> TrainStatus:
    """Dispara o treino em background. Retorna o status atual."""
    if state.is_running():
        return state.snapshot()

    thread = threading.Thread(target=_run_training, args=(params,), daemon=True)
    state.set_thread(thread)
    thread.start()
    return state.snapshot()


def get_status() -> TrainStatus:
    return state.snapshot()
