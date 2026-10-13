"""Distância pelo caminho livre num mapa de ocupação (PNG/PGM do map_server).

Substitui a linha reta quando há obstáculos entre os pontos: dois lados de
uma estante podem estar a 2 m em linha reta e a 15 m pelo caminho. O mapa é
reduzido para células de `cell_m`, os obstáculos são inflados pelo raio do
robô (`inflate_m`) e a distância é a de um Dijkstra 8-conectado a partir de
cada ponto consultado (com cache por ponto de origem).

Não é o planejador do Nav2 — não considera custo de proximidade nem
cinemática —, mas captura o que importa para alocar: quanto o robô realmente
precisa andar para chegar.
"""
from __future__ import annotations

import heapq
import math
from pathlib import Path

import numpy as np

SQRT2 = math.sqrt(2.0)


class GridMap:
    def __init__(
        self,
        image_path: str | Path,
        resolution: float,
        origin: tuple[float, float],
        free_threshold: int = 240,
        inflate_m: float = 0.25,
        cell_m: float = 0.1,
    ) -> None:
        from PIL import Image

        raw = np.array(Image.open(image_path).convert("L"))
        occupied_px = raw < free_threshold  # cinza (desconhecido) conta como ocupado

        factor = max(1, int(round(cell_m / resolution)))
        h, w = (occupied_px.shape[0] // factor) * factor, (occupied_px.shape[1] // factor) * factor
        # Linha 0 da imagem é o topo (y máximo); o crop descarta o resto do topo/direita
        # para manter a origem (canto inferior esquerdo) alinhada.
        cropped = occupied_px[occupied_px.shape[0] - h:, :w]
        blocks = cropped.reshape(h // factor, factor, w // factor, factor).any(axis=(1, 3))
        self.cell = resolution * factor
        self.origin = (float(origin[0]), float(origin[1]))
        self.occupied = _inflate(np.flipud(blocks), int(math.ceil(inflate_m / self.cell)))  # [row=y][col=x]
        self._cache: dict[tuple[int, int], np.ndarray] = {}

    @property
    def shape(self) -> tuple[int, int]:
        return self.occupied.shape

    def to_cell(self, p: tuple[float, float]) -> tuple[int, int]:
        return int((p[1] - self.origin[1]) / self.cell), int((p[0] - self.origin[0]) / self.cell)

    def is_free(self, p: tuple[float, float]) -> bool:
        r, c = self.to_cell(p)
        return 0 <= r < self.shape[0] and 0 <= c < self.shape[1] and not self.occupied[r, c]

    def distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        ca, cb = self.to_cell(a), self.to_cell(b)
        if ca == cb:
            return 0.0
        if cb in self._cache and ca not in self._cache:
            ca, cb = cb, ca  # grafo simétrico: reaproveita o Dijkstra já feito
        field = self._cache.get(ca)
        if field is None:
            field = self._dijkstra(ca)
            self._cache[ca] = field
        d = field[cb]
        return float(d) * self.cell if np.isfinite(d) else math.inf

    def _dijkstra(self, start: tuple[int, int]) -> np.ndarray:
        rows, cols = self.shape
        occ = self.occupied
        dist = np.full(self.shape, np.inf)
        if occ[start]:
            return dist
        dist[start] = 0.0
        heap = [(0.0, start[0], start[1])]
        steps = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                 (1, 1, SQRT2), (1, -1, SQRT2), (-1, 1, SQRT2), (-1, -1, SQRT2))
        while heap:
            d, r, c = heapq.heappop(heap)
            if d > dist[r, c]:
                continue
            for dr, dc, w in steps:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not occ[nr, nc]:
                    # diagonal só se as duas células laterais estão livres (não corta quina)
                    if dr and dc and (occ[r + dr, c] or occ[r, c + dc]):
                        continue
                    nd = d + w
                    if nd < dist[nr, nc]:
                        dist[nr, nc] = nd
                        heapq.heappush(heap, (nd, nr, nc))
        return dist


def _inflate(occupied: np.ndarray, radius_cells: int) -> np.ndarray:
    if radius_cells <= 0:
        return occupied.copy()
    out = occupied.copy()
    rows, cols = occupied.shape
    for dr in range(-radius_cells, radius_cells + 1):
        for dc in range(-radius_cells, radius_cells + 1):
            if dr * dr + dc * dc > radius_cells * radius_cells:
                continue
            src = occupied[max(0, -dr):rows - max(0, dr), max(0, -dc):cols - max(0, dc)]
            out[max(0, dr):rows - max(0, -dr), max(0, dc):cols - max(0, -dc)] |= src
    return out
