
"""Geracao de dataset sintetico para deteccao de icones AWS com YOLO11.

Ideia central
-------------
Treinar o YOLO apenas com os PNGs "puros" dos icones nao funciona: o modelo
nunca ve o icone dentro de um contexto (fundo, linhas, caixas, sobreposicao,
escalas diferentes) e nao aprende a localiza-lo em um diagrama real.

Aqui geramos automaticamente centenas de "diagramas sinteticos": colamos os
icones em posicoes/escalas/fundos aleatorios, adicionamos ruido visual que
imita diagramas de arquitetura (caixas de agrupamento, linhas de conexao,
setas, textos) e produzimos os rotulos no formato YOLO (uma linha por icone:
`class_id x_center y_center width height`, todos normalizados de 0 a 1).

Basta o usuario colocar os PNGs em `icons/` (um arquivo por servico, ou uma
subpasta por servico) e o dataset e construido sem anotacao manual.
"""
from __future__ import annotations

import io
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from app.config import settings
from app.services import layout_engine as le
from app.services.layout_engine import DiagramSpec

SUPPORTED_EXT = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".gif", ".svg"}


@dataclass
class Placement:
    x1: int
    y1: int
    x2: int
    y2: int
    class_id: int

    def iou(self, other: "Placement") -> float:
        ix1, iy1 = max(self.x1, other.x1), max(self.y1, other.y1)
        ix2, iy2 = min(self.x2, other.x2), min(self.y2, other.y2)
        iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
        inter = iw * ih
        if inter == 0:
            return 0.0
        area_a = (self.x2 - self.x1) * (self.y2 - self.y1)
        area_b = (other.x2 - other.x1) * (other.y2 - other.y1)
        return inter / float(area_a + area_b - inter)


# --------------------------------------------------------------------------- #
# Descoberta e carregamento dos icones
# --------------------------------------------------------------------------- #
def _sanitize_class_name(name: str) -> str:
    return name.strip().lower().replace(" ", "-").replace("_", "-")


def discover_icons(icons_dir: Path) -> Dict[str, List[Path]]:
    """Mapeia nome_da_classe -> lista de arquivos de icone.

    Suporta dois layouts:
      1. Arquivos soltos:  icons/s3.png            -> classe "s3"
      2. Subpastas:        icons/s3/qualquer.png   -> classe "s3"
    """
    if not icons_dir.exists():
        raise FileNotFoundError(f"Pasta de icones nao encontrada: {icons_dir}")

    classes: Dict[str, List[Path]] = {}

    for entry in sorted(icons_dir.iterdir()):
        if entry.is_dir():
            files = [p for p in sorted(entry.iterdir()) if p.suffix.lower() in SUPPORTED_EXT]
            if files:
                classes.setdefault(_sanitize_class_name(entry.name), []).extend(files)
        elif entry.suffix.lower() in SUPPORTED_EXT:
            classes.setdefault(_sanitize_class_name(entry.stem), []).append(entry)

    if not classes:
        raise ValueError(
            f"Nenhum icone encontrado em {icons_dir}. "
            "Coloque arquivos PNG (um por servico) ou subpastas por servico."
        )
    return dict(sorted(classes.items()))


def _has_transparency(img: Image.Image) -> bool:
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        return alpha.getextrema()[0] < 255
    return img.mode == "P" and "transparency" in img.info


def _remove_solid_background(img: Image.Image, tolerance: int) -> Image.Image:
    """Torna transparente o fundo solido/uniforme de um icone centralizado.

    Estima a cor de fundo pelas bordas da imagem e usa flood fill a partir dos
    cantos/bordas, de modo que so o fundo CONECTADO as bordas vira transparente
    (o interior do icone e preservado, mesmo que contenha branco).
    """
    rgb = img.convert("RGB")
    w, h = rgb.size
    arr = np.asarray(rgb)

    border = np.concatenate(
        [arr[0], arr[-1], arr[:, 0], arr[:, -1]], axis=0
    ).astype(np.float32)
    bg = np.median(border, axis=0)

    # Se a borda nao for uniforme, provavelmente nao ha fundo solido a remover.
    if float(np.sqrt(((border - bg) ** 2).sum(axis=1)).mean()) > 45.0:
        return img.convert("RGBA")

    work = rgb.copy()
    sentinel = (0, 255, 1)  # cor improvavel usada como marcador
    seeds = [
        (0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
        (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2),
    ]
    for seed in seeds:
        try:
            ImageDraw.floodfill(work, seed, sentinel, thresh=float(tolerance))
        except Exception:  # noqa: BLE001
            continue

    marked = np.all(np.asarray(work) == np.array(sentinel), axis=-1)
    alpha = np.where(marked, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr, alpha])
    return Image.fromarray(rgba, "RGBA")


def _is_svg(path: Path) -> bool:
    """Detecta SVG por conteudo (a extensao pode estar errada, ex.: .jpg)."""
    if path.suffix.lower() == ".svg":
        return True
    try:
        with open(path, "rb") as fh:
            head = fh.read(1024).lstrip().lower()
        return b"<svg" in head
    except OSError:
        return False


def _rasterize_svg(path: Path) -> Image.Image:
    """Rasteriza um SVG para RGB (fundo branco) usando svglib + reportlab."""
    try:
        from reportlab.graphics import renderPM
        from svglib.svglib import svg2rlg
    except ImportError as exc:  # noqa: BLE001
        raise RuntimeError(
            "Icone SVG encontrado, mas 'svglib' nao esta instalado. "
            "Rode: pip install svglib"
        ) from exc

    drawing = svg2rlg(str(path))
    if drawing is None:
        raise ValueError(f"Nao foi possivel interpretar o SVG: {path}")

    # Escala para uma resolucao boa (icones pequenos ficam nitidos ao compor).
    target = 384.0
    longest = max(drawing.width or target, drawing.height or target)
    scale = max(1.0, target / longest)
    drawing.scale(scale, scale)
    drawing.width = (drawing.width or target) * scale
    drawing.height = (drawing.height or target) * scale

    pil = renderPM.drawToPIL(drawing, dpi=72, bg=0xFFFFFF)
    return pil.convert("RGB")


def _to_hires(img: Image.Image, crop: bool) -> Image.Image:
    """Normaliza um RGBA para alta-res (maior lado == hires) + margem transparente."""
    img = img.convert("RGBA")
    if crop:
        bbox = img.split()[-1].getbbox()
        if bbox:
            img = img.crop(bbox)

    target = max(1, settings.hires_icon_size)
    w, h = img.size
    scale = target / max(w, h)
    if abs(scale - 1.0) > 1e-3:
        img = img.resize((max(1, int(round(w * scale))), max(1, int(round(h * scale)))),
                         Image.LANCZOS)

    margin_frac = random.uniform(settings.icon_margin_min, settings.icon_margin_max)
    pad = int(max(img.size) * margin_frac)
    if pad > 0:
        img = ImageOps.expand(img, border=pad, fill=(0, 0, 0, 0))
    return img


def _load_icon_variants(path: Path) -> Dict[str, Image.Image]:
    """Carrega o icone em ALTA RESOLUCAO em duas variantes cacheadas:

      - "transparent": fundo solido removido (recortado ao conteudo real);
      - "original": imagem original preservada (com seu fundo/box, icone opaco).

    A partir delas o pipeline sorteia, por colagem, entre transparente / original
    / card branco (ver `_finalize_icon`), garantindo variedade e evitando que
    icones claros de linha fina fiquem invisiveis sobre fundos claros.

    Suporta PNG/JPEG/WebP/BMP/GIF (detectando pelo conteudo) e SVG (svglib).
    """
    if _is_svg(path):
        raw_rgb = _rasterize_svg(path)  # RGB com fundo branco
        original = raw_rgb.convert("RGBA")
        transparent = _remove_solid_background(raw_rgb, settings.icon_bg_tolerance)
    else:
        raw = Image.open(path)
        original = raw.convert("RGBA")
        if settings.remove_icon_background and not _has_transparency(raw):
            transparent = _remove_solid_background(raw, settings.icon_bg_tolerance)
        else:
            transparent = raw.convert("RGBA")

    return {
        "transparent": _to_hires(transparent, crop=True),
        "original": _to_hires(original, crop=True),
    }


def _make_card(icon_transp: Image.Image, rng: random.Random) -> Image.Image:
    """Compoe o icone transparente sobre um card branco arredondado (tile AWS)."""
    w, h = icon_transp.size
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    pad = int(min(w, h) * rng.uniform(0.03, 0.08))
    radius = int(min(w, h) * rng.uniform(0.08, 0.16))
    draw.rounded_rectangle(
        [pad, pad, w - pad, h - pad], radius=radius,
        fill=(255, 255, 255, 255),
        outline=(208, 213, 221, 255), width=max(2, int(min(w, h) * 0.012)),
    )
    card.alpha_composite(icon_transp)
    return card


def _silhouette(icon_transp: Image.Image, color: Tuple[int, int, int]) -> Image.Image:
    """Recolore o icone (mantendo o formato/alpha) com uma cor solida."""
    alpha = icon_transp.split()[-1]
    out = Image.new("RGBA", icon_transp.size, color + (0,))
    out.putalpha(alpha)
    return out


def _make_black_on_white_removed(icon_transp: Image.Image) -> Image.Image:
    """Silhueta totalmente PRETA do icone (fundo transparente)."""
    return _silhouette(icon_transp, (0, 0, 0))


def _make_white_on_black(icon_transp: Image.Image, rng: random.Random) -> Image.Image:
    """Icone em BRANCO sobre um card PRETO arredondado (apos remover o fundo)."""
    w, h = icon_transp.size
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    pad = int(min(w, h) * rng.uniform(0.03, 0.08))
    radius = int(min(w, h) * rng.uniform(0.08, 0.16))
    draw.rounded_rectangle(
        [pad, pad, w - pad, h - pad], radius=radius, fill=(0, 0, 0, 255),
    )
    card.alpha_composite(_silhouette(icon_transp, (255, 255, 255)))
    return card


def _make_white_outline(icon_transp: Image.Image, rng: random.Random) -> Image.Image:
    """Silhueta BRANCA com fino contorno escuro, sem fundo.

    O contorno (silhueta dilatada, escura) garante que o icone branco seja
    visivel sobre qualquer fundo (claro ou escuro).
    """
    alpha = icon_transp.split()[-1]
    k = rng.choice([3, 5])
    dilated = alpha.filter(ImageFilter.MaxFilter(k))
    outline = Image.new("RGBA", icon_transp.size, (35, 35, 40, 0))
    outline.putalpha(dilated)
    outline.alpha_composite(_silhouette(icon_transp, (255, 255, 255)))
    return outline


def _make_recolor(icon_transp: Image.Image, rng: random.Random) -> Image.Image:
    """Muda a cor do icone: hue shift (preserva detalhe) ou silhueta colorida."""
    if rng.random() < 0.55:
        # rotacao de matiz preservando forma/detalhe interno
        r, g, b, a = icon_transp.split()
        hsv = Image.merge("RGB", (r, g, b)).convert("HSV")
        h, s, v = hsv.split()
        shift = rng.randint(20, 235)
        h = h.point(lambda p: (p + shift) % 256)
        rgb2 = Image.merge("HSV", (h, s, v)).convert("RGB")
        r2, g2, b2 = rgb2.split()
        return Image.merge("RGBA", (r2, g2, b2, a))
    # silhueta de cor solida (escura o suficiente p/ visibilidade em fundo claro)
    color = tuple(rng.randint(20, 150) for _ in range(3))
    return _silhouette(icon_transp, color)


def _pick_variant(rng: random.Random) -> str:
    r = rng.random()
    acc = settings.icon_original_ratio
    if r < acc:
        return "original"
    acc += settings.icon_card_ratio
    if r < acc:
        return "card"
    acc += settings.icon_black_ratio
    if r < acc:
        return "black"
    acc += settings.icon_white_on_black_ratio
    if r < acc:
        return "white_on_black"
    acc += settings.icon_white_ratio
    if r < acc:
        return "white"
    acc += settings.icon_recolor_ratio
    if r < acc:
        return "recolor"
    return "transparent"


# --------------------------------------------------------------------------- #
# Fundos estilo ferramentas de diagrama (Draw.io, Lucid, Miro, PowerPoint...)
# --------------------------------------------------------------------------- #
_BG_BASE = {
    "white": (255, 255, 255),
    "grid": (255, 255, 255),
    "gray": (245, 246, 248),
    "drawio": (255, 255, 255),
    "lucid": (250, 250, 252),
    "miro": (247, 245, 240),
    "ppt": (252, 252, 252),
}


def _render_background(size: int, style: str, rng: random.Random) -> Image.Image:
    """Fundo discreto conforme o estilo escolhido pelo layout engine."""
    base = _BG_BASE.get(style, (255, 255, 255))
    bg = Image.new("RGB", (size, size), base)
    draw = ImageDraw.Draw(bg)

    if style in ("grid", "drawio"):
        step = rng.choice([24, 28, 32, 40])
        color = (232, 234, 238) if style == "drawio" else (236, 238, 241)
        for x in range(0, size, step):
            draw.line([(x, 0), (x, size)], fill=color, width=1)
        for y in range(0, size, step):
            draw.line([(0, y), (size, y)], fill=color, width=1)
    elif style in ("lucid", "miro"):
        step = rng.choice([26, 32, 40])
        color = (236, 238, 242) if style == "lucid" else (232, 228, 220)
        for x in range(0, size, step):
            for y in range(0, size, step):
                draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=color)
    return bg


# --------------------------------------------------------------------------- #
# Estilo visual dos containers AWS (borda, preenchimento suave)
# --------------------------------------------------------------------------- #
_BOX_STYLE = {
    "aws-cloud": ((60, 110, 160), (247, 251, 255)),
    "account": ((90, 110, 140), (248, 250, 253)),
    "region": ((70, 130, 180), (247, 251, 255)),
    "vpc": ((90, 150, 90), (247, 253, 247)),
    "az": ((120, 150, 120), (250, 253, 250)),
    "public-subnet": ((70, 140, 90), (244, 252, 246)),
    "private-subnet": ((70, 110, 170), (244, 248, 253)),
    "security-group": ((190, 120, 70), (253, 249, 244)),
    "generic": ((150, 150, 160), (250, 250, 252)),
}


def _draw_boxes(canvas: Image.Image, spec: DiagramSpec,
                font: ImageFont.ImageFont) -> None:
    draw = ImageDraw.Draw(canvas, "RGBA")
    for box in sorted(spec.boxes, key=lambda b: b.depth):
        border, fill = _BOX_STYLE.get(box.kind, _BOX_STYLE["generic"])
        draw.rounded_rectangle(
            [box.x1, box.y1, box.x2, box.y2], radius=14,
            outline=border + (230,), width=2, fill=fill + (90,),
        )
        if box.label:
            draw.text((box.x1 + 8, box.y1 + 5), box.label, fill=border, font=font)


# --------------------------------------------------------------------------- #
# Conexoes ortogonais entre icones (rota calculada no layout_engine)
# --------------------------------------------------------------------------- #
def _dashed_line(draw, x1, y1, x2, y2, color, width, dash=9, gap=6):
    length = math.hypot(x2 - x1, y2 - y1)
    if length == 0:
        return
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    pos = 0.0
    while pos < length:
        a, b = pos, min(length, pos + dash)
        draw.line([(x1 + ux * a, y1 + uy * a), (x1 + ux * b, y1 + uy * b)],
                  fill=color, width=width)
        pos += dash + gap


def _draw_arrow(draw, p_from, p_to, color, width):
    x1, y1 = p_from
    x2, y2 = p_to
    ang = math.atan2(y2 - y1, x2 - x1)
    length = 8 + width * 2
    for da in (math.radians(152), math.radians(-152)):
        ax = x2 + length * math.cos(ang + da)
        ay = y2 + length * math.sin(ang + da)
        draw.line([(x2, y2), (ax, ay)], fill=color, width=width)


def _draw_connections(canvas: Image.Image, spec: DiagramSpec,
                      rects: List[Optional[Tuple[float, float, float, float]]],
                      rng: random.Random) -> None:
    draw = ImageDraw.Draw(canvas, "RGBA")
    for conn in spec.connections:
        if conn.a >= len(rects) or conn.b >= len(rects):
            continue
        ra, rb = rects[conn.a], rects[conn.b]
        if ra is None or rb is None:
            continue
        pts = le.route_orthogonal(ra, rb, rng)
        color = tuple(conn.color) + (235,)
        for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
            if conn.dashed:
                _dashed_line(draw, x1, y1, x2, y2, color, conn.width)
            else:
                draw.line([(x1, y1), (x2, y2)], fill=color, width=conn.width)
        if conn.arrow and len(pts) >= 2:
            _draw_arrow(draw, pts[-2], pts[-1], color, conn.width)


# --------------------------------------------------------------------------- #
# Augmentations em ALTA RESOLUCAO (aplicadas antes do resize final)
# --------------------------------------------------------------------------- #
def _find_coeffs(pa, pb):
    """Coeficientes de perspectiva mapeando os cantos `pa` (saida) -> `pb` (fonte)."""
    matrix = []
    for (px, py), (qx, qy) in zip(pa, pb):
        matrix.append([px, py, 1, 0, 0, 0, -qx * px, -qx * py])
        matrix.append([0, 0, 0, px, py, 1, -qy * px, -qy * py])
    A = np.array(matrix, dtype=np.float64)
    B = np.array(pb, dtype=np.float64).reshape(8)
    res = np.linalg.solve(A, B)
    return res.tolist()


def _perspective(img: Image.Image, rng: random.Random, max_warp: float) -> Image.Image:
    w, h = img.size
    dx, dy = w * max_warp, h * max_warp
    pa = [(0, 0), (w, 0), (w, h), (0, h)]
    pb = [
        (rng.uniform(0, dx), rng.uniform(0, dy)),
        (w - rng.uniform(0, dx), rng.uniform(0, dy)),
        (w - rng.uniform(0, dx), h - rng.uniform(0, dy)),
        (rng.uniform(0, dx), h - rng.uniform(0, dy)),
    ]
    coeffs = _find_coeffs(pa, pb)
    return img.transform((w, h), Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC)


def _motion_blur(img: Image.Image, rng: random.Random) -> Image.Image:
    n = rng.choice([3, 5, 7])
    axis = 1 if rng.random() < 0.5 else 0
    arr = np.asarray(img).astype(np.float32)
    acc = np.zeros_like(arr)
    for i in range(n):
        acc += np.roll(arr, i - n // 2, axis=axis)
    acc /= n
    return Image.fromarray(np.clip(acc, 0, 255).astype(np.uint8), "RGBA")


def _gaussian_noise(img: Image.Image, rng: random.Random) -> Image.Image:
    arr = np.asarray(img).astype(np.int16)
    sigma = rng.uniform(4, 14)
    noise = np.random.normal(0, sigma, arr[..., :3].shape)
    arr[..., :3] = np.clip(arr[..., :3] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def _jpeg_compress(img: Image.Image, rng: random.Random) -> Image.Image:
    """Compressao JPEG preservando o canal alpha (simula exportacoes)."""
    r, g, b, a = img.split()
    buf = io.BytesIO()
    Image.merge("RGB", (r, g, b)).save(buf, format="JPEG", quality=rng.randint(35, 85))
    buf.seek(0)
    rr, gg, bb = Image.open(buf).convert("RGB").split()
    return Image.merge("RGBA", (rr, gg, bb, a))


def _res_jitter(img: Image.Image, rng: random.Random) -> Image.Image:
    w, h = img.size
    f = rng.uniform(0.5, 0.85)
    small = img.resize((max(1, int(w * f)), max(1, int(h * f))), Image.BILINEAR)
    return small.resize((w, h), Image.BILINEAR)


def _augment_hires(icon: Image.Image, rng: random.Random) -> Image.Image:
    """Aplica um conjunto amplo de augmentations no icone em ALTA RESOLUCAO.

    Todas mantem o icone perfeitamente identificavel. O resize final e feito
    depois, pelo chamador.
    """
    img = icon
    # geometricas leves
    if rng.random() < 0.30:
        img = img.rotate(rng.uniform(-7, 7), expand=True, resample=Image.BICUBIC)
    if rng.random() < 0.22:
        img = _perspective(img, rng, max_warp=rng.uniform(0.02, 0.06))
    # cor
    if rng.random() < 0.60:
        img = ImageEnhance.Brightness(img).enhance(rng.uniform(0.82, 1.18))
    if rng.random() < 0.50:
        img = ImageEnhance.Contrast(img).enhance(rng.uniform(0.85, 1.20))
    if rng.random() < 0.35:
        img = ImageEnhance.Color(img).enhance(rng.uniform(0.70, 1.30))
    # nitidez / desfoque (exclusivos)
    roll = rng.random()
    if roll < 0.18:
        img = img.filter(ImageFilter.GaussianBlur(rng.uniform(0.4, 1.4)))
    elif roll < 0.30:
        img = _motion_blur(img, rng)
    elif roll < 0.42:
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=rng.randint(80, 160)))
    # resolucao / compressao / ruido
    if rng.random() < 0.25:
        img = _res_jitter(img, rng)
    if rng.random() < 0.30:
        img = _jpeg_compress(img, rng)
    if rng.random() < 0.25:
        img = _gaussian_noise(img, rng)
    # opacidade leve
    if rng.random() < 0.12:
        r, g, b, a = img.split()
        a = a.point(lambda v: int(v * rng.uniform(0.80, 1.0)))
        img = Image.merge("RGBA", (r, g, b, a))
    return img


def _finalize_icon(variants: Dict[str, Image.Image], target: int,
                   rng: random.Random) -> Image.Image:
    """Sorteia a variante (transparent/original/card/black/white_on_black/
    white/recolor), augmenta em alta-res e reduz para o tamanho final."""
    variant = _pick_variant(rng)
    if variant == "original":
        base = variants["original"]
    elif variant == "card":
        base = _make_card(variants["transparent"], rng)
    elif variant == "black":
        base = _make_black_on_white_removed(variants["transparent"])
    elif variant == "white_on_black":
        base = _make_white_on_black(variants["transparent"], rng)
    elif variant == "white":
        base = _make_white_outline(variants["transparent"], rng)
    elif variant == "recolor":
        base = _make_recolor(variants["transparent"], rng)
    else:
        base = variants["transparent"]

    aug = _augment_hires(base, rng)
    w, h = aug.size
    scale = target / max(w, h)
    nw, nh = max(1, int(round(w * scale))), max(1, int(round(h * scale)))
    return aug.resize((nw, nh), Image.LANCZOS)


def _draw_service_label(draw: ImageDraw.ImageDraw, rect, text: str,
                        rng: random.Random, font: ImageFont.ImageFont) -> None:
    """Escreve o nome do servico proximo ao icone (acima/abaixo/lateral)."""
    x1, y1, x2, y2 = rect
    color = tuple(rng.randint(40, 110) for _ in range(3))
    place = rng.random()
    if place < 0.6:
        pos = (x1, y2 + 2)                      # abaixo
    elif place < 0.85:
        pos = (x1, max(0, y1 - 15))             # acima
    else:
        pos = (x2 + 3, y1 + (y2 - y1) / 2 - 7)  # lateral
    draw.text(pos, text, fill=color, font=font)


def _nn_distances(centers: List[Tuple[float, float]]) -> List[Optional[float]]:
    """Distancia ao vizinho mais proximo (para limitar o tamanho e evitar overlap)."""
    n = len(centers)
    res: List[Optional[float]] = [None] * n
    for i in range(n):
        best = None
        for j in range(n):
            if i == j:
                continue
            d = math.hypot(centers[i][0] - centers[j][0], centers[i][1] - centers[j][1])
            if best is None or d < best:
                best = d
        res[i] = best
    return res


def _global_finish(img: Image.Image, rng: random.Random) -> Image.Image:
    """Pequenas degradacoes globais (simula export do diagrama inteiro)."""
    if rng.random() < 0.15:
        img = img.filter(ImageFilter.GaussianBlur(rng.uniform(0.3, 0.8)))
    if rng.random() < 0.20:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=rng.randint(45, 88))
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
    if rng.random() < 0.15:
        arr = np.asarray(img).astype(np.int16)
        noise = rng.randint(3, 9)
        arr += np.random.randint(-noise, noise + 1, arr.shape, dtype=np.int16)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img


# --------------------------------------------------------------------------- #
# Geracao de uma imagem
# --------------------------------------------------------------------------- #
def _valid_box(p: Placement, size: int) -> bool:
    """Garante bbox dentro da imagem e com area minima (evita cortes/ruido)."""
    if p.x2 <= p.x1 or p.y2 <= p.y1:
        return False
    if p.x1 < 0 or p.y1 < 0 or p.x2 > size or p.y2 > size:
        return False
    return (p.x2 - p.x1) >= 6 and (p.y2 - p.y1) >= 6


def _generate_one(
    icons_by_class: Dict[str, List[Path]],
    class_names: List[str],
    icon_cache: Dict[Path, Image.Image],
    rng: random.Random,
    font: ImageFont.ImageFont,
    isolated: bool = False,
    balancer: Optional[le.ClassBalancer] = None,
) -> Tuple[Image.Image, List[Placement]]:
    """Gera UMA imagem a partir de um `DiagramSpec` do layout_engine.

    Ordem de renderizacao: fundo -> caixas AWS -> conexoes ortogonais ->
    icones -> rotulos. As bounding boxes YOLO usam o conteudo REAL (nao a
    margem transparente) de cada icone ja posicionado.
    """
    size = settings.image_size
    spec: DiagramSpec = (le.build_isolated(class_names, size, rng, balancer) if isolated
                         else le.build_diagram(class_names, size, rng, balancer))

    canvas = _render_background(size, spec.background, rng).convert("RGBA")
    _draw_boxes(canvas, spec, font)

    # distancia ao vizinho mais proximo limita o tamanho (evita overlap excessivo)
    centers = [(s.cx, s.cy) for s in spec.icons]
    nn = _nn_distances(centers)

    prepared = []  # (icon_img, px, py, content_rect, class_id, slot)
    rects: List[Optional[Tuple[float, float, float, float]]] = []

    for idx, slot in enumerate(spec.icons):
        icon_path = rng.choice(icons_by_class[slot.class_name])
        if icon_path not in icon_cache:
            icon_cache[icon_path] = _load_icon_variants(icon_path)
        variants = icon_cache[icon_path]

        target = slot.size
        if nn[idx] is not None:
            target = min(target, int(nn[idx] * 0.95))
        target = int(max(24, min(target, size * 0.9)))

        icon_img = _finalize_icon(variants, target, rng)
        iw, ih = icon_img.size
        # posiciona centralizado no slot, garantindo que caiba 100% na imagem
        px = int(round(min(max(slot.cx - iw / 2, 0), max(0, size - iw))))
        py = int(round(min(max(slot.cy - ih / 2, 0), max(0, size - ih))))

        cbox = icon_img.split()[-1].getbbox()  # conteudo real (ignora margem)
        if cbox is None:
            rects.append(None)
            continue
        crect = (px + cbox[0], py + cbox[1], px + cbox[2], py + cbox[3])
        rects.append(crect)
        prepared.append((icon_img, px, py, crect, class_names.index(slot.class_name), slot))

    # conexoes por baixo dos icones (setas terminam na borda do icone)
    _draw_connections(canvas, spec, rects, rng)

    # cola os icones por cima
    for icon_img, px, py, crect, cid, slot in prepared:
        canvas.alpha_composite(icon_img, (px, py))

    # rotulos (nome do servico + rotulos contextuais)
    draw = ImageDraw.Draw(canvas)
    for icon_img, px, py, crect, cid, slot in prepared:
        if slot.show_label:
            _draw_service_label(draw, crect, class_names[cid], rng, font)
    for lab in spec.labels:
        draw.text((lab.x, lab.y), lab.text, fill=lab.color, font=font)

    final = _global_finish(canvas.convert("RGB"), rng)

    placements = [Placement(int(round(c[0])), int(round(c[1])),
                            int(round(c[2])), int(round(c[3])), cid)
                  for _, _, _, c, cid, _ in prepared]
    placements = [p for p in placements if _valid_box(p, size)]
    return final, placements


def _write_label(label_path: Path, placements: List[Placement], size: int) -> None:
    lines = []
    for p in placements:
        xc = ((p.x1 + p.x2) / 2) / size
        yc = ((p.y1 + p.y2) / 2) / size
        w = (p.x2 - p.x1) / size
        h = (p.y2 - p.y1) / size
        lines.append(f"{p.class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")
    label_path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------- #
# API publica do modulo
# --------------------------------------------------------------------------- #
def generate_dataset(
    train_images: int | None = None,
    val_images: int | None = None,
    on_progress=None,
    seed: int | None = None,
) -> Tuple[Path, List[str]]:
    """Gera o dataset sintetico completo e o arquivo data.yaml.

    `seed`: se None, usa `settings.seed`; se este tambem for None, sorteia uma
    seed aleatoria (execucoes consecutivas produzem datasets diferentes).

    Retorna (caminho_data_yaml, lista_de_classes).
    """
    train_images = train_images or settings.train_images
    val_images = val_images or settings.val_images

    if seed is None:
        seed = settings.seed
    if seed is None:
        seed = random.randrange(1, 2 ** 31 - 1)

    rng = random.Random(seed)
    random.seed(seed)                 # usado por _load_icon_hires (margem)
    np.random.seed(seed % (2 ** 32))  # usado pelas augmentations com numpy

    icons_by_class = discover_icons(settings.icons_dir)
    class_names = list(icons_by_class.keys())

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        font = ImageFont.load_default()

    dataset_dir = settings.dataset_dir
    icon_cache: Dict[Path, Image.Image] = {}
    balancer = le.ClassBalancer(class_names)  # frequencia uniforme entre classes

    splits = {"train": train_images, "val": val_images}
    for split, count in splits.items():
        img_dir = dataset_dir / "images" / split
        lbl_dir = dataset_dir / "labels" / split
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)

        # Limpa arquivos antigos do split.
        for old in img_dir.glob("*"):
            old.unlink()
        for old in lbl_dir.glob("*"):
            old.unlink()

        min_icons = max(1, settings.min_icons_per_image)
        for i in range(count):
            # ~80% diagramas completos, ~20% icones isolados / grupos pequenos.
            isolated = rng.random() < settings.isolated_ratio
            image, placements = _generate_one(
                icons_by_class, class_names, icon_cache, rng, font,
                isolated=isolated, balancer=balancer,
            )
            # garante o minimo de icones: regenera (diagrama completo) se faltar.
            attempts = 0
            while len(placements) < min_icons and attempts < 6:
                attempts += 1
                image, placements = _generate_one(
                    icons_by_class, class_names, icon_cache, rng, font,
                    isolated=False, balancer=balancer,
                )
            name = f"{split}_{i:05d}"
            image.save(img_dir / f"{name}.jpg", quality=90)
            _write_label(lbl_dir / f"{name}.txt", placements, settings.image_size)

            if on_progress and (i + 1) % 25 == 0:
                on_progress(split, i + 1, count)

    data_yaml = {
        "path": str(dataset_dir.resolve()),
        "train": "images/train",
        "val": "images/val",
        "nc": len(class_names),
        "names": class_names,
    }
    settings.data_yaml_path.write_text(
        yaml.safe_dump(data_yaml, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    return settings.data_yaml_path, class_names
