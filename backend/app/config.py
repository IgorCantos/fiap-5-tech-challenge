
"""Configuracoes centrais do projeto.

Todos os caminhos sao derivados da raiz do projeto para funcionar
independentemente do diretorio de onde a API for iniciada.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Raiz do projeto (pasta que contem a pasta "app").
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Configuracoes carregaveis via variaveis de ambiente ou arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="YOLO_", extra="ignore")

    # ----- Caminhos -----
    icons_dir: Path = BASE_DIR / "model_training" / "data" / "icons"
    datasets_dir: Path = BASE_DIR / "datasets"
    dataset_name: str = "aws_icons"
    models_dir: Path = BASE_DIR / "models"
    runs_dir: Path = BASE_DIR / "runs"

    # Peso base do YOLO11 usado como ponto de partida do treino.
    base_weights: str = "yolo11n.pt"
    # Nome do arquivo do melhor modelo treinado (usado na inferencia).
    best_weights_name: str = "best.pt"

    # ----- Geracao do dataset sintetico -----
    train_images: int = 5000          # qtd de imagens sinteticas de treino
    val_images: int = 500            # qtd de imagens sinteticas de validacao
    image_size: int = 1024           # lado da imagem sintetica (quadrada)
    min_icons_per_image: int = 5
    max_icons_per_image: int = 14
    min_icon_scale: float = 0.045    # fracao do lado da imagem
    max_icon_scale: float = 0.13
    max_placement_iou: float = 0.35  # sobreposicao maxima permitida entre icones
    # Seed configuravel. None => gera uma seed aleatoria a cada execucao, de modo
    # que duas geracoes consecutivas produzam datasets diferentes.
    seed: Optional[int] = None

    # Icones em ALTA RESOLUCAO: as augmentations sao aplicadas no icone grande e
    # so depois ele e redimensionado para o tamanho final, preservando detalhes.
    hires_icon_size: int = 512
    # Margem transparente aleatoria adicionada ao redor do icone (fracao do lado).
    icon_margin_min: float = 0.05
    icon_margin_max: float = 0.20

    # Layout tipo diagrama: "snap" de grade + jitter para nao ficar perfeito demais.
    snap_grid: int = 16
    # Fracao do dataset composta por icones isolados / grupos pequenos (o resto
    # sao diagramas completos).
    isolated_ratio: float = 0.2

    # Remocao automatica de fundo solido dos icones (util p/ JPG/PNG sem alpha,
    # com o icone centralizado sobre fundo branco/uniforme).
    remove_icon_background: bool = True
    icon_bg_tolerance: int = 32       # tolerancia de cor do flood fill (0-255)

    # Variedade de renderizacao dos icones (aumenta a diversidade do dataset):
    #  - "original": mantem a imagem original, com seu fundo/box (icone opaco)
    #  - "card": icone (fundo removido) sobre um card branco arredondado (tile AWS)
    #  - "black": silhueta totalmente preta do icone (apos remover o fundo)
    #  - "white_on_black": icone em branco sobre um card preto (apos remover o fundo)
    #  - "white": silhueta branca com fino contorno escuro, sem fundo (visivel em qualquer fundo)
    #  - "recolor": muda a cor do icone (hue shift preservando detalhe, ou silhueta colorida)
    #  - restante: fundo removido/transparente (comportamento atual)
    # Evita que icones claros (linha fina) fiquem invisiveis sobre fundo claro.
    icon_original_ratio: float = 0.22
    icon_card_ratio: float = 0.15
    icon_black_ratio: float = 0.10
    icon_white_on_black_ratio: float = 0.10
    icon_white_ratio: float = 0.08
    icon_recolor_ratio: float = 0.12

    # ----- Treino -----
    epochs: int = 1
    batch: int = 16
    train_imgsz: int = 1024
    patience: int = 30
    device: str = "cpu"                 # "" = auto (cpu/gpu), "cpu", "0", "0,1"...

    # ----- Inferencia -----
    conf_threshold: float = 0.35
    iou_threshold: float = 0.5

    @property
    def dataset_dir(self) -> Path:
        return self.datasets_dir / self.dataset_name

    @property
    def data_yaml_path(self) -> Path:
        return self.dataset_dir / "data.yaml"

    @property
    def best_weights_path(self) -> Path:
        return self.models_dir / self.best_weights_name

    @property
    def base_weights_pt_path(self) -> Path:
        """Caminho esperado do peso pre-treinado local (models/yolo11n.pt)."""
        name = Path(self.base_weights).name
        if not name.endswith(".pt"):
            name = f"{Path(name).stem}.pt"
        return self.models_dir / name

    def base_pretrained_path(self) -> Optional[Path]:
        """Retorna o peso pre-treinado local, se existir (caminho abs ou models/)."""
        p = Path(self.base_weights)
        if p.suffix == ".pt" and p.is_file():
            return p
        if self.base_weights_pt_path.is_file():
            return self.base_weights_pt_path
        return None

    def base_arch_yaml(self) -> str:
        """Arquitetura equivalente (offline) para treino do zero, ex.: yolo11n.yaml."""
        stem = Path(self.base_weights).stem or "yolo11n"
        return f"{stem}.yaml"

    def ensure_dirs(self) -> None:
        for path in (self.icons_dir, self.datasets_dir, self.models_dir, self.runs_dir):
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()
