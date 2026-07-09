"""
Logica de los Fantasmas.
Maneja sus estados (Normal, Asustado, Ojos), su animacion, y la nueva habilidad de Dash (Aceleracion).
"""
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
        self.es_jugador = False  # Nuevo flag para control manual
        self.cooldown_habilidad = 0
        self.max_cooldown = 480  # 8 segundos a 60 FPS

    @property
    def esperando(self):
        return self.timer_salida > 0

    def update(self, mapa):
        if self.cooldown_habilidad > 0:
            self.cooldown_habilidad -= 1

        if self.timer_salida > 0:
            self.timer_salida -= 1
            return

        if self.ojos_solo:
            # Siempre usamos _ir_a_casa para los ojitos para que sea automatico y no se atasque
            self._ir_a_casa(mapa)
            super().update(mapa, es_fantasma=True)
            
            # Ampliamos un poco el margen para revivir por si el jugador se pasa de largo
            if (abs(self.tile_col - self.inicio_col) <= 1
                    and abs(self.tile_fila - self.inicio_fila) <= 1
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

    def usar_habilidad(self, mapa):
        """Embestida (Dash): avanza hasta 3 tiles en la direccion actual si es posible."""
        if not self.es_jugador or not self.activo or self.ojos_solo or self.asustado or self.esperando:
            return False
        if self.cooldown_habilidad > 0:
            return False
            
        dx, dy = self.direccion
        if (dx, dy) == (0, 0):
            return False
            
        # Avanzar tile por tile
        tiles_dash = 3
        for _ in range(tiles_dash):
            nx = Entidad._wrap_col(self.tile_col + dx)
            ny = self.tile_fila + dy
            if mapa.es_transitable(nx, ny, es_fantasma=True):
                self.x += dx * TILE_SIZE
                self.y += dy * TILE_SIZE
            else:
                break
                
        # Reiniciar cooldown a 8 segundos
        self.cooldown_habilidad = self.max_cooldown
        return True

    def _ir_a_casa(self, mapa):
        if not self.en_centro_tile():
            return
        
        # Algoritmo BFS para que la IA nunca se atasque en el laberinto
        visitados = set()
        cola = [(self.tile_col, self.tile_fila, [])]
        
        mejor_dir = None
        while cola:
            cx, cy, path = cola.pop(0)
            if cx == self.inicio_col and cy == self.inicio_fila:
                if path:
                    mejor_dir = path[0]
                break
                
            if (cx, cy) in visitados:
                continue
            visitados.add((cx, cy))
            
            for d in [ARRIBA, ABAJO, IZQUIERDA, DERECHA]:
                nx = Entidad._wrap_col(cx + d[0])
                ny = cy + d[1]
                if mapa.es_transitable(nx, ny, es_fantasma=True):
                    cola.append((nx, ny, path + [d]))
                    
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
        self.cooldown_habilidad = 0

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