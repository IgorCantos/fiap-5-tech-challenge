
"""Motor de layout de diagramas de arquitetura AWS.

Responsabilidade UNICA: gerar a *estrutura logica* de um diagrama (posicoes dos
icones, caixas/containers aninhados, conexoes entre servicos e rotulos de
texto). Este modulo NAO carrega icones, NAO compoe imagem e NAO escreve
anotacoes -- isso continua a cargo de `dataset.py`.

A saida e um `DiagramSpec` (estrutura de dados pura) que o pipeline de
composicao consome para renderizar a imagem e produzir os labels YOLO.

Ideias implementadas
---------------------
- Varios algoritmos de layout (pipeline horizontal/vertical, arvore, estrela,
  grade, duas colunas, tres camadas, mesh, hub-and-spoke, serverless,
  microservices), escolhidos aleatoriamente por imagem.
- Containers reais da AWS aninhados (AWS Cloud, Region, VPC, Availability Zone,
  Public/Private Subnet, Security Group) com os icones posicionados dentro.
- Biblioteca de templates de arquiteturas conhecidas (CloudFront -> ALB -> ECS
  -> RDS, API Gateway -> Lambda -> DynamoDB, etc.), cada um com variacoes.
- Conexoes ligando os proprios icones (nunca linhas aleatorias), com roteamento
  ortogonal (segmentos H/V, "L"), evitando diagonais.
- Distribuicao de escala probabilistica (~30% pequenos, ~50% medios, ~20%
  grandes) e "snap" de grade com jitter para parecer feito a mao.
- Rotulos contextuais (VPC, Public Subnet, Users, Internet, Region, ...).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from app.config import settings

Point = Tuple[float, float]
Rect = Tuple[float, float, float, float]  # (x1, y1, x2, y2)
Color = Tuple[int, int, int]


# --------------------------------------------------------------------------- #
# Estruturas de dados (spec logico do diagrama)
# --------------------------------------------------------------------------- #
@dataclass
class IconSlot:
    """Um icone a ser colado: classe + centro + tamanho alvo (maior lado, px)."""

    class_name: str
    cx: float
    cy: float
    size: int
    show_label: bool = True


@dataclass
class Box:
    """Container tipo AWS (retangulo com cantos arredondados e rotulo)."""

    x1: float
    y1: float
    x2: float
    y2: float
    kind: str            # 'aws-cloud' | 'region' | 'vpc' | 'az' | 'public-subnet' ...
    label: str = ""
    depth: int = 0


@dataclass
class Connection:
    """Ligacao entre dois icones (por indice em `DiagramSpec.icons`)."""

    a: int
    b: int
    width: int = 2
    color: Color = (110, 110, 120)
    arrow: bool = True
    dashed: bool = False


@dataclass
class TextLabel:
    x: float
    y: float
    text: str
    color: Color = (90, 90, 100)
    size: int = 15
    anchor: str = "la"   # ancoras do PIL (la, ma, ...)


@dataclass
class DiagramSpec:
    size: int
    background: str
    complexity: str = "medium"
    boxes: List[Box] = field(default_factory=list)
    icons: List[IconSlot] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
    labels: List[TextLabel] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Vocabulario e estilos
# --------------------------------------------------------------------------- #
BACKGROUND_STYLES = [
    "white", "white", "grid", "grid", "gray", "drawio", "lucid", "miro", "ppt",
]

BOX_LABELS = {
    "aws-cloud": "AWS Cloud",
    "account": "AWS Account",
    "region": "Region",
    "vpc": "VPC",
    "az": "Availability Zone",
    "public-subnet": "Public Subnet",
    "private-subnet": "Private Subnet",
    "security-group": "Security Group",
    "generic": "",
}

CONTEXT_LABELS = [
    "Users", "Internet", "API", "Database", "Application", "Ingress", "Egress",
    "Load Balancer", "Region", "Production", "Development", "Client", "Traffic",
]

# Termos de template -> substrings que podem existir nos nomes das classes reais.
SERVICE_SYNONYMS: Dict[str, List[str]] = {
    "s3": ["s3", "bucket", "storage"],
    "glacier": ["glacier"],
    "lambda": ["lambda", "function"],
    "rds": ["rds", "database", "db", "aurora"],
    "dynamodb": ["dynamo", "rds", "db"],
    "elasticache": ["cache", "redis", "rds"],
    "ec2": ["ec2", "instance", "compute"],
    "ecs": ["ecs", "fargate", "container", "ec2"],
    "alb": ["load-balancer", "alb", "elb", "balancer"],
    "cloudwatch": ["cloud-watch", "cloudwatch", "watch", "monitor"],
    "cloudfront": ["cloudfront", "cdn"],
    "apigateway": ["api", "gateway"],
    "sns": ["sns", "notification"],
    "sqs": ["sqs", "queue"],
    "eventbridge": ["event", "bridge"],
    "connect": ["connect"],
}


# --------------------------------------------------------------------------- #
# Biblioteca de templates de arquiteturas reais
# Cada template define uma sequencia de servicos e (opcionalmente) arestas extra.
# As conexoes padrao ligam a sequencia em cadeia (0->1->2->...).
# --------------------------------------------------------------------------- #
TEMPLATES: List[Dict] = [
    {"name": "web-3tier", "services": ["cloudfront", "alb", "ecs", "rds"]},
    {"name": "serverless-api", "services": ["apigateway", "lambda", "dynamodb"]},
    {"name": "s3-event", "services": ["s3", "lambda", "sns"]},
    {"name": "static-site", "services": ["cloudfront", "s3"]},
    {"name": "contact-center", "services": ["connect", "lambda", "dynamodb"]},
    {"name": "event-driven", "services": ["eventbridge", "lambda", "sqs"]},
    {"name": "cache-tier", "services": ["ecs", "elasticache", "rds"]},
    {"name": "fanout", "services": ["sns", "sqs", "lambda"], "edges": [(0, 1), (1, 2)]},
    {"name": "ingest-lake", "services": ["s3", "lambda", "glacier"]},
    {"name": "api-cache", "services": ["apigateway", "lambda", "elasticache", "dynamodb"]},
    {"name": "web-monitored", "services": ["alb", "ec2", "rds", "cloudwatch"],
     "edges": [(0, 1), (1, 2), (1, 3)]},
    {"name": "microbatch", "services": ["s3", "lambda", "dynamodb", "sns"]},
    {"name": "queue-worker", "services": ["apigateway", "sqs", "lambda", "rds"]},
    {"name": "cdn-alb-ec2", "services": ["cloudfront", "alb", "ec2", "rds", "cloudwatch"],
     "edges": [(0, 1), (1, 2), (2, 3), (2, 4)]},
    {"name": "data-archive", "services": ["ec2", "s3", "glacier"]},
    {"name": "notify-pipeline", "services": ["eventbridge", "lambda", "sns", "sqs"],
     "edges": [(0, 1), (1, 2), (1, 3)]},
]

LAYOUTS = [
    "pipeline_h", "pipeline_v", "tree", "star", "grid", "two_columns",
    "three_tier", "mesh", "hub_spoke", "serverless", "microservices",
]


# --------------------------------------------------------------------------- #
# Helpers de escala, snap e jitter
# --------------------------------------------------------------------------- #
def sample_scale_frac(rng: random.Random) -> float:
    """Escala (fracao do lado da imagem) com distribuicao ~30/50/20."""
    lo, hi = settings.min_icon_scale, settings.max_icon_scale
    span = hi - lo
    r = rng.random()
    if r < 0.30:                      # pequenos
        a, b = lo, lo + span * 0.34
    elif r < 0.80:                    # medios
        a, b = lo + span * 0.34, lo + span * 0.67
    else:                            # grandes
        a, b = lo + span * 0.67, hi
    return rng.uniform(a, b)


def _snap(value: float, grid: int) -> float:
    return round(value / grid) * grid


def _jitter(rng: random.Random, amount: float) -> float:
    return rng.uniform(-amount, amount)


def _snap_jitter(rng: random.Random, x: float, y: float,
                 jitter: float) -> Point:
    grid = max(4, settings.snap_grid)
    sx = _snap(x, grid) + _jitter(rng, jitter)
    sy = _snap(y, grid) + _jitter(rng, jitter)
    return sx, sy


class ClassBalancer:
    """Balanceia a frequencia das classes ao longo de todo o dataset.

    Mantem um contador global e escolhe classes com probabilidade inversamente
    proporcional ao uso, de modo que todas apareçam com frequencia parecida
    (importante quando ha muitas classes e templates que favorecem algumas).
    """

    def __init__(self, class_names: List[str]):
        self.counts: Dict[str, int] = {c: 0 for c in class_names}

    def register(self, class_name: str) -> None:
        if class_name in self.counts:
            self.counts[class_name] += 1

    def pick(self, rng: random.Random, class_names: Optional[List[str]] = None) -> str:
        names = class_names or list(self.counts)
        maxc = max((self.counts.get(n, 0) for n in names), default=0)
        weights = [maxc - self.counts.get(n, 0) + 1 for n in names]
        chosen = rng.choices(names, weights=weights, k=1)[0]
        self.register(chosen)
        return chosen


def _pick_class(class_names: List[str], rng: random.Random,
                balancer: Optional[ClassBalancer]) -> str:
    """Escolhe uma classe: balanceada se houver balancer, senao uniforme."""
    if balancer is not None:
        return balancer.pick(rng, class_names)
    return rng.choice(class_names)


def resolve_service(keyword: str, class_names: List[str], rng: random.Random,
                    balancer: Optional["ClassBalancer"] = None) -> str:
    """Resolve um termo de template para uma classe realmente disponivel.

    Quando ha correspondencia por sinonimo, respeita a semantica do template
    (e registra o uso no balancer). Sem correspondencia, cai para uma escolha
    balanceada entre todas as classes.
    """
    kw = keyword.lower()
    syn = SERVICE_SYNONYMS.get(kw, [kw])
    matches = [cn for cn in class_names if any(s in cn.lower() for s in syn)]
    if matches:
        chosen = rng.choice(matches)
        if balancer is not None:
            balancer.register(chosen)
        return chosen
    return _pick_class(class_names, rng, balancer)


# --------------------------------------------------------------------------- #
# Algoritmos de layout: posicionam N centros dentro de uma regiao
# Cada funcao retorna List[Point] (centros) na ordem logica dos servicos.
# --------------------------------------------------------------------------- #
def _region_dims(region: Rect) -> Tuple[float, float, float, float, float, float]:
    x1, y1, x2, y2 = region
    return x1, y1, x2, y2, (x2 - x1), (y2 - y1)


def layout_pipeline_h(n: int, region: Rect, rng: random.Random) -> List[Point]:
    x1, y1, x2, y2, w, h = _region_dims(region)
    cy = y1 + h / 2
    pts = []
    for i in range(n):
        cx = x1 + w * (i + 0.5) / n
        pts.append(_snap_jitter(rng, cx, cy + _jitter(rng, h * 0.06), h * 0.05))
    return pts


def layout_pipeline_v(n: int, region: Rect, rng: random.Random) -> List[Point]:
    x1, y1, x2, y2, w, h = _region_dims(region)
    cx = x1 + w / 2
    pts = []
    for i in range(n):
        cy = y1 + h * (i + 0.5) / n
        pts.append(_snap_jitter(rng, cx + _jitter(rng, w * 0.06), cy, w * 0.05))
    return pts


def layout_two_columns(n: int, region: Rect, rng: random.Random) -> List[Point]:
    x1, y1, x2, y2, w, h = _region_dims(region)
    rows = (n + 1) // 2
    pts = []
    for i in range(n):
        col = i % 2
        row = i // 2
        cx = x1 + w * (0.28 if col == 0 else 0.72)
        cy = y1 + h * (row + 0.5) / max(1, rows)
        pts.append(_snap_jitter(rng, cx, cy, min(w, h) * 0.04))
    return pts


def layout_grid(n: int, region: Rect, rng: random.Random) -> List[Point]:
    x1, y1, x2, y2, w, h = _region_dims(region)
    cols = max(1, int(round(n ** 0.5)))
    rows = (n + cols - 1) // cols
    pts = []
    for i in range(n):
        r, c = divmod(i, cols)
        cx = x1 + w * (c + 0.5) / cols
        cy = y1 + h * (r + 0.5) / rows
        pts.append(_snap_jitter(rng, cx, cy, min(w / cols, h / rows) * 0.12))
    return pts


def layout_tree(n: int, region: Rect, rng: random.Random) -> List[Point]:
    x1, y1, x2, y2, w, h = _region_dims(region)
    pts = [(_snap(x1 + w / 2, settings.snap_grid), y1 + h * 0.14)]  # raiz
    remaining = n - 1
    if remaining <= 0:
        return pts
    # duas linhas de filhos
    row1 = min(remaining, max(2, remaining // 2 + remaining % 2))
    for i in range(row1):
        cx = x1 + w * (i + 0.5) / row1
        pts.append(_snap_jitter(rng, cx, y1 + h * 0.52, w * 0.03))
    row2 = remaining - row1
    for i in range(row2):
        cx = x1 + w * (i + 0.5) / max(1, row2)
        pts.append(_snap_jitter(rng, cx, y1 + h * 0.85, w * 0.03))
    return pts


def layout_star(n: int, region: Rect, rng: random.Random) -> List[Point]:
    import math
    x1, y1, x2, y2, w, h = _region_dims(region)
    cx, cy = x1 + w / 2, y1 + h / 2
    pts = [(cx, cy)]
    k = n - 1
    radius = min(w, h) * 0.36
    for i in range(k):
        ang = 2 * math.pi * i / max(1, k) - math.pi / 2
        px = cx + radius * math.cos(ang)
        py = cy + radius * math.sin(ang)
        pts.append(_snap_jitter(rng, px, py, radius * 0.06))
    return pts


def layout_hub_spoke(n: int, region: Rect, rng: random.Random) -> List[Point]:
    return layout_star(n, region, rng)


def layout_three_tier(n: int, region: Rect, rng: random.Random) -> List[Point]:
    x1, y1, x2, y2, w, h = _region_dims(region)
    tiers = [y1 + h * 0.2, y1 + h * 0.5, y1 + h * 0.8]
    per = [0, 0, 0]
    for i in range(n):
        per[i % 3] += 1
    pts = []
    idx_in_tier = [0, 0, 0]
    for i in range(n):
        t = i % 3
        count = max(1, per[t])
        cx = x1 + w * (idx_in_tier[t] + 0.5) / count
        idx_in_tier[t] += 1
        pts.append(_snap_jitter(rng, cx, tiers[t], w * 0.03))
    return pts


def layout_mesh(n: int, region: Rect, rng: random.Random) -> List[Point]:
    return layout_grid(n, region, rng)


def layout_microservices(n: int, region: Rect, rng: random.Random) -> List[Point]:
    return layout_grid(n, region, rng)


def layout_serverless(n: int, region: Rect, rng: random.Random) -> List[Point]:
    return layout_pipeline_h(n, region, rng)


LAYOUT_FUNCS: Dict[str, Callable[[int, Rect, random.Random], List[Point]]] = {
    "pipeline_h": layout_pipeline_h,
    "pipeline_v": layout_pipeline_v,
    "tree": layout_tree,
    "star": layout_star,
    "grid": layout_grid,
    "two_columns": layout_two_columns,
    "three_tier": layout_three_tier,
    "mesh": layout_mesh,
    "hub_spoke": layout_hub_spoke,
    "serverless": layout_serverless,
    "microservices": layout_microservices,
}


# --------------------------------------------------------------------------- #
# Conexoes por layout (quando nao ha template): ligam servicos de modo coerente
# --------------------------------------------------------------------------- #
def _edges_for_layout(layout: str, n: int, rng: random.Random) -> List[Tuple[int, int]]:
    if n < 2:
        return []
    if layout in ("star", "hub_spoke"):
        return [(0, i) for i in range(1, n)]
    if layout == "tree":
        edges = []
        for i in range(1, n):
            parent = max(0, (i - 1) // 2)
            edges.append((parent, i))
        return edges
    if layout in ("mesh", "microservices"):
        edges = [(i, i + 1) for i in range(n - 1)]
        for _ in range(max(1, n // 3)):
            a, b = rng.randrange(n), rng.randrange(n)
            if a != b:
                edges.append((a, b))
        return edges
    # pipelines, grid, colunas, tiers -> cadeia sequencial
    return [(i, i + 1) for i in range(n - 1)]


# --------------------------------------------------------------------------- #
# Containers AWS (caixas aninhadas) + regioes de posicionamento
# --------------------------------------------------------------------------- #
def _inset(region: Rect, dx: float, dy: float) -> Rect:
    x1, y1, x2, y2 = region
    return (x1 + dx, y1 + dy, x2 - dx, y2 - dy)


def _build_containers(region: Rect, complexity: str, rng: random.Random
                      ) -> Tuple[List[Box], List[Rect]]:
    """Cria caixas AWS aninhadas e devolve as regioes internas p/ os icones."""
    boxes: List[Box] = []
    x1, y1, x2, y2 = region
    w, h = x2 - x1, y2 - y1

    if complexity == "simple":
        if rng.random() < 0.55:
            boxes.append(Box(x1, y1, x2, y2, "aws-cloud", BOX_LABELS["aws-cloud"], 0))
            return boxes, [_inset(region, w * 0.06, h * 0.12)]
        return boxes, [region]

    # medium / complex: AWS Cloud externa
    boxes.append(Box(x1, y1, x2, y2, "aws-cloud", BOX_LABELS["aws-cloud"], 0))
    vpc = _inset(region, w * 0.05, h * 0.1)
    boxes.append(Box(*vpc, "vpc", BOX_LABELS["vpc"], 1))

    if complexity == "medium":
        inner = _inset(vpc, (vpc[2] - vpc[0]) * 0.05, (vpc[3] - vpc[1]) * 0.14)
        # as vezes uma subnet unica
        if rng.random() < 0.5:
            kind = rng.choice(["public-subnet", "private-subnet"])
            boxes.append(Box(*inner, kind, BOX_LABELS[kind], 2))
            inner = _inset(inner, 12, 22)
        return boxes, [inner]

    # complex: 2-3 subnets dentro da VPC (colunas verticais)
    vx1, vy1, vx2, vy2 = vpc
    vw = vx2 - vx1
    n_sub = rng.choice([2, 3])
    kinds = ["public-subnet", "private-subnet", "private-subnet"][:n_sub]
    regions: List[Rect] = []
    pad = vw * 0.02
    sub_w = (vw - pad * (n_sub + 1)) / n_sub
    for i in range(n_sub):
        sx1 = vx1 + pad + i * (sub_w + pad)
        sub = (sx1, vy1 + (vy2 - vy1) * 0.12, sx1 + sub_w, vy2 - (vy2 - vy1) * 0.04)
        boxes.append(Box(*sub, kinds[i], BOX_LABELS[kinds[i]], 2))
        regions.append(_inset(sub, sub_w * 0.06, (sub[3] - sub[1]) * 0.1))
    return boxes, regions


# --------------------------------------------------------------------------- #
# Roteamento ortogonal de conexoes (usado pelo renderizador em dataset.py)
# --------------------------------------------------------------------------- #
def _center(rect: Rect) -> Point:
    x1, y1, x2, y2 = rect
    return (x1 + x2) / 2, (y1 + y2) / 2


def route_orthogonal(a: Rect, b: Rect, rng: random.Random) -> List[Point]:
    """Rota em L/segmentos ortogonais entre as LATERAIS de dois retangulos.

    Evita diagonais: usa apenas segmentos horizontais e verticais. Sai da borda
    do icone de origem e entra na borda do icone de destino.
    """
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    acx, acy = _center(a)
    bcx, bcy = _center(b)
    dx, dy = bcx - acx, bcy - acy

    horizontal_first = abs(dx) >= abs(dy)

    if horizontal_first:
        # sai pela esquerda/direita
        if dx >= 0:
            sx, ex = ax2, bx1
        else:
            sx, ex = ax1, bx2
        sy, ey = acy, bcy
        if abs(sy - ey) < 4:
            return [(sx, sy), (ex, ey)]
        mx = (sx + ex) / 2 + _jitter(rng, abs(ex - sx) * 0.08)
        return [(sx, sy), (mx, sy), (mx, ey), (ex, ey)]
    else:
        if dy >= 0:
            sy, ey = ay2, by1
        else:
            sy, ey = ay1, by2
        sx, ex = acx, bcx
        if abs(sx - ex) < 4:
            return [(sx, sy), (ex, ey)]
        my = (sy + ey) / 2 + _jitter(rng, abs(ey - sy) * 0.08)
        return [(sx, sy), (sx, my), (ex, my), (ex, ey)]


# --------------------------------------------------------------------------- #
# Montagem do diagrama
# --------------------------------------------------------------------------- #
def _pick_complexity(rng: random.Random) -> str:
    r = rng.random()
    if r < 0.35:
        return "simple"
    if r < 0.80:
        return "medium"
    return "complex"


def _count_for(complexity: str, rng: random.Random) -> int:
    if complexity == "simple":
        return rng.randint(max(4, settings.min_icons_per_image),
                           max(6, settings.min_icons_per_image + 2))
    if complexity == "medium":
        return rng.randint(6, 11)
    return rng.randint(12, 26)


def _instantiate_template(class_names: List[str], rng: random.Random,
                          complexity: str,
                          balancer: Optional[ClassBalancer] = None
                          ) -> Tuple[List[str], List[Tuple[int, int]], str]:
    tpl = rng.choice(TEMPLATES)
    services = [resolve_service(s, class_names, rng, balancer) for s in tpl["services"]]

    # variacao: as vezes duplica um estagio (ex.: 2 EC2 atras do ALB)
    if complexity != "simple" and rng.random() < 0.5 and len(services) >= 2:
        idx = rng.randrange(len(services))
        services.insert(idx, services[idx])

    n = len(services)
    if "edges" in tpl:
        edges = [(a, b) for a, b in tpl["edges"] if a < n and b < n]
    else:
        edges = [(i, i + 1) for i in range(n - 1)]

    layout = "pipeline_h" if n <= 4 else rng.choice(
        ["pipeline_h", "tree", "grid", "three_tier"]
    )
    return services, edges, layout


def _assign_sizes(region: Rect, count: int, rng: random.Random, size: int) -> List[int]:
    """Tamanho por icone: escala probabilistica, limitada pela celula da regiao."""
    x1, y1, x2, y2 = region
    w, h = x2 - x1, y2 - y1
    cols = max(1, int(round(count ** 0.5)))
    rows = max(1, (count + cols - 1) // cols)
    cell = min(w / cols, h / rows)
    cap = max(24, cell * 0.82)
    sizes = []
    for _ in range(count):
        px = sample_scale_frac(rng) * size
        px *= rng.uniform(0.92, 1.08)  # pequena variacao entre componentes
        sizes.append(int(max(24, min(px, cap))))
    return sizes


def _add_context_labels(spec: DiagramSpec, region: Rect, rng: random.Random) -> None:
    x1, y1, x2, y2 = region
    for _ in range(rng.randint(0, 2)):
        text = rng.choice(CONTEXT_LABELS)
        lx = rng.uniform(x1, x2 * 0.6)
        ly = rng.uniform(max(2, y1 - 18), y1 + 6)
        spec.labels.append(TextLabel(lx, ly, text,
                                     color=tuple(rng.randint(70, 130) for _ in range(3)),
                                     size=rng.choice([14, 16, 18])))


def build_isolated(class_names: List[str], size: int, rng: random.Random,
                   balancer: Optional[ClassBalancer] = None) -> DiagramSpec:
    """Grupo pequeno de icones com contexto minimo (respeita o minimo global)."""
    spec = DiagramSpec(size=size, background=rng.choice(BACKGROUND_STYLES),
                       complexity="isolated")
    min_icons = max(1, settings.min_icons_per_image)
    n = rng.randint(min_icons, min_icons + 2)
    margin = size * 0.18
    region = (margin, margin, size - margin, size - margin)
    layout = rng.choice(["pipeline_h", "pipeline_v", "grid"])
    pts = LAYOUT_FUNCS[layout](n, region, rng)
    # icones isolados tendem a ser grandes
    for i in range(n):
        frac = rng.uniform((settings.min_icon_scale + settings.max_icon_scale) / 2,
                           settings.max_icon_scale * 1.6)
        px = int(min(size * 0.34, frac * size))
        cx, cy = pts[i]
        spec.icons.append(IconSlot(_pick_class(class_names, rng, balancer), cx, cy, px,
                                   show_label=rng.random() < 0.5))
    if n >= 2 and rng.random() < 0.4:
        for i in range(n - 1):
            spec.connections.append(Connection(i, i + 1,
                                                width=rng.randint(1, 3),
                                                arrow=rng.random() < 0.7))
    return spec


def build_diagram(class_names: List[str], size: int, rng: random.Random,
                  balancer: Optional[ClassBalancer] = None) -> DiagramSpec:
    """Gera o spec logico completo de um diagrama de arquitetura."""
    if not class_names:
        raise ValueError("class_names vazio")

    complexity = _pick_complexity(rng)
    spec = DiagramSpec(size=size, background=rng.choice(BACKGROUND_STYLES),
                       complexity=complexity)

    margin = size * rng.uniform(0.04, 0.09)
    region = (margin, margin, size - margin, size - margin)
    boxes, regions = _build_containers(region, complexity, rng)
    spec.boxes.extend(boxes)

    use_template = rng.random() < 0.6
    if use_template:
        services, edges, layout = _instantiate_template(class_names, rng, complexity, balancer)
    else:
        n = _count_for(complexity, rng)
        services = [_pick_class(class_names, rng, balancer) for _ in range(n)]
        layout = rng.choice(LAYOUTS)
        edges = _edges_for_layout(layout, n, rng)

    # garante um minimo de icones por diagrama (evita imagens com 1-2 icones)
    min_icons = max(1, settings.min_icons_per_image)
    while len(services) < min_icons:
        services.append(_pick_class(class_names, rng, balancer))
        edges.append((len(services) - 2, len(services) - 1))

    n = len(services)

    # Distribui os servicos entre as regioes internas (subnets).
    n_regions = len(regions)
    groups: List[List[int]] = [[] for _ in range(n_regions)]
    for i in range(n):
        groups[i % n_regions].append(i)

    positions: List[Point] = [(0.0, 0.0)] * n
    sizes: List[int] = [0] * n
    for r_idx, region_r in enumerate(regions):
        idxs = groups[r_idx]
        if not idxs:
            continue
        lay = layout if n_regions == 1 else rng.choice(
            ["pipeline_v", "grid", "two_columns"]
        )
        pts = LAYOUT_FUNCS[lay](len(idxs), region_r, rng)
        szs = _assign_sizes(region_r, len(idxs), rng, size)
        for k, gi in enumerate(idxs):
            positions[gi] = pts[k]
            sizes[gi] = szs[k]

    for i in range(n):
        cx, cy = positions[i]
        spec.icons.append(IconSlot(services[i], cx, cy, sizes[i],
                                   show_label=rng.random() < 0.55))

    # Conexoes (variam cor/espessura). Algumas viram cruzamentos naturalmente.
    for a, b in edges:
        if a == b or a >= n or b >= n:
            continue
        spec.connections.append(Connection(
            a, b,
            width=rng.randint(1, 3),
            color=tuple(rng.randint(90, 160) for _ in range(3)),
            arrow=rng.random() < 0.85,
            dashed=rng.random() < 0.12,
        ))
    # cruzamento extra ocasional
    if n >= 4 and rng.random() < 0.35:
        a, b = rng.randrange(n), rng.randrange(n)
        if a != b:
            spec.connections.append(Connection(a, b, width=1,
                                               color=(150, 150, 160),
                                               arrow=rng.random() < 0.5))

    _add_context_labels(spec, region, rng)
    return spec
