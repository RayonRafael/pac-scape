import pygame
import sys
from constantes import *
from mapa import Mapa
from pacman import PacMan
from fantasma import Fantasma
from ia import (
    ia_pacman_tonta, ia_pacman_temerosa,
    ia_pacman_astuta, ia_pacman_maestra,
    ia_pinky, ia_inky, ia_clyde, ia_asustado,
)
from sonidos import Sonidos


def colisionan(e1, e2, radio=TILE_SIZE * 0.7):
    dx = e1.x - e2.x
    dy = e1.y - e2.y
    return (dx * dx + dy * dy) < radio * radio


def format_tiempo(frames):
    s = frames // 60
    return f"{s // 60}:{s % 60:02d}"


def crear_juego(dificultad):
    mapa = Mapa()
    pacman = PacMan()
    pacman.dificultad = dificultad
    fantasmas = [
        Fantasma(*BLINKY_INICIO, VEL_FANTASMA, BLINKY_COLOR, "Blinky"),
        Fantasma(*PINKY_INICIO, VEL_FANTASMA, PINKY_COLOR, "Pinky"),
        Fantasma(*INKY_INICIO, VEL_FANTASMA, INKY_COLOR, "Inky"),
        Fantasma(*CLYDE_INICIO, VEL_FANTASMA, CLYDE_COLOR, "Clyde"),
    ]
    return mapa, pacman, fantasmas


def stats_vacias(mapa):
    return {
        'dots': 0, 'power_pellets': 0,
        'fantasmas_comidos': 0,
        'tiempo_frames': 0,
        'total_dots': mapa.puntos_restantes,
    }


# ============================================================
# MENU PRINCIPAL
# ============================================================

def dibujar_menu(pantalla, fuente, fuente_grande, fuente_chica,
                 sel_dificultad, num_jugadores):
    pantalla.fill(NEGRO)
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2

    # Titulo
    txt = fuente_grande.render("PAC-SCAPE", True, AMARILLO)
    pantalla.blit(txt, txt.get_rect(center=(cx, cy - 150)))
    txt = fuente.render("4 Fantasmas vs Pac-Man IA", True, (150, 150, 180))
    pantalla.blit(txt, txt.get_rect(center=(cx, cy - 115)))

    pygame.draw.line(pantalla, AZUL_PARED,
                     (cx - 160, cy - 95), (cx + 160, cy - 95), 2)

    # Jugadores (A / D)
    y = cy - 72
    txt = fuente_chica.render("Jugadores  (A / D)", True, (120, 120, 140))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))
    y += 22
    if num_jugadores == 1:
        ptxt = "1 Jugador"
        pcol = (100, 200, 255)
    else:
        ptxt = "2 Jugadores"
        pcol = (255, 200, 100)
    txt = fuente.render(f"◄  {ptxt}  ►", True, pcol)
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))

    # Dificultad (W / S)
    y += 32
    txt = fuente_chica.render("Dificultad  (W / S)", True, (120, 120, 140))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))
    y += 18

    for i, nombre in enumerate(NOMBRES_DIFICULTAD):
        col = COLORES_DIFICULTAD[i]
        if i == sel_dificultad:
            rect = pygame.Rect(cx - 90, y - 3, 180, 26)
            pygame.draw.rect(pantalla, (30, 30, 60), rect, border_radius=5)
            pygame.draw.rect(pantalla, col, rect, 2, border_radius=5)
            txt = fuente_chica.render(f"  {nombre}", True, col)
            pantalla.blit(txt, (cx - 82, y + 2))
        else:
            txt = fuente_chica.render(f"  {nombre}", True, (60, 60, 80))
            pantalla.blit(txt, (cx - 82, y + 2))
        y += 26

    y += 4
    txt = fuente_chica.render(DESCRIPCIONES[sel_dificultad], True,
                              COLORES_DIFICULTAD[sel_dificultad])
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))

    pygame.draw.line(pantalla, AZUL_PARED,
                     (cx - 160, y + 18), (cx + 160, y + 18), 2)

    # Controles
    y += 35
    if num_jugadores == 1:
        lineas = [
            ("WASD → Blinky (rojo)", BLINKY_COLOR),
            ("Pinky, Inky y Clyde son IA", (120, 120, 140)),
        ]
    else:
        lineas = [
            ("P1: WASD → Blinky (rojo)", BLINKY_COLOR),
            ("P2: Flechas → Pinky (rosa)", PINKY_COLOR),
            ("Inky y Clyde siempre son IA", (120, 120, 140)),
        ]
    for texto, color in lineas:
        txt = fuente_chica.render(texto, True, color)
        pantalla.blit(txt, txt.get_rect(center=(cx, y)))
        y += 20

    # Footer
    txt = fuente_chica.render(
        "W/S dificultad | A/D jugadores | ENTER jugar",
        True, (80, 80, 100))
    pantalla.blit(txt, txt.get_rect(center=(cx, cy + 170)))
    txt = fuente_chica.render("ESC: salir", True, (50, 50, 70))
    pantalla.blit(txt, txt.get_rect(center=(cx, cy + 190)))


# ============================================================
# PAUSA
# ============================================================

def dibujar_pausa(pantalla, fuente, fuente_grande, fuente_chica, seleccion):
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    pantalla.blit(overlay, (0, 0))

    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2

    txt = fuente_grande.render("PAUSA", True, BLANCO)
    pantalla.blit(txt, txt.get_rect(center=(cx, cy - 60)))

    y = cy - 5
    for i, opcion in enumerate(PAUSA_OPCIONES):
        if i == seleccion:
            col = AMARILLO
            txt = fuente.render(f">  {opcion}", True, col)
        else:
            col = (120, 120, 140)
            txt = fuente.render(f"   {opcion}", True, col)
        pantalla.blit(txt, txt.get_rect(center=(cx, y)))
        y += 36

    txt = fuente_chica.render(
        "W/S mover | ENTER confirmar | ESC reanudar",
        True, (80, 80, 100))
    pantalla.blit(txt, txt.get_rect(center=(cx, cy + 110)))


# ============================================================
# HUD
# ============================================================

def dibujar_hud(pantalla, fuente, fuente_chica, pacman, mapa,
                power_timer, dificultad, num_jugadores):
    y_base = MAPA_FILAS * TILE_SIZE
    pygame.draw.rect(pantalla, HUD_BG, (0, y_base, ANCHO, HUD_ALTO))
    pygame.draw.line(pantalla, AZUL_PARED, (0, y_base), (ANCHO, y_base), 2)

    txt = fuente.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
    pantalla.blit(txt, (16, y_base + 4))

    txt = fuente.render(f"Rest: {mapa.puntos_restantes}", True, HUD_TEXTO)
    pantalla.blit(txt, (ANCHO - 140, y_base + 4))

    txt = fuente_chica.render(
        f"{NOMBRES_DIFICULTAD[dificultad]}  |  {num_jugadores}J",
        True, COLORES_DIFICULTAD[dificultad])
    pantalla.blit(txt, (ANCHO // 2 - 35, y_base + 6))

    for i in range(pacman.vidas):
        lx = 16 + i * 28
        ly = y_base + 32
        pygame.draw.circle(pantalla, AMARILLO, (lx, ly), 7)
        pygame.draw.polygon(pantalla, NEGRO, [
            (lx, ly), (lx + 9, ly - 3), (lx + 9, ly + 3)])

    if power_timer > 0:
        bar_x = ANCHO - 120
        bar_y = y_base + 30
        bar_w = 100
        bar_h = 8
        ratio = power_timer / TIEMPO_ASUSTADO
        pygame.draw.rect(pantalla, (40, 40, 60),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(pantalla, AMARILLO,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h),
                         border_radius=4)


# ============================================================
# OVERLAYS
# ============================================================

def dibujar_ready(pantalla, fuente_grande):
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2
    txt = fuente_grande.render("READY!", True, AMARILLO)
    pantalla.blit(txt, txt.get_rect(center=(cx, cy + 20)))


def dibujar_stats(pantalla, fuente, fuente_chica, fuente_grande,
                  stats, pacman, num_jugadores, titulo, color_titulo):
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    pantalla.blit(overlay, (0, 0))

    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2

    txt = fuente_grande.render(titulo, True, color_titulo)
    pantalla.blit(txt, txt.get_rect(center=(cx, cy - 120)))

    y = cy - 65
    lineas = [
        (f"Puntos: {pacman.puntuacion}", BLANCO),
        (f"Dots: {stats['dots']}/{stats['total_dots']}",
         (180, 180, 200)),
        (f"Power pellets: {stats['power_pellets']}/4",
         (180, 180, 200)),
        (f"Fantasmas comidos: {stats['fantasmas_comidos']}",
         (180, 180, 200)),
        (f"Dificultad: {NOMBRES_DIFICULTAD[pacman.dificultad]}  |  "
         f"{num_jugadores}J",
         COLORES_DIFICULTAD[pacman.dificultad]),
        (f"Tiempo: {format_tiempo(stats['tiempo_frames'])}",
         (180, 180, 200)),
    ]
    for texto, color in lineas:
        txt = fuente_chica.render(texto, True, color)
        pantalla.blit(txt, txt.get_rect(center=(cx, y)))
        y += 24

    y += 12
    pygame.draw.line(pantalla, AZUL_PARED, (cx - 120, y), (cx + 120, y), 1)
    y += 15
    txt = fuente_chica.render("R: menu  |  ESC: salir", True, (100, 100, 120))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# MAIN
# ============================================================

def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Pac-Scape")
    reloj = pygame.time.Clock()
    fuente = pygame.font.Font(None, 28)
    fuente_grande = pygame.font.Font(None, 56)
    fuente_chica = pygame.font.Font(None, 22)
    sonidos = Sonidos()

    ias_pacman = {
        DIFIC_TONTA: ia_pacman_tonta,
        DIFIC_TEMEROSA: ia_pacman_temerosa,
        DIFIC_ASTUTA: ia_pacman_astuta,
        DIFIC_MAESTRA: ia_pacman_maestra,
    }
    CLYDE_ESQUINA = (1, 29)

    estado = ESTADO_MENU
    sel_dificultad = DIFIC_TONTA
    num_jugadores = 2
    dificultad = DIFIC_TONTA
    pausa_sel = 0

    mapa = pacman = fantasmas = None
    blinky = pinky = inky = clyde = None
    streak_comer = 0
    power_timer = 0
    timer_estado = 0
    stats = {}

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            elif evento.type == pygame.KEYDOWN:

                # ============ MENU ============
                if estado == ESTADO_MENU:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        sel_dificultad = (sel_dificultad - 1) % 4
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        sel_dificultad = (sel_dificultad + 1) % 4
                    elif evento.key in (pygame.K_a, pygame.K_LEFT):
                        num_jugadores = max(1, num_jugadores - 1)
                    elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                        num_jugadores = min(2, num_jugadores + 1)
                    elif evento.key == pygame.K_RETURN:
                        dificultad = sel_dificultad
                        mapa, pacman, fantasmas = crear_juego(dificultad)
                        blinky, pinky, inky, clyde = fantasmas
                        streak_comer = 0
                        power_timer = 0
                        stats = stats_vacias(mapa)
                        timer_estado = TIEMPO_LISTO
                        estado = ESTADO_LISTO
                        sonidos.play_ready()
                    elif evento.key == pygame.K_ESCAPE:
                        corriendo = False

                # ============ LISTO ============
                elif estado == ESTADO_LISTO:
                    if evento.key == pygame.K_ESCAPE:
                        sel_dificultad = dificultad
                        estado = ESTADO_MENU

                # ============ JUGANDO ============
                elif estado == ESTADO_JUGANDO:
                    if evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        pausa_sel = 0
                        estado = ESTADO_PAUSA

                # ============ PAUSA ============
                elif estado == ESTADO_PAUSA:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        pausa_sel = (pausa_sel - 1) % 3
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        pausa_sel = (pausa_sel + 1) % 3
                    elif evento.key == pygame.K_RETURN:
                        if pausa_sel == 0:
                            estado = ESTADO_JUGANDO
                        elif pausa_sel == 1:
                            mapa, pacman, fantasmas = crear_juego(dificultad)
                            blinky, pinky, inky, clyde = fantasmas
                            streak_comer = 0
                            power_timer = 0
                            stats = stats_vacias(mapa)
                            timer_estado = TIEMPO_LISTO
                            estado = ESTADO_LISTO
                            sonidos.play_ready()
                        elif pausa_sel == 2:
                            sel_dificultad = dificultad
                            estado = ESTADO_MENU
                    elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        estado = ESTADO_JUGANDO

                # ============ GAME OVER / VICTORIA ============
                elif estado in (ESTADO_GAME_OVER, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        sel_dificultad = dificultad
                        estado = ESTADO_MENU
                    elif evento.key == pygame.K_ESCAPE:
                        corriendo = False

        # ============ UPDATE ============

        if estado == ESTADO_LISTO:
            timer_estado -= 1
            if timer_estado <= 0:
                pacman.invincible = True
                pacman.tiempo_invencible = TIEMPO_INVENCIBLE
                estado = ESTADO_JUGANDO

        elif estado == ESTADO_JUGANDO:
            stats['tiempo_frames'] += 1
            teclas = pygame.key.get_pressed()

            # P1 -> Blinky (WASD) siempre
            if teclas[pygame.K_w]:
                blinky.direccion_siguiente = ARRIBA
            elif teclas[pygame.K_s]:
                blinky.direccion_siguiente = ABAJO
            elif teclas[pygame.K_a]:
                blinky.direccion_siguiente = IZQUIERDA
            elif teclas[pygame.K_d]:
                blinky.direccion_siguiente = DERECHA

            # Pinky: jugador en 2J, IA en 1J
            if num_jugadores == 2:
                if teclas[pygame.K_UP]:
                    pinky.direccion_siguiente = ARRIBA
                elif teclas[pygame.K_DOWN]:
                    pinky.direccion_siguiente = ABAJO
                elif teclas[pygame.K_LEFT]:
                    pinky.direccion_siguiente = IZQUIERDA
                elif teclas[pygame.K_RIGHT]:
                    pinky.direccion_siguiente = DERECHA
            else:
                if pinky.asustado:
                    ia_asustado(pinky, pacman.tile_col,
                                pacman.tile_fila, mapa)
                else:
                    ia_pinky(pinky, mapa,
                             pacman.tile_col, pacman.tile_fila,
                             pacman.direccion)

            # IA Pac-Man
            ias_pacman[dificultad](pacman, mapa, fantasmas)

            # IA Inky
            if inky.asustado:
                ia_asustado(inky, pacman.tile_col, pacman.tile_fila, mapa)
            else:
                ia_inky(inky, mapa,
                        pacman.tile_col, pacman.tile_fila,
                        pacman.direccion,
                        blinky.tile_col, blinky.tile_fila)

            # IA Clyde
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

            if pacman.comio_punto:
                stats['dots'] += 1
                sonidos.chomp()
            if pacman.comio_power:
                stats['power_pellets'] += 1
                sonidos.play_power()

            if pacman.activar_power:
                pacman.activar_power = False
                for f in fantasmas:
                    f.poner_asustado(TIEMPO_ASUSTADO)
                streak_comer = 0
                power_timer = TIEMPO_ASUSTADO

            if power_timer > 0:
                power_timer -= 1

            for f in fantasmas:
                if not f.activo or f.ojos_solo:
                    continue
                if not colisionan(pacman, f):
                    continue
                if f.asustado:
                    pts = FANTASMA_PTS[min(streak_comer,
                                          len(FANTASMA_PTS) - 1)]
                    pacman.puntuacion += pts
                    f.ser_comido()
                    streak_comer += 1
                    stats['fantasmas_comidos'] += 1
                    sonidos.play_eat_ghost()
                elif not pacman.invincible:
                    pacman.registrar_muerte()
                    pacman.vidas -= 1
                    pacman.iniciar_muerte()
                    sonidos.play_death()
                    estado = ESTADO_MURIENDO
                    timer_estado = TIEMPO_MURIENDO
                    break

            if mapa.puntos_restantes <= 0:
                estado = ESTADO_VICTORIA

        elif estado == ESTADO_MURIENDO:
            pacman.update(mapa)
            timer_estado -= 1
            if timer_estado <= 0:
                if pacman.vidas <= 0:
                    estado = ESTADO_GAME_OVER
                else:
                    pacman.reiniciar_posicion()
                    for f in fantasmas:
                        f.reiniciar()
                    power_timer = 0
                    streak_comer = 0
                    timer_estado = TIEMPO_LISTO
                    estado = ESTADO_LISTO
                    sonidos.play_ready()

        # ============ RENDER ============
        pantalla.fill(NEGRO)

        if estado == ESTADO_MENU:
            dibujar_menu(pantalla, fuente, fuente_grande, fuente_chica,
                         sel_dificultad, num_jugadores)
        else:
            mapa.render(pantalla)
            pacman.render(pantalla)
            for f in fantasmas:
                f.render(pantalla)
            dibujar_hud(pantalla, fuente, fuente_chica, pacman, mapa,
                        power_timer, dificultad, num_jugadores)

            if estado == ESTADO_LISTO:
                dibujar_ready(pantalla, fuente_grande)
            elif estado == ESTADO_PAUSA:
                dibujar_pausa(pantalla, fuente, fuente_grande,
                              fuente_chica, pausa_sel)
            elif estado == ESTADO_GAME_OVER:
                dibujar_stats(pantalla, fuente, fuente_chica, fuente_grande,
                              stats, pacman, num_jugadores,
                              "GAME OVER", (255, 0, 0))
            elif estado == ESTADO_VICTORIA:
                dibujar_stats(pantalla, fuente, fuente_chica, fuente_grande,
                              stats, pacman, num_jugadores,
                              "VICTORIA!", AMARILLO)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()