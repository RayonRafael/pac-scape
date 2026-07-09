"""
Define objetos menores interactivos dentro del juego, 
como las Frutas que dan puntos extra y los PopUps flotantes de texto.
"""
import pygame
from constantes import *

class PopUp:
    def __init__(self, x, y, texto, color):
        self.x = x
        self.y = y
        self.texto = texto
        self.color = color
        self.timer = POPUP_DURACION

    def update(self):
        self.timer -= 1
        self.y -= 0.5

    @property
    def activo(self):
        return self.timer > 0

    def render(self, surface, fuente):
        txt = fuente.render(self.texto, True, self.color)
        rect = txt.get_rect(center=(int(self.x), int(self.y)))
        bg = pygame.Surface((rect.width + 10, rect.height + 6), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        
        if self.timer > POPUP_DURACION - 10:
            escala = 1.0 + (self.timer - (POPUP_DURACION - 10)) * 0.05
            w = int(bg.get_width() * escala)
            h = int(bg.get_height() * escala)
            bg = pygame.transform.scale(bg, (w, h))
            txt = pygame.transform.scale(txt, (int(txt.get_width() * escala), int(txt.get_height() * escala)))
        
        bg_rect = bg.get_rect(center=(int(self.x), int(self.y)))
        rect = txt.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(bg, bg_rect)
        surface.blit(txt, rect)

class Fruta:
    def __init__(self, nombre, color, puntos, col, fila):
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = fila * TILE_SIZE + TILE_SIZE // 2
        self.nombre = nombre
        self.color = color
        self.puntos = puntos
        self.timer = FRUTA_DURACION
        self.activa = True

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.activa = False

    def render(self, surface):
        if not self.activa:
            return
        r = TILE_SIZE // 2 - 3
        pygame.draw.circle(surface, self.color, (self.x, self.y), r)
        pygame.draw.line(surface, (0, 100, 0),
                         (self.x, self.y - r),
                         (self.x + 2, self.y - r - 4), 2)
        sr = max(1, r // 4)
        pygame.draw.circle(surface, (255, 255, 255),
                           (self.x - r // 3, self.y - r // 3), sr)
        if self.timer < 120 and (self.timer // 10) % 2 == 0:
            pygame.draw.circle(surface, NEGRO, (self.x, self.y), r + 1)
