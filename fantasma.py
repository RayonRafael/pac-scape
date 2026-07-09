import pygame
from entidad import Entidad
from constantes import *


class Fantasma(Entidad):
    def __init__(self, col, fila, velocidad, color, nombre, salida_delay=0):
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
        self.ojos_solo = False
        self.salida_delay_inicial = salida_delay
        self.timer_salida = salida_delay

    @property
    def esperando(self):
        return self.timer_salida > 0

    def update(self, mapa):
        if self.timer_salida > 0:
            self.timer_salida -= 1
            return

        if self.ojos_solo:
            self._ir_a_casa(mapa)
            super().update(mapa, es_fantasma=True)
            if (self.tile_col == self.inicio_col
                    and self.tile_fila == self.inicio_fila
                    and self.en_centro_tile()):
                self._reaparecer_ojos()
            return

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

    def _ir_a_casa(self, mapa):
        if not self.en_centro_tile():
            return
        dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
        reverso = (-self.direccion[0], -self.direccion[1])
        mejor_dir = None
        mejor_dist = float('inf')
        for d in dirs:
            if d == reverso and len(dirs) > 1:
                continue
            nc = Entidad._wrap_col(self.tile_col + d[0])
            nf = self.tile_fila + d[1]
            if not mapa.es_transitable(nc, nf, es_fantasma=True):
                continue
            dist = (nc - self.inicio_col) ** 2 + (nf - self.inicio_fila) ** 2
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_dir = d
        if mejor_dir:
            self.direccion_siguiente = mejor_dir

    def _reaparecer_ojos(self):
        self.x = self.inicio_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.inicio_fila * TILE_SIZE + TILE_SIZE // 2
        self.ojos_solo = False
        self.asustado = False
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.velocidad = VEL_FANTASMA

    def poner_asustado(self, duracion):
        if not self.activo or self.ojos_solo or self.esperando:
            return
        self.asustado = True
        self.tiempo_asustado = duracion
        if self.direccion != QUIETO:
            self.direccion = (-self.direccion[0], -self.direccion[1])

    def ser_comido(self):
        self.ojos_solo = True
        self.asustado = False
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.velocidad = VEL_FANTASMA * 2

    def reaparecer(self):
        self.x = self.inicio_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.inicio_fila * TILE_SIZE + TILE_SIZE // 2
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.asustado = False
        self.ojos_solo = False
        self.activo = True
        self.velocidad = VEL_FANTASMA

    def reiniciar(self):
        self.x = self.inicio_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.inicio_fila * TILE_SIZE + TILE_SIZE // 2
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.asustado = False
        self.tiempo_asustado = 0
        self.activo = True
        self.tiempo_desaparecido = 0
        self.ojos_solo = False
        self.velocidad = VEL_FANTASMA
        self.timer_salida = self.salida_delay_inicial

    def render(self, surface):
        if self.ojos_solo:
            self._render_ojos(surface)
            return
        if not self.activo:
            return
        # Parpadeo mientras espera para salir
        if self.timer_salida > 0:
            if (self.timer_salida // 15) % 2 == 0:
                return

        color = ASUSTADO_COLOR if self.asustado else self.color
        x, y = self.x, self.y
        r = self.radio

        if self.asustado and self.tiempo_asustado < 120:
            if (self.tiempo_asustado // 15) % 2 == 0:
                color = BLANCO

        pygame.draw.circle(surface, color, (x, y - 1), r)
        pygame.draw.rect(surface, color, (x - r, y - 1, r * 2, r + 1))

        onda_r = r // 3
        for i in range(3):
            ox = x - r + onda_r + i * (r * 2 // 3)
            oy = y + r
            pygame.draw.circle(surface, color, (ox, oy), onda_r)

        if self.asustado:
            pygame.draw.circle(surface, BLANCO, (x - 4, y - 3), 2)
            pygame.draw.circle(surface, BLANCO, (x + 4, y - 3), 2)
        else:
            self._render_ojos_internos(surface, x, y)

    def _render_ojos(self, surface):
        self._render_ojos_internos(surface, self.x, self.y)

    def _render_ojos_internos(self, surface, x, y):
        dx, dy = self.direccion
        for ox in [-5, 5]:
            pygame.draw.ellipse(surface, BLANCO, (x + ox - 3, y - 6, 6, 7))
            pygame.draw.circle(
                surface, PUPILA_COLOR,
                (x + ox + dx * 2, y - 2 + dy * 2), 2)