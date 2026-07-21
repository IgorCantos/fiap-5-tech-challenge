
"""Aplicacao FastAPI: deteccao de icones de servicos AWS com YOLO11.

Duas APIs principais:
  - POST /train        -> treina o modelo (gera dataset sintetico + YOLO11)
  - POST /analyse/trained -> identifica servicos AWS (modelo treinado)
  - POST /analyse/base    -> baseline com YOLO11 base (COCO, sem treino)
Auxiliares:
  - GET  /train/status -> status do treino
  - GET  /health       -> saude + disponibilidade do modelo
"""
from __future__ import annotations

from fastapi import FastAPI

from app.config import settings
from app.routes import analyse as analyse_route
from app.routes import train as train_route
from app.services import detection

app = FastAPI(
    title="AWS Icons YOLO11",
    description="Treina e usa um YOLO11 para identificar icones de servicos AWS em diagramas.",
    version="1.0.0",
)

app.include_router(train_route.router)
app.include_router(analyse_route.router)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {
        "status": "ok",
        "model_trained": detection.model_available(),
        "best_weights": str(settings.best_weights_path),
        "icons_dir": str(settings.icons_dir),
    }


@app.get("/", tags=["infra"])
def root() -> dict:
    return {
        "service": "AWS Icons YOLO11",
        "docs": "/docs",
        "endpoints": {
            "treinar": "POST /train",
            "status_treino": "GET /train/status",
            "analisar_treinado": "POST /analyse/trained",
            "analisar_base": "POST /analyse/base",
            "saude": "GET /health",
        },
    }
