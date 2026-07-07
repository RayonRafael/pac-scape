# ============================================================
# fantasma.py
# ============================================================
# Define a los 4 fantasmas: Blinky (rojo), Pinky (rosa),
# Inky (cian) y Clyde (naranja).
# Heredan de Entidad (movimiento base) y agregan:
#   - Estado asustado (azul, huye de Pac-Man)
#   - Estado ojos-solo (cuando es comido, vuelve a la casa)
#   - Parpadeo cuando el power mode esta por terminar
#   - Render con forma de fantasma (semicirculo + rectangulo + ondas)
#   - Ojos con pupilas que apuntan en la direccion de movimiento
# ============================================================

import pygame
from entidad import Entidad
from constantes import *


class Fantasma(Entidad):
    """Fantasma con estados: normal, asustado, ojos-solo."""

    def __init__(self, col, fila, velocidad, color, nombre):
        super().__init__(col, fila, velocidad)
        self.color = color           # Color original del fantasma
        self.nombre = nombre         # Nombre (para debug)
        self.inicio_col = col        # Columna de inicio (para respawn)
        self.inicio_fila = fila      # Fila de inicio (para respawn)
        self.radio = TILE_SIZE // 2 - 1  # Tamano del fantasma

        # Estados del fantasma
        self.asustado = False        # True cuando Pac-Man come un power pellet
        self.tiempo_asustado = 0     # Frames restantes de estado asustado
        self.activo = True           # False si fue comido y esta desaparecido
        self.tiempo_desaparecido = 0 # Frames para reaparecer (solo fantasmas IA)
        self.ojos_solo = False       # True si fue comido: solo quedan los ojos

    def update(self, mapa):
        """
        Actualiza el fantasma cada frame. Hay 3 modos:
        1) Ojos-solo: vuelve rapido a la casa de fantasmas
        2) Desaparecido: cuenta regresiva para reaparecer
        3) Normal/asustado: se mueve con IA o jugador
        """

        # --- MODO OJOS-SOLO ---
        # El fantasma fue comido, solo quedan los ojos.
        # Se mueven rapido de vuelta a la casa de fantasmas.
        if self.ojos_solo:
            self._ir_a_casa(mapa)  # Calcular direccion hacia la casa
            super().update(mapa, es_fantasma=True)  # Moverse rapido
            # Si llego a la casa, reaparecer como fantasma normal
            if (self.tile_col == self.inicio_col
                    and self.tile_fila == self.inicio_fila
                    and self.en_centro_tile()):
                self._reaparecer_ojos()
            return

        # --- MODO DESAPARECIDO ---
        # El fantasma fue comido y esta invisible (solo fantasmas IA).
        # Cuenta regresiva para reaparecer en la casa.
        if not self.activo:
            self.tiempo_desaparecido -= 1
            if self.tiempo_desaparecido <= 0:
                self.reaparecer()
            return

        # --- MODO NORMAL/ASUSTADO ---
        super().update(mapa, es_fantasma=True)

        # Actualizar estado asustado
        if self.asustado:
            self.tiempo_asustado -= 1
            if self.tiempo_asustado <= 0:
                self.asustado = False  # Se acabo el power mode

    def _ir_a_casa(self, mapa):
        """
        Calcula la direccion para ir hacia la casa de fantasmas.
        Elige la casilla adyacente que mas se acerque al inicio.
        """
        if not self.en_centro_tile():
            return
        dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
        reverso = (-self.direccion[0], -self.direccion[1])
        mejor_dir = None
        mejor_dist = float('inf')
        for d in dirs:
            # No dar la vuelta si hay otra opcion
            if d == reverso and len(dirs) > 1:
                continue
            nc = Entidad._wrap_col(self.tile_col + d[0])
            nf = self.tile_fila + d[1]
            if not mapa.es_transitable(nc, nf, es_fantasma=True):
                continue
            # Distancia al punto de inicio (cuadrado, sin raiz)
            dist = (nc - self.inicio_col) ** 2 + (nf - self.inicio_fila) ** 2
            if dist < mejor_dist:
                mejor_dist = dist
                mejor_dir = d
        if mejor_dir:
            self.direccion_siguiente = mejor_dir

    def _reaparecer_ojos(self):
        """Cuando los ojos llegan a la casa, el fantasma vuelve a la normalidad."""
        self.x = self.inicio_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.inicio_fila * TILE_SIZE + TILE_SIZE // 2
        self.ojos_solo = False
        self.asustado = False
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.velocidad = VEL_FANTASMA  # Vuelve a velocidad normal

    def poner_asustado(self, duracion):
        """Activa el estado asustado (fantasma azul)."""
        if not self.activo or self.ojos_solo:
            return
        self.asustado = True
        self.tiempo_asustado = duracion
        # Al ponerse asustado, invierte su direccion (como en el original)
        if self.direccion != QUIETO:
            self.direccion = (-self.direccion[0], -self.direccion[1])

    def ser_comido(self):
        """
        Pac-Man se comio al fantasma.
        Solo quedan los ojos que vuelven a la casa a doble velocidad.
        """
        self.ojos_solo = True
        self.asustado = False
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.velocidad = VEL_FANTASMA * 2  # Ojos van al doble de rapido

    def reaparecer(self):
        """Reaparece en la casa de fantasmas (usado por fantasmas IA)."""
        self.x = self.inicio_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.inicio_fila * TILE_SIZE + TILE_SIZE // 2
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO
        self.asustado = False
        self.ojos_solo = False
        self.activo = True
        self.velocidad = VEL_FANTASMA

    def reiniciar(self):
        """Reinicia completamente el fantasma (nueva partida)."""
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

    def render(self, surface):
        """Dibuja el fantasma en pantalla."""

        # Si solo quedan los ojos, dibujar solo ojos
        if self.ojos_solo:
            self._render_ojos(surface)
            return

        # Si esta desaparecido (comido, esperando respawn), no dibujar nada
        if not self.activo:
            return

        # Color: azul si esta asustado, color original si no
        color = ASUSTADO_COLOR if self.asustado else self.color
        x, y = self.x, self.y
        r = self.radio

        # Parpadeo blanco/azul cuando el power mode esta por terminar
        # (ultimos 2 segundos = 120 frames)
        if self.asustado and self.tiempo_asustado < 120:
            if (self.tiempo_asustado // 15) % 2 == 0:
                color = BLANCO  # Alterna entre azul y blanco

        # Cuerpo: semicirculo superior + rectangulo inferior
        pygame.draw.circle(surface, color, (x, y - 1), r)
        pygame.draw.rect(surface, color, (x - r, y - 1, r * 2, r + 1))

        # Ondas en la base (3 circulos que dan forma de "falda")
        onda_r = r // 3
        for i in range(3):
            ox = x - r + onda_r + i * (r * 2 // 3)
            oy = y + r
            pygame.draw.circle(surface, color, (ox, oy), onda_r)

        # Ojos
        if self.asustado:
            # Ojos asustados: dos puntos blancos simples
            pygame.draw.circle(surface, BLANCO, (x - 4, y - 3), 2)
            pygame.draw.circle(surface, BLANCO, (x + 4, y - 3), 2)
        else:
            # Ojos normales: oval blanco con pupila que mira la direccion
            self._render_ojos_internos(surface, x, y)

    def _render_ojos(self, surface):
        """Dibuja solo los ojos (cuando el cuerpo fue comido)."""
        self._render_ojos_internos(surface, self.x, self.y)

    def _render_ojos_internos(self, surface, x, y):
        """
        Dibuja los ojos con pupilas.
        Las pupilas apuntan en la direccion de movimiento.
        """
        dx, dy = self.direccion
        for ox in [-5, 5]:  # Ojo izquierdo y derecho
            # Oval blanco (esclerotica)
            pygame.draw.ellipse(surface, BLANCO, (x + ox - 3, y - 6, 6, 7))
            # Pupila oscura que se desplaza segun la direccion
            pygame.draw.circle(
                surface, PUPILA_COLOR,
                (x + ox + dx * 2, y - 2 + dy * 2), 2)