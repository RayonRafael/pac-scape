# ============================================================
# pacman.py
# ============================================================
# Define a Pac-Man: el personaje que se come los puntos.
# Hereda de Entidad (movimiento base) y agrega:
#   - Puntuacion y vidas
#   - Boca animada (se abre/cierra al moverse)
#   - Comer puntos y power pellets
#   - Activar power mode
#   - Invencibilidad parpadeante al reaparecer
#   - Animacion de muerte (boca se abre, cuerpo se encoge)
#   - Grid de peligro (para la IA maestra)
# ============================================================

import pygame
import math
from entidad import Entidad
from constantes import *


class PacMan(Entidad):
    """El jugador principal controlado por IA."""

    def __init__(self, col=14, fila=23, velocidad=VEL_PACMAN):
        super().__init__(col, fila, velocidad)

        # Pac-Man empieza mirando a la izquierda (como en el original)
        self.direccion = IZQUIERDA

        self.puntuacion = 0      # Puntos acumulados en esta partida
        self.vidas = 3           # Vidas restantes
        self.frame_boca = 0      # Contador para la animacion de la boca
        self.radio = TILE_SIZE // 2 - 1  # Tamano del circulo de Pac-Man

        # Senales que main.py lee para activar sonidos y power mode.
        # Pac-Man no activa el power mode directamente; solo dice
        # "comi un power pellet" y main.py se encarga del resto.
        self.activar_power = False   # True si acaba de comer un power pellet
        self.comio_punto = False     # True si acaba de comer un punto
        self.comio_power = False     # True si acaba de comer un power pellet

        # Invencibilidad: Pac-Man parpadea y no puede morir
        # durante unos segundos despues de reaparecer.
        self.invincible = False
        self.tiempo_invencible = 0

        # Dificultad de la IA (constante de constantes.py)
        self.dificultad = DIFIC_TONTA

        # Grid de peligro para la IA maestra.
        # Es una grilla del mismo tamano que el mapa donde cada celda
        # tiene un valor de 0.0 (seguro) a 1.0 (peligroso).
        # Se incrementa cuando Pac-Man muere en esa zona y se decae
        # lentamente con el tiempo.
        self.peligro_grid = [[0.0] * MAPA_COLS for _ in range(MAPA_FILAS)]

        # Animacion de muerte
        self.muriendo = False      # True durante la animacion de muerte
        self.frame_muerte = 0      # Contador de frames de la animacion

    def update(self, mapa):
        """
        Actualiza Pac-Man cada frame:
        1) Resetear senales de comer
        2) Si esta muriendo, solo avanzar la animacion
        3) Actualizar invencibilidad
        4) Decaer el grid de peligro (IA maestra)
        5) Mover (usando la logica de Entidad)
        6) Comer puntos en la celda actual
        7) Animar la boca
        """

        # Resetear senales (solo son True durante 1 frame)
        self.comio_punto = False
        self.comio_power = False

        # Si esta muriendo, solo avanzar la animacion (no se mueve)
        if self.muriendo:
            self.frame_muerte += 1
            return

        # Actualizar invencibilidad
        if self.invincible:
            self.tiempo_invencible -= 1
            if self.tiempo_invencible <= 0:
                self.invincible = False

        # Decaimiento del grid de peligro (solo para IA maestra)
        # Cada frame, el peligro de todas las celdas baja un 0.2%.
        # Esto hace que las zonas peligrosas "se olviden" con el tiempo.
        if self.dificultad == DIFIC_MAESTRA:
            for f in range(MAPA_FILAS):
                for c in range(MAPA_COLS):
                    self.peligro_grid[f][c] *= 0.998

        # Mover usando la logica de la clase padre (Entidad)
        super().update(mapa)

        # Comer punto/power pellet en la celda actual
        puntos = mapa.comer(self.tile_col, self.tile_fila)
        self.puntuacion += puntos

        # Activar senales para que main.py sepa que paso algo
        if puntos > 0:
            self.comio_punto = True
        if puntos == POWER_PTS:
            self.comio_power = True
            self.activar_power = True

        # Animar la boca: incrementar el frame solo cuando se mueve
        if self.direccion != QUIETO:
            self.frame_boca = (self.frame_boca + 1) % 20

    def iniciar_muerte(self):
        """Activa la animacion de muerte. Pac-Man deja de moverse."""
        self.muriendo = True
        self.frame_muerte = 0
        self.direccion = QUIETO

    def registrar_muerte(self):
        """
        Llamar cuando Pac-Man muere. Incrementa el valor de peligro
        en una zona de 9x9 tiles alrededor de donde murio.
        Esto le enseña a la IA maestra a evitar esa zona.
        """
        for df in range(-4, 5):      # -4 a +4 filas
            for dc in range(-4, 5):  # -4 a +4 columnas
                nf = self.tile_fila + df
                nc = self.tile_col + dc
                if 0 <= nf < MAPA_FILAS and 0 <= nc < MAPA_COLS:
                    # Cuanto mas lejos del centro, menor el incremento
                    dist = abs(df) + abs(dc)
                    inc = max(0, 0.6 - dist * 0.1)
                    self.peligro_grid[nf][nc] = min(
                        1.0, self.peligro_grid[nf][nc] + inc)

    def reiniciar_posicion(self):
        """Reubica a Pac-Man en su posicion inicial (tras perder una vida)."""
        self.x = PACMAN_INICIO[0] * TILE_SIZE + TILE_SIZE // 2
        self.y = PACMAN_INICIO[1] * TILE_SIZE + TILE_SIZE // 2
        self.direccion = IZQUIERDA
        self.direccion_siguiente = QUIETO
        self.invincible = False
        self.tiempo_invencible = 0
        self.muriendo = False
        self.frame_muerte = 0

    def reiniciar(self):
        """Reinicia TODO (cuando se empieza una partida nueva)."""
        self.reiniciar_posicion()
        self.puntuacion = 0
        self.vidas = 3
        self.activar_power = False
        self.invincible = False
        self.tiempo_invencible = 0
        # Limpiar el grid de peligro
        self.peligro_grid = [[0.0] * MAPA_COLS for _ in range(MAPA_FILAS)]

    def render(self, surface):
        """Dibuja a Pac-Man en pantalla."""

        # Si esta muriendo, usar la animacion de muerte
        if self.muriendo:
            self._render_muerte(surface)
            return

        # Si es invencible, parpadear (desaparece cada 5 frames)
        if self.invincible and (self.tiempo_invencible // 5) % 2 == 0:
            return  # No dibujar este frame (efecto parpadeo)

        # Cuerpo: circulo amarillo
        pygame.draw.circle(surface, AMARILLO, (self.x, self.y), self.radio)

        # Boca: triangulo negro que apunta en la direccion de movimiento
        dx, dy = self.direccion
        if dx != 0 or dy != 0:
            # Calcular angulo de la boca segun la direccion
            angulo = math.atan2(-dy, dx)  # atan2 da el angulo en radianes

            # La boca se abre y cierra usando una onda sinusoidal
            boca_max = 0.5  # Apertura maxima en radianes
            boca = boca_max * abs(math.sin(self.frame_boca * math.pi / 10))

            # Dos puntos que forman los "labios" de la boca
            ext = self.radio + 2  # Que sobrepase el circulo
            p2 = (self.x + int(ext * math.cos(angulo - boca)),
                  self.y - int(ext * math.sin(angulo - boca)))
            p3 = (self.x + int(ext * math.cos(angulo + boca)),
                  self.y - int(ext * math.sin(angulo + boca)))

            # Dibujar el triangulo de la boca (centro + dos labios)
            pygame.draw.polygon(surface, NEGRO, [(self.x, self.y), p2, p3])

    def _render_muerte(self, surface):
        """
        Animacion de muerte de Pac-Man:
        - La boca se abre cada vez mas hasta que el cuerpo desaparece
        - El cuerpo se encoge simultaneamente
        - Dura TIEMPO_MURIENDO frames (1.5 segundos)
        """
        # Progreso de 0.0 (inicio) a 1.0 (fin)
        progreso = self.frame_muerte / TIEMPO_MURIENDO

        # Cuando el progreso llega a 0.9, Pac-Man desaparece
        if progreso >= 0.9:
            return

        # El radio se reduce a medida que avanza la animacion
        r = max(1, int(self.radio * (1.0 - progreso * 0.9)))

        # Dibujar circulo que se encoge
        pygame.draw.circle(surface, AMARILLO, (self.x, self.y), r)

        # La boca se abre progresivamente (de 0.1*pi a 0.95*pi radianes)
        angulo_apertura = 0.1 * math.pi + progreso * 0.85 * math.pi
        ext = r + 2
        p2 = (self.x + int(ext * math.cos(-angulo_apertura)),
              self.y - int(ext * math.sin(-angulo_apertura)))
        p3 = (self.x + int(ext * math.cos(angulo_apertura)),
              self.y - int(ext * math.sin(angulo_apertura)))
        pygame.draw.polygon(surface, NEGRO, [(self.x, self.y), p2, p3])