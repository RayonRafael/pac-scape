import pygame
import sys
from constantes import *
from mapa import Mapa
from pacman import PacMan
from fantasma import Fantasma
from ia import ia_blinky, ia_pinky, ia_inky, ia_clyde, ia_asustado


def colisionan(e1, e2, radio=TILE_SIZE * 0.7):
    dx = e1.x - e2.x
    dy = e1.y - e2.y
    return (dx * dx + dy * dy) < radio * radio


def dibujar_hud(pantalla, fuente, pacman, mapa, power_timer):
    y_base = MAPA_FILAS * TILE_SIZE
    pygame.draw.rect(pantalla, HUD_BG, (0, y_base, ANCHO, HUD_ALTO))
    pygame.draw.line(pantalla, AZUL_PARED, (0, y_base), (ANCHO, y_base), 2)

    txt = fuente.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
    pantalla.blit(txt, (16, y_base + 4))

    txt = fuente.render("P1:WASD  P2:Arrows", True, (70, 70, 110))
    pantalla.blit(txt, (ANCHO // 2 - 95, y_base + 4))

    txt = fuente.render(f"Rest: {mapa.puntos_restantes}", True, HUD_TEXTO)
    pantalla.blit(txt, (ANCHO - 140, y_base + 4))

    for i in range(pacman.vidas):
        lx = 16 + i * 28
        ly = y_base + 32
        pygame.draw.circle(pantalla, AMARILLO, (lx, ly), 7)
        pygame.draw.polygon(pantalla, NEGRO, [
            (lx, ly), (lx + 9, ly - 3), (lx + 9, ly + 3)])

    if power_timer > 0:
        txt = fuente.render("POWER!", True, AMARILLO)
        pantalla.blit(txt, (ANCHO - 110, y_base + 28))


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pac-Scape")
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 28)
    fuente_grande = pygame.font.Font(None, 56)

    mapa = Mapa()
    pacman = PacMan()

    fantasmas = [
        Fantasma(*BLINKY_INICIO, VEL_FANTASMA, BLINKY_COLOR, "Blinky"),
        Fantasma(*PINKY_INICIO, VEL_FANTASMA, PINKY_COLOR, "Pinky"),
        Fantasma(*INKY_INICIO, VEL_FANTASMA, INKY_COLOR, "Inky"),
        Fantasma(*CLYDE_INICIO, VEL_FANTASMA, CLYDE_COLOR, "Clyde"),
    ]
    blinky, pinky, inky, clyde = fantasmas

    # Esquina de Clyde (esquina inferior izquierda del mapa)
    CLYDE_ESQUINA = (1, 29)

    estado = ESTADO_JUGANDO
    streak_comer = 0
    power_timer = 0

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False
                if evento.key == pygame.K_r and estado in (ESTADO_GAME_OVER, ESTADO_VICTORIA):
                    mapa = Mapa()
                    pacman.reiniciar()
                    for f in fantasmas:
                        f.reiniciar()
                    estado = ESTADO_JUGANDO
                    streak_comer = 0
                    power_timer = 0

        if estado == ESTADO_JUGANDO:
            teclas = pygame.key.get_pressed()

            # P1 -> Blinky (WASD)
            if teclas[pygame.K_w]:
                blinky.direccion_siguiente = ARRIBA
            elif teclas[pygame.K_s]:
                blinky.direccion_siguiente = ABAJO
            elif teclas[pygame.K_a]:
                blinky.direccion_siguiente = IZQUIERDA
            elif teclas[pygame.K_d]:
                blinky.direccion_siguiente = DERECHA

            # P2 -> Pinky (Flechas)
            if teclas[pygame.K_UP]:
                pinky.direccion_siguiente = ARRIBA
            elif teclas[pygame.K_DOWN]:
                pinky.direccion_siguiente = ABAJO
            elif teclas[pygame.K_LEFT]:
                pinky.direccion_siguiente = IZQUIERDA
            elif teclas[pygame.K_RIGHT]:
                pinky.direccion_siguiente = DERECHA

            # IA Inky — flanqueador (usa posicion de Blinky)
            if inky.asustado:
                ia_asustado(inky, pacman.tile_col, pacman.tile_fila, mapa)
            else:
                ia_inky(inky, mapa,
                        pacman.tile_col, pacman.tile_fila,
                        pacman.direccion,
                        blinky.tile_col, blinky.tile_fila)

            # IA Clyde — cobarde
            if clyde.asustado:
                ia_asustado(clyde, pacman.tile_col, pacman.tile_fila, mapa)
            else:
                ia_clyde(clyde, mapa,
                         pacman.tile_col, pacman.tile_fila,
                         *CLYDE_ESQUINA)

            # Updates
            pacman.update(mapa)
            for f in fantasmas:
                f.update(mapa)

            # Power mode
            if pacman.activar_power:
                pacman.activar_power = False
                for f in fantasmas:
                    f.poner_asustado(TIEMPO_ASUSTADO)
                streak_comer = 0
                power_timer = TIEMPO_ASUSTADO

            if power_timer > 0:
                power_timer -= 1

            # Colisiones
            for f in fantasmas:
                if not f.activo:
                    continue
                if not colisionan(pacman, f):
                    continue
                if f.asustado:
                    pts = FANTASMA_PTS[min(streak_comer, len(FANTASMA_PTS) - 1)]
                    pacman.puntuacion += pts
                    f.ser_comido()
                    streak_comer += 1
                elif not pacman.invincible:
                    pacman.vidas -= 1
                    if pacman.vidas <= 0:
                        estado = ESTADO_GAME_OVER
                    else:
                        pacman.reiniciar_posicion()
                        for g in fantasmas:
                            g.reiniciar()
                        power_timer = 0
                    break

            if mapa.puntos_restantes <= 0:
                estado = ESTADO_VICTORIA

        # ---- Render ----
        pantalla.fill(NEGRO)
        mapa.render(pantalla)
        pacman.render(pantalla)
        for f in fantasmas:
            f.render(pantalla)
        dibujar_hud(pantalla, fuente, pacman, mapa, power_timer)

        cx = ANCHO // 2
        cy = MAPA_FILAS * TILE_SIZE // 2

        if estado == ESTADO_GAME_OVER:
            overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
            overlay.set_alpha(150)
            overlay.fill(NEGRO)
            pantalla.blit(overlay, (0, 0))
            txt = fuente_grande.render("GAME OVER", True, (255, 0, 0))
            pantalla.blit(txt, txt.get_rect(center=(cx, cy)))
            txt2 = fuente.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
            pantalla.blit(txt2, txt2.get_rect(center=(cx, cy + 40)))
            txt3 = fuente.render("Presiona R para reiniciar", True, (150, 150, 150))
            pantalla.blit(txt3, txt3.get_rect(center=(cx, cy + 70)))

        if estado == ESTADO_VICTORIA:
            overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
            overlay.set_alpha(150)
            overlay.fill(NEGRO)
            pantalla.blit(overlay, (0, 0))
            txt = fuente_grande.render("VICTORIA!", True, AMARILLO)
            pantalla.blit(txt, txt.get_rect(center=(cx, cy)))
            txt2 = fuente.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
            pantalla.blit(txt2, txt2.get_rect(center=(cx, cy + 40)))
            txt3 = fuente.render("Presiona R para reiniciar", True, (150, 150, 150))
            pantalla.blit(txt3, txt3.get_rect(center=(cx, cy + 70)))

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()