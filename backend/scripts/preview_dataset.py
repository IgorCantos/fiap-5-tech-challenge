"""Gera algumas imagens sinteticas de exemplo para inspecao visual.

Util para validar se a composicao (icones + fundo tipo diagrama) esta boa
ANTES de rodar um treino completo.

Uso:
    python scripts/preview_dataset.py --n 6 --out preview
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

# Permite rodar o script direto (adiciona a raiz do projeto ao path).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from PIL import ImageDraw, ImageFont

from app.config import settings
from app.services import dataset as ds


def main() -> None:
    parser = argparse.ArgumentParser(description="Previa do dataset sintetico")
    parser.add_argument("--n", type=int, default=6, help="Quantidade de imagens")
    parser.add_argument("--out", type=str, default="preview", help="Pasta de saida")
    parser.add_argument("--boxes", action="store_true", help="Desenha as bounding boxes")
    args = parser.parse_args()

    icons_by_class = ds.discover_icons(settings.icons_dir)
    class_names = list(icons_by_class.keys())
    print(f"Classes encontradas ({len(class_names)}): {class_names}")

    seed = settings.seed if settings.seed is not None else random.randrange(1, 2 ** 31 - 1)
    print(f"Seed: {seed}")
    rng = random.Random(seed)
    random.seed(seed)
    np.random.seed(seed % (2 ** 32))
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    icon_cache: dict = {}

    for i in range(args.n):
        isolated = rng.random() < settings.isolated_ratio
        image, placements = ds._generate_one(
            icons_by_class, class_names, icon_cache, rng, font, isolated=isolated
        )
        if args.boxes:
            draw = ImageDraw.Draw(image)
            for p in placements:
                draw.rectangle([p.x1, p.y1, p.x2, p.y2], outline=(255, 0, 0), width=2)
                draw.text((p.x1, max(0, p.y1 - 14)), class_names[p.class_id],
                          fill=(255, 0, 0), font=font)
        path = out_dir / f"preview_{i:02d}.jpg"
        image.save(path, quality=92)
        print(f"salvo: {path}  ({len(placements)} icones)")


if __name__ == "__main__":
    main()
