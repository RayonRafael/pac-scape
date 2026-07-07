# ============================================================
# mapa.py — Datos del laberinto + logica de colision + render
# ============================================================
import pygame
from constantes import *

MAPA_DATOS = [
    "############################",  # 0
    "#............##............#",  # 1
    "#.####.#####.##.#####.####.#",  # 2
    "#o####.#####.##.#####.####o#",  # 3  power pellets
    "#.####.#####.##.#####.####.#",  # 4
    "#..........................#",  # 5
    "#.####.##.########.##.####.#",  # 6
    "#.####.##.########.##.####.#",  # 7
    "#......##....##....##......#",  # 8
    "######.##### ## #####.######",  # 9
    "     #.##### ## #####.#     ",  # 10
    "     #.##          ##.#     ",  # 11
    "     #.## ###--### ##.#     ",  # 12  puerta fantasma
    "######.## #      # ##.######",  # 13
    "      .   #      #   .      ",  # 14  ← TUNEL
    "######.## #      # ##.######",  # 15
    "     #.## ######## ##.#     ",  # 16
    "     #.##          ##.#     ",  # 17
    "     #.## ######## ##.#     ",  # 18
    "######.## ######## ##.######",  # 19
    "#............##............#",  # 20
    "#.####.#####.##.#####.####.#",  # 21
    "#.####.#####.##.#####.####.#",  # 22
    "#o..##.......  .......##..o#",  # 23  power pellets
    "###.##.##.########.##.##.###",  # 24
    "###.##.##.########.##.##.###",  # 25
    "#......##....##....##......#",  # 26
    "#.##########.##.##########.#",  # 27
    "#.##########.##.##########.#",  # 28
    "#..........................#",  # 29
    "############################",  # 30
]


class Mapa:
    def __init__(self):
        self.grid = [list(fila) for fila in MAPA_DATOS]
        self.puntos_restantes = sum(
            1 for fila in self.grid for c in fila if c in (PUNTO, POWER)
        )
        # Pre-renderizar paredes (cache estatico, se dibuja una sola vez)
        self._cache_paredes = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
        self._cache_paredes.fill(NEGRO)
        self._construir_paredes()

    # ---- construccion del cache de paredes ----
    def _construir_paredes(self):
        s = self._cache_paredes
        borde = AZUL_PARED
        g = 2  # grosor del borde
        for f in range(MAPA_FILAS):
            for c in range(MAPA_COLS):
                if self.grid[f][c] != PARED:
                    continue
                x, y = c * TILE_SIZE, f * TILE_SIZE
                # Relleno oscuro
                pygame.draw.rect(s, PARED_RELLENO, (x, y, TILE_SIZE, TILE_SIZE))
                # Bordes azules solo donde hay camino al lado
                if f == 0 or self.grid[f - 1][c] != PARED:
                    pygame.draw.line(s, borde, (x, y), (x + TILE_SIZE - 1, y), g)
                if f == MAPA_FILAS - 1 or self.grid[f + 1][c] != PARED:
                    pygame.draw.line(s, borde, (x, y + TILE_SIZE - 1),
                                     (x + TILE_SIZE - 1, y + TILE_SIZE - 1), g)
                if c == 0 or self.grid[f][c - 1] != PARED:
                    pygame.draw.line(s, borde, (x, y), (x, y + TILE_SIZE - 1), g)
                if c == MAPA_COLS - 1 or self.grid[f][c + 1] != PARED:
                    pygame.draw.line(s, borde, (x + TILE_SIZE - 1, y),
                                     (x + TILE_SIZE - 1, y + TILE_SIZE - 1), g)

    # ---- consultas de grilla ----
    def es_pared(self, col, fila):
        if col < 0 or col >= MAPA_COLS or fila < 0 or fila >= MAPA_FILAS:
            return True
        return self.grid[fila][col] == PARED

    def es_transitable(self, col, fila, es_fantasma=False):
        """Devuelve True si la entidad puede pisar ese tile."""
        if col < 0 or col >= MAPA_COLS or fila < 0 or fila >= MAPA_FILAS:
            return False
        celda = self.grid[fila][col]
        if celda == PARED:
            return False
        if celda == PUERTA:
            return es_fantasma  # solo fantasmas cruzan la puerta
        return True

    def comer(self, col, fila):
        """Come lo que haya en el tile. Devuelve puntos ganados."""
        if col < 0 or col >= MAPA_COLS or fila < 0 or fila >= MAPA_FILAS:
            return 0
        celda = self.grid[fila][col]
        if celda == PUNTO:
            self.grid[fila][col] = VACIO
            self.puntos_restantes -= 1
            return 10
        if celda == POWER:
            self.grid[fila][col] = VACIO
            self.puntos_restantes -= 1
            return 50
        return 0

    # ---- render ----
    def render(self, surface):
        # 1) Paredes cacheadas (muy rapido)
        surface.blit(self._cache_paredes, (0, 0))
        # 2) Elementos dinamicos (puntos, power pellets, puerta)
        t = pygame.time.get_ticks()
        for f in range(MAPA_FILAS):
            for c in range(MAPA_COLS):
                celda = self.grid[f][c]
                cx = c * TILE_SIZE + TILE_SIZE // 2
                cy = f * TILE_SIZE + TILE_SIZE // 2
                if celda == PUNTO:
                    pygame.draw.circle(surface, PUNTO_COLOR, (cx, cy), 2)
                elif celda == POWER:
                    radio = int(4 + 2 * abs((t % 800) / 400 - 1))
                    pygame.draw.circle(surface, PUNTO_COLOR, (cx, cy), radio)
                elif celda == PUERTA:
                    pygame.draw.rect(
                        surface, ROSA,
                        (c * TILE_SIZE + 2, f * TILE_SIZE + TILE_SIZE // 2 - 2,
                         TILE_SIZE - 4, 4))