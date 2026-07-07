import pygame
import sys
from constantes import *
from mapa import Mapa
from pacman import PacMan


def dibujar_hud(pantalla, fuente, pacman, mapa):
    y_base = MAPA_FILAS * TILE_SIZE
    pygame.draw.rect(pantalla, HUD_BG, (0, y_base, ANCHO, HUD_ALTO))
    pygame.draw.line(pantalla, AZUL_PARED, (0, y_base), (ANCHO, y_base), 2)
    txt_pts = fuente.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
    pantalla.blit(txt_pts, (16, y_base + 6))
    txt_rem = fuente.render(f"Restantes: {mapa.puntos_restantes}", True, HUD_TEXTO)
    pantalla.blit(txt_rem, (ANCHO - 230, y_base + 6))
    txt_ctrl = fuente.render("W A S D", True, (70, 70, 110))
    pantalla.blit(txt_ctrl, (ANCHO // 2 - 40, y_base + 6))
    for i in range(pacman.vidas):
        lx = 16 + i * 28
        ly = y_base + 36
        pygame.draw.circle(pantalla, AMARILLO, (lx, ly), 7)
        pygame.draw.polygon(pantalla, NEGRO, [
            (lx, ly), (lx + 9, ly - 3), (lx + 9, ly + 3)
        ])


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pac-Scape")
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 28)
    mapa = Mapa()
    pacman = PacMan()
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_w]:
            pacman.direccion_siguiente = ARRIBA
        elif teclas[pygame.K_s]:
            pacman.direccion_siguiente = ABAJO
        elif teclas[pygame.K_a]:
            pacman.direccion_siguiente = IZQUIERDA
        elif teclas[pygame.K_d]:
            pacman.direccion_siguiente = DERECHA
        pacman.update(mapa)
        if mapa.puntos_restantes <= 0:
            print(f"Victoria  Puntuacion final: {pacman.puntuacion}")
            corriendo = False
        pantalla.fill(NEGRO)
        mapa.render(pantalla)
        pacman.render(pantalla)
        dibujar_hud(pantalla, fuente, pacman, mapa)
        pygame.display.flip()
        reloj.tick(FPS)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()