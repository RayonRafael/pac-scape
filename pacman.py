import pygame
import math
from entidad import Entidad
from constantes import *


class PacMan(Entidad):
    def __init__(self, col=14, fila=23, velocidad=VEL_PACMAN):
        super().__init__(col, fila, velocidad)
        self.direccion = IZQUIERDA
        self.puntuacion = 0
        self.vidas = 3
        self.frame_boca = 0
        self.radio = TILE_SIZE // 2 - 1
        self.activar_power = False
        self.invincible = False
        self.tiempo_invencible = 0
        self.dificultad = DIFIC_TONTA
        self.peligro_grid = [[0.0] * MAPA_COLS for _ in range(MAPA_FILAS)]
        self.muriendo = False
        self.frame_muerte = 0
        self.comio_punto = False
        self.comio_power = False

    def update(self, mapa):
        self.comio_punto = False
        self.comio_power = False

        if self.muriendo:
            self.frame_muerte += 1
            return

        if self.invincible:
            self.tiempo_invencible -= 1
            if self.tiempo_invencible <= 0:
                self.invincible = False

        if self.dificultad == DIFIC_MAESTRA:
            for f in range(MAPA_FILAS):
                for c in range(MAPA_COLS):
                    self.peligro_grid[f][c] *= 0.998

        super().update(mapa)
        puntos = mapa.comer(self.tile_col, self.tile_fila)
        self.puntuacion += puntos

        if puntos > 0:
            self.comio_punto = True
        if puntos == POWER_PTS:
            self.comio_power = True
            self.activar_power = True

        if self.direccion != QUIETO:
            self.frame_boca = (self.frame_boca + 1) % 20

    def iniciar_muerte(self):
        self.muriendo = True
        self.frame_muerte = 0
        self.direccion = QUIETO

    def registrar_muerte(self):
        for df in range(-4, 5):
            for dc in range(-4, 5):
                nf = self.tile_fila + df
                nc = self.tile_col + dc
                if 0 <= nf < MAPA_FILAS and 0 <= nc < MAPA_COLS:
                    dist = abs(df) + abs(dc)
                    inc = max(0, 0.6 - dist * 0.1)
                    self.peligro_grid[nf][nc] = min(
                        1.0, self.peligro_grid[nf][nc] + inc)

    def reiniciar_posicion(self):
        self.x = PACMAN_INICIO[0] * TILE_SIZE + TILE_SIZE // 2
        self.y = PACMAN_INICIO[1] * TILE_SIZE + TILE_SIZE // 2
        self.direccion = IZQUIERDA
        self.direccion_siguiente = QUIETO
        self.invincible = False
        self.tiempo_invencible = 0
        self.muriendo = False
        self.frame_muerte = 0

    def reiniciar(self):
        self.reiniciar_posicion()
        self.puntuacion = 0
        self.vidas = 3
        self.activar_power = False
        self.invincible = False
        self.tiempo_invencible = 0
        self.peligro_grid = [[0.0] * MAPA_COLS for _ in range(MAPA_FILAS)]

    def render(self, surface):
        if self.muriendo:
            self._render_muerte(surface)
            return
        if self.invincible and (self.tiempo_invencible // 5) % 2 == 0:
            return

        pygame.draw.circle(surface, AMARILLO, (self.x, self.y), self.radio)
        dx, dy = self.direccion
        if dx != 0 or dy != 0:
            angulo = math.atan2(-dy, dx)
            boca_max = 0.5
            boca = boca_max * abs(math.sin(self.frame_boca * math.pi / 10))
            ext = self.radio + 2
            p2 = (self.x + int(ext * math.cos(angulo - boca)),
                  self.y - int(ext * math.sin(angulo - boca)))
            p3 = (self.x + int(ext * math.cos(angulo + boca)),
                  self.y - int(ext * math.sin(angulo + boca)))
            pygame.draw.polygon(surface, NEGRO, [(self.x, self.y), p2, p3])

    def _render_muerte(self, surface):
        progreso = self.frame_muerte / TIEMPO_MURIENDO
        if progreso >= 0.9:
            return
        r = max(1, int(self.radio * (1.0 - progreso * 0.9)))
        pygame.draw.circle(surface, AMARILLO, (self.x, self.y), r)
        angulo_apertura = 0.1 * math.pi + progreso * 0.85 * math.pi
        ext = r + 2
        p2 = (self.x + int(ext * math.cos(-angulo_apertura)),
              self.y - int(ext * math.sin(-angulo_apertura)))
        p3 = (self.x + int(ext * math.cos(angulo_apertura)),
              self.y - int(ext * math.sin(angulo_apertura)))
        pygame.draw.polygon(surface, NEGRO, [(self.x, self.y), p2, p3])