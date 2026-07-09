import pygame
import random
import math
from constantes import *

class Particula:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        # Velocidad radial aleatoria
        angulo = random.uniform(0, 2 * math.pi)
        velocidad = random.uniform(1.0, 3.5)
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad
        self.vida = random.randint(15, 30)
        self.vida_max = self.vida
        self.tamano = random.uniform(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vida -= 1

    def render(self, surface):
        if self.vida > 0:
            alpha = int((self.vida / self.vida_max) * 255)
            # Aproximar alpha con oscurecimiento
            r = int(self.color[0] * (alpha / 255))
            g = int(self.color[1] * (alpha / 255))
            b = int(self.color[2] * (alpha / 255))
            t = int(self.tamano * (self.vida / self.vida_max))
            if t > 0:
                pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), t)

class GestorParticulas:
    def __init__(self):
        self.particulas = []

    def emitir(self, x, y, color, cantidad=4):
        for _ in range(cantidad):
            self.particulas.append(Particula(x, y, color))

    def update(self):
        for p in self.particulas:
            p.update()
        self.particulas = [p for p in self.particulas if p.vida > 0]

    def render(self, surface):
        for p in self.particulas:
            p.render(surface)

def dibujar_grid_fondo(surface, ancho, alto, color_linea, tamano_celda=40):
    """
    Dibuja un grid estilo retro en toda la superficie que hace panning animado.
    """
    t = pygame.time.get_ticks()
    offset_x = (t / 30.0) % tamano_celda
    offset_y = (t / 30.0) % tamano_celda

    # Fondo base
    surface.fill(FONDO_JUEGO)

    # Lineas verticales
    x = -tamano_celda + offset_x
    while x < ancho:
        pygame.draw.line(surface, color_linea, (int(x), 0), (int(x), alto), 1)
        x += tamano_celda

    # Lineas horizontales
    y = -tamano_celda + offset_y
    while y < alto:
        pygame.draw.line(surface, color_linea, (0, int(y)), (ancho, int(y)), 1)
        y += tamano_celda

def dibujar_aura(surface, cx, cy, radio, color, alpha_max):
    """
    Dibuja un circulo con gradiente alpha radial para simular brillo/aura.
    Como pygame no soporta gradientes circulares nativos facilmente,
    creamos una mini-superficie temporal y dibujamos circulos concentricos.
    """
    temp = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
    pasos = 5
    for i in range(pasos):
        r = radio - (radio / pasos) * i
        alpha = int(alpha_max * (i + 1) / pasos)
        pygame.draw.circle(temp, (*color, alpha), (radio, radio), int(r))
    surface.blit(temp, (int(cx) - radio, int(cy) - radio))

def construir_paredes_retro(self):
    """
    Reemplazo (monkey-patch) para Mapa._construir_paredes.
    Dibuja paredes con gradientes o brillo interno, pero deja el resto (caminos)
    transparente para que el grid retro del fondo se vea.
    """
    # Hacer que la cache soporte alpha (transparencia)
    self._cache_paredes = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE), pygame.SRCALPHA)
    self._cache_paredes.fill((0, 0, 0, 0))  # Fondo transparente
    
    s = self._cache_paredes
    borde = PARED_BRILLO
    relleno = PARED_RELLENO
    g = 2  # grosor de la linea del borde

    for f in range(MAPA_FILAS):
        for c in range(MAPA_COLS):
            if self.grid[f][c] != PARED:
                continue

            x, y = c * TILE_SIZE, f * TILE_SIZE

            # 1) Relleno base solido con un toque neon
            pygame.draw.rect(s, relleno, (x, y, TILE_SIZE, TILE_SIZE))

            # 2) Gradiente / Sombra interior simulada dibujando rectangulos mas pequeños oscuros
            # Esto da un efecto de bloque 3D o de tubo iluminado
            offset = 4
            pygame.draw.rect(s, (5, 5, 20), (x + offset, y + offset, TILE_SIZE - offset*2, TILE_SIZE - offset*2))

            # 3) Bordes iluminados
            if f == 0 or self.grid[f - 1][c] != PARED:
                pygame.draw.line(s, borde, (x, y), (x + TILE_SIZE - 1, y), g)
            if f == MAPA_FILAS - 1 or self.grid[f + 1][c] != PARED:
                pygame.draw.line(s, borde, (x, y + TILE_SIZE - 1), (x + TILE_SIZE - 1, y + TILE_SIZE - 1), g)
            if c == 0 or self.grid[f][c - 1] != PARED:
                pygame.draw.line(s, borde, (x, y), (x, y + TILE_SIZE - 1), g)
            if c == MAPA_COLS - 1 or self.grid[f][c + 1] != PARED:
                pygame.draw.line(s, borde, (x + TILE_SIZE - 1, y), (x + TILE_SIZE - 1, y + TILE_SIZE - 1), g)
