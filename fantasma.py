import pygame
from entidad import Entidad
from constantes import *


class Fantasma(Entidad):
    def __init__(self, col, fila, velocidad, color, nombre):
        super().__init__(col, fila, velocidad)
        self.color = color
        self.nombre = nombre
        self.inicio_col = col
        self.inicio_fila = fila
        self.radio = TILE_SIZE // 2 - 1
        self.asustado = False
        self.tiempo_asustado = 0
        self.activo = True
        self.tiempo_desaparecido = 0

    def update(self, mapa):
        if not self.activo:
            self.tiempo_desaparecido -= 1
            if self.tiempo_desaparecido <= 0:
                self.reaparecer()
            return
        super().update(mapa, es_fantasma=True)
        if self.asustado:
            self.tiempo_asustado -= 1
            if self.tiempo_asustado <= 0:
                self.asustado = False

    def poner_asustado(self, duracion):
        if not self.activo:
            return
        self.asustado = True
        self.tiempo_asustado = duracion
        if self.direccion != QUIETO:
            self.direccion = (-self.direccion[0], -self.direccion[1])

    def ser_comido(self):
        self.activo = False
        self.tiempo_desaparecido = TIEMPO_DESAPARECIDO
        self.asustado = False
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO

    def reaparecer(self):
        self.x = self.inicio_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.inicio_fila * TILE_SIZE + TILE_SIZE // 2
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.asustado = False
        self.activo = True

    def reiniciar(self):
        self.x = self.inicio_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.inicio_fila * TILE_SIZE + TILE_SIZE // 2
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.asustado = False
        self.tiempo_asustado = 0
        self.activo = True
        self.tiempo_desaparecido = 0

    def render(self, surface):
        if not self.activo:
            return
        color = ASUSTADO_COLOR if self.asustado else self.color
        x, y = self.x, self.y
        r = self.radio

        # Cuerpo: semicirculo + rectangulo
        pygame.draw.circle(surface, color, (x, y - 1), r)
        pygame.draw.rect(surface, color, (x - r, y - 1, r * 2, r + 1))

        # Ondas en la base
        onda_r = r // 3
        for i in range(3):
            ox = x - r + onda_r + i * (r * 2 // 3)
            oy = y + r
            pygame.draw.circle(surface, color, (ox, oy), onda_r)

        # Ojos
        if self.asustado:
            pygame.draw.circle(surface, BLANCO, (x - 4, y - 3), 2)
            pygame.draw.circle(surface, BLANCO, (x + 4, y - 3), 2)
        else:
            dx, dy = self.direccion
            for ox in [-5, 5]:
                pygame.draw.ellipse(
                    surface, BLANCO, (x + ox - 3, y - 6, 6, 7))
                pygame.draw.circle(
                    surface, PUPILA_COLOR,
                    (x + ox + dx * 2, y - 2 + dy * 2), 2)