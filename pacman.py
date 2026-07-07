import pygame
import math
from entidad import Entidad
from constantes import *


class PacMan(Entidad):
    def __init__(self, col=14, fila=23, velocidad=VEL_PACMAN):
        super().__init__(col, fila, velocidad)
        self.puntuacion = 0
        self.vidas = 3
        self.frame_boca = 0
        self.radio = TILE_SIZE // 2 - 1

    def update(self, mapa):
        super().update(mapa)
        puntos = mapa.comer(self.tile_col, self.tile_fila)
        self.puntuacion += puntos
        if self.direccion != QUIETO:
            self.frame_boca = (self.frame_boca + 1) % 20

    def render(self, surface):
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

    def reiniciar_posicion(self, col=14, fila=23):
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = fila * TILE_SIZE + TILE_SIZE // 2
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
