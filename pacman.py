import pygame
import math
from entidad import Entidad
from constantes import *
from ia import ia_pacman_tonta


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

    def update(self, mapa):
        ia_pacman_tonta(self, mapa)

        if self.invincible:
            self.tiempo_invencible -= 1
            if self.tiempo_invencible <= 0:
                self.invincible = False

        super().update(mapa)
        puntos = mapa.comer(self.tile_col, self.tile_fila)
        self.puntuacion += puntos
        if puntos == POWER_PTS:
            self.activar_power = True
        if self.direccion != QUIETO:
            self.frame_boca = (self.frame_boca + 1) % 20

    def reiniciar_posicion(self):
        self.x = PACMAN_INICIO[0] * TILE_SIZE + TILE_SIZE // 2
        self.y = PACMAN_INICIO[1] * TILE_SIZE + TILE_SIZE // 2
        self.direccion = IZQUIERDA
        self.direccion_siguiente = QUIETO
        self.invincible = True
        self.tiempo_invencible = TIEMPO_INVENCIBLE

    def reiniciar(self):
        self.reiniciar_posicion()
        self.puntuacion = 0
        self.vidas = 3
        self.activar_power = False
        self.invincible = False
        self.tiempo_invencible = 0

    def render(self, surface):
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