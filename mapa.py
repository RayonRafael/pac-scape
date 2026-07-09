"""
Maneja la cuadricula del nivel (Tilemap).
Se encarga de cargar el laberinto, dibujar las paredes neon y gestionar las pildoras (dots).
"""
# ============================================================
# mapa.py
# ============================================================
# Define el laberinto clasico de Pac-Man como una grilla de texto.
# Se encarga de:
#   - Cargar el mapa desde un array de strings
#   - Renderizar las paredes (cacheado para rendimiento)
#   - Dibujar puntos y power pellets
#   - Decir si una celda es transitable o no
#   - "Comer" puntos cuando Pac-Man pasa por encima
#   - Contar cuantos puntos quedan
# ============================================================

import pygame
from constantes import *


# ============================================================
# DATOS DEL MAPA (28 columnas x 31 filas)
# ============================================================
# Simbolos:
#   # = pared (nadie puede pasar)
#   . = punto comestible
#   o = power pellet (punto grande, activa power mode)
#   - = puerta de la casa de fantasmas (solo fantasmas pasan)
#   ' ' = espacio vacio (se puede caminar, no hay punto)
#
# Fila 14 tiene tuneles: los espacios vacios en los extremos
# permiten que Pac-Man y los fantasmas crucen de un lado al otro.
# ============================================================

MAPA_DATOS = [
    "############################",  # 0  - Borde superior
    "#............##............#",  # 1  - Zona superior con divisor central
    "#.####.#####.##.#####.####.#",  # 2  - Bloques de paredes
    "#o####.#####.##.#####.####o#",  # 3  - Power pellets en los extremos
    "#.####.#####.##.#####.####.#",  # 4
    "#..........................#",  # 5  - Pasillo largo
    "#.####.##.########.##.####.#",  # 6
    "#.####.##.########.##.####.#",  # 7
    "#......##....##....##......#",  # 8
    "######.##### ## #####.######",  # 9  - Bloques grandes separados
    "     #.##### ## #####.#     ",  # 10 - Espacios vacios en los bordes
    "     #.##          ##.#     ",  # 11
    "     #.## ###--### ##.#     ",  # 12 - Puerta de la casa de fantasmas
    "######.## #      # ##.######",  # 13 - Casa de fantasmas
    "      .   #      #   .      ",  # 14 - TUNELES (espacios en extremos)
    "######.## #      # ##.######",  # 15 - Casa de fantasmas (parte baja)
    "     #.## ######## ##.#     ",  # 16
    "     #.##          ##.#     ",  # 17
    "     #.## ######## ##.#     ",  # 18
    "######.## ######## ##.######",  # 19
    "#............##............#",  # 20 - Pasillo ancho
    "#.####.#####.##.#####.####.#",  # 21
    "#.####.#####.##.#####.####.#",  # 22
    "#o..##.......  .......##..o#",  # 23 - Power pellets + zona baja
    "###.##.##.########.##.##.###",  # 24
    "###.##.##.########.##.##.###",  # 25
    "#......##....##....##......#",  # 26
    "#.##########.##.##########.#",  # 27
    "#.##########.##.##########.#",  # 28
    "#..........................#",  # 29 - Pasillo inferior
    "############################",  # 30 - Borde inferior
]


class Mapa:
    """Maneja el laberinto: colision, puntos, render."""

    def __init__(self):
        # Convertimos el array de strings en una lista de listas
        # para poder modificar celdas individualmente (cuando Pac-Man come)
        self.grid = [list(fila) for fila in MAPA_DATOS]

        # Contamos cuantos puntos hay al inicio (para saber cuando ganaste)
        self.puntos_restantes = sum(
            1 for fila in self.grid for c in fila if c in (PUNTO, POWER)
        )

        # Pre-renderizamos las paredes en una superficie cacheada.
        # Las paredes NO cambian durante el juego, asi que las dibujamos
        # UNA SOLA VEZ y las reutilizamos cada frame. Esto es mucho mas rapido
        # que dibujar ~200 rectangulos de pared cada frame.
        self._cache_paredes = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
        self._cache_paredes.fill(NEGRO)
        self._construir_paredes()

    def _construir_paredes(self):
        """
        Dibuja todas las paredes en el cache.
        Para cada pared, dibuja:
        1. Un relleno oscuro (interior de la pared)
        2. Lineas azules en los bordes donde hay camino al lado
           (esto crea el efecto visual de "borde" del laberinto clasico)
        """
        s = self._cache_paredes
        borde = AZUL_PARED
        g = 2  # grosor de la linea del borde

        for f in range(MAPA_FILAS):
            for c in range(MAPA_COLS):
                # Solo procesamos paredes
                if self.grid[f][c] != PARED:
                    continue

                # Posicion en pixeles de esta celda
                x, y = c * TILE_SIZE, f * TILE_SIZE

                # 1) Relleno oscuro en toda la celda
                pygame.draw.rect(s, PARED_RELLENO,
                                 (x, y, TILE_SIZE, TILE_SIZE))

                # 2) Bordes azules: solo dibujamos la linea donde
                #    la celda vecina NO es pared (ahi se ve el camino)
                # Borde superior
                if f == 0 or self.grid[f - 1][c] != PARED:
                    pygame.draw.line(s, borde,
                                     (x, y), (x + TILE_SIZE - 1, y), g)
                # Borde inferior
                if f == MAPA_FILAS - 1 or self.grid[f + 1][c] != PARED:
                    pygame.draw.line(s, borde,
                                     (x, y + TILE_SIZE - 1),
                                     (x + TILE_SIZE - 1, y + TILE_SIZE - 1), g)
                # Borde izquierdo
                if c == 0 or self.grid[f][c - 1] != PARED:
                    pygame.draw.line(s, borde,
                                     (x, y), (x, y + TILE_SIZE - 1), g)
                # Borde derecho
                if c == MAPA_COLS - 1 or self.grid[f][c + 1] != PARED:
                    pygame.draw.line(s, borde,
                                     (x + TILE_SIZE - 1, y),
                                     (x + TILE_SIZE - 1, y + TILE_SIZE - 1), g)

    # ============================================================
    # CONSULTAS DE GRILLA
    # ============================================================

    def es_pared(self, col, fila):
        """Devuelve True si la celda es una pared solida."""
        # Si esta fuera del mapa, tratamos como pared
        if col < 0 or col >= MAPA_COLS or fila < 0 or fila >= MAPA_FILAS:
            return True
        return self.grid[fila][col] == PARED

    def es_transitable(self, col, fila, es_fantasma=False):
        """
        Devuelve True si una entidad puede pisar esa celda.
        La puerta solo es transitable para fantasmas (no para Pac-Man).
        """
        if col < 0 or col >= MAPA_COLS or fila < 0 or fila >= MAPA_FILAS:
            return False
        celda = self.grid[fila][col]
        if celda == PARED:
            return False
        if celda == PUERTA:
            return es_fantasma  # Solo fantasmas cruzan la puerta
        return True

    def comer(self, col, fila):
        """
        Come lo que haya en la celda (punto o power pellet).
        Devuelve los puntos ganados (10, 50, o 0 si no habia nada).
        """
        if col < 0 or col >= MAPA_COLS or fila < 0 or fila >= MAPA_FILAS:
            return 0
        celda = self.grid[fila][col]
        if celda == PUNTO:
            self.grid[fila][col] = VACIO      # Eliminar el punto del mapa
            self.puntos_restantes -= 1         # Actualizar contador
            return PUNTO_PTS                   # Devolver 10 puntos
        if celda == POWER:
            self.grid[fila][col] = VACIO      # Eliminar el power pellet
            self.puntos_restantes -= 1
            return POWER_PTS                   # Devolver 50 puntos
        return 0  # No habia nada comible

    # ============================================================
    # RENDER
    # ============================================================

    def render(self, surface):
        """
        Dibuja todo el mapa en la superficie dada.
        1) Copia el cache de paredes (muy rapido, es un solo blit)
        2) Dibuja los puntos y power pellets (cambian durante el juego)
        3) Dibuja la puerta de la casa de fantasmas
        """
        # 1) Paredes cacheadas
        surface.blit(self._cache_paredes, (0, 0))

        # 2) Elementos dinamicos (se dibujan cada frame porque cambian)
        t = pygame.time.get_ticks()  # Tiempo actual para animaciones
        for f in range(MAPA_FILAS):
            for c in range(MAPA_COLS):
                celda = self.grid[f][c]
                # Centro de la celda en pixeles
                cx = c * TILE_SIZE + TILE_SIZE // 2
                cy = f * TILE_SIZE + TILE_SIZE // 2

                if celda == PUNTO:
                    # Punto pequeno: circulo de 2px de radio
                    pygame.draw.circle(surface, PUNTO_COLOR, (cx, cy), 2)

                elif celda == POWER:
                    # Power pellet: circulo que pulsa (crece y decrece)
                    # La funcion abs(... ) crea un ciclo triangular de 800ms
                    radio = int(4 + 2 * abs((t % 800) / 400 - 1))
                    pygame.draw.circle(surface, PUNTO_COLOR, (cx, cy), radio)

                elif celda == PUERTA:
                    # Puerta: rectangulo rosa horizontal
                    pygame.draw.rect(
                        surface, ROSA,
                        (c * TILE_SIZE + 2,
                         f * TILE_SIZE + TILE_SIZE // 2 - 2,
                         TILE_SIZE - 4, 4))