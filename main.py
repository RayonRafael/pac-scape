# ============================================================
# main.py
# ============================================================
# El motor principal del juego. Une todos los modulos y controla
# el flujo completo del juego.
#
# Responsabilidades:
#   - Game loop (bucle principal que se repite 60 veces por segundo)
#   - Procesar eventos de teclado y ventana
#   - Gestionar los 7 estados del juego
#   - Actualizar la logica de cada frame
#   - Renderizar todo en pantalla
#   - Escalar el juego al tamano de ventana (resize / pantalla completa)
#
# Los 7 estados del juego y sus transiciones:
#
#   MENU → LISTO → JUGANDO → MURIENDO → GAME_OVER → MENU
#                   ↕ PAUSA               ↑
#                   → VICTORIA ───────────┘
#
# ============================================================

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


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def colisionan(e1, e2, radio=TILE_SIZE * 0.7):
    """
    Detecta si dos entidades estan lo suficientemente cerca
    como para considerarse "tocandose".
    Compara la distancia al cuadrado con un radio de colision.
    Usar distancia al cuadrado evita calcular raiz cuadrada (mas rapido).
    """
    dx = e1.x - e2.x
    dy = e1.y - e2.y
    return (dx * dx + dy * dy) < radio * radio


def format_tiempo(frames):
    """Convierte frames a formato M:SS (ej: 1200 frames = 0:20)."""
    s = frames // 60
    return f"{s // 60}:{s % 60:02d}"


def escalar_a_ventana(interna, vw, vh):
    """
    Escala la superficie interna del juego al tamano de la ventana,
    manteniendo la proporcion (aspect ratio).
    Si la ventana es mas ancha de lo necesario, deja barras negras
    a los lados. Si es mas alta, deja barras arriba/abajo.

    Parametros:
        interna: superficie del juego (672x794)
        vw, vh: tamano actual de la ventana
    Devuelve:
        (superficie_escalada, offset_x, offset_y)
    """
    escala = min(vw / ANCHO, vh / ALTO)
    nw = int(ANCHO * escala)
    nh = int(ALTO * escala)
    x = (vw - nw) // 2  # Centrar horizontalmente
    y = (vh - nh) // 2  # Centrar verticalmente
    return pygame.transform.scale(interna, (nw, nh)), x, y


def crear_juego(dificultad):
    """
    Crea una partida nueva desde cero.
    Devuelve: (mapa, pacman, lista_de_fantasmas)
    """
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
    """Crea un diccionario de estadisticas vacio para una nueva partida."""
    return {
        'dots': 0, 'power_pellets': 0,
        'fantasmas_comidos': 0,
        'tiempo_frames': 0,
        'total_dots': mapa.puntos_restantes,
    }


# ============================================================
# MENU PRINCIPAL
# ============================================================

def dibujar_menu(pantalla, f_grande, f_media, f_chica,
                 sel_dificultad, num_jugadores):
    """
    Dibuja la pantalla de inicio con:
    - Titulo del juego
    - Selector de jugadores (1 o 2, con A/D)
    - Selector de dificultad (4 niveles, con W/S)
    - Controles segun el modo elegido
    - Boton para iniciar (ENTER)
    """
    pantalla.fill(NEGRO)
    cx = ANCHO // 2  # Centro horizontal

    # --- Titulo ---
    y = 50
    txt = f_grande.render("PAC-SCAPE", True, AMARILLO)
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))
    y += 40
    txt = f_chica.render("4 FANTASMAS  vs  PAC-MAN IA", True, (150, 150, 180))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))

    # --- Separador ---
    y += 30
    pygame.draw.line(pantalla, AZUL_PARED, (cx - 180, y), (cx + 180, y), 1)

    # --- Jugadores (A / D) ---
    y += 25
    txt = f_chica.render("JUGADORES", True, (90, 90, 120))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))
    y += 28

    # Flechas < y > alrededor del texto
    flecha_col = (150, 150, 200)
    if num_jugadores > 1:
        txt = f_media.render("<", True, flecha_col)
        pantalla.blit(txt, (cx - 80, y))

    if num_jugadores == 1:
        ptxt, pcol = "1 JUGADOR", (100, 220, 255)
    else:
        ptxt, pcol = "2 JUGADORES", (255, 220, 100)
    txt = f_media.render(ptxt, True, pcol)
    pantalla.blit(txt, txt.get_rect(center=(cx, y + 2)))

    if num_jugadores < 2:
        txt = f_media.render(">", True, flecha_col)
        pantalla.blit(txt, (cx + 60, y))

    y += 36
    txt = f_chica.render("A / D  para cambiar", True, (70, 70, 90))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))

    # --- Separador ---
    y += 25
    pygame.draw.line(pantalla, AZUL_PARED, (cx - 180, y), (cx + 180, y), 1)

    # --- Dificultad (W / S) ---
    y += 25
    txt = f_chica.render("DIFICULTAD PAC-MAN", True, (90, 90, 120))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))
    y += 28

    # Mostrar las 4 dificultades, la seleccionada tiene recuadro
    for i, nombre in enumerate(NOMBRES_DIFICULTAD):
        col = COLORES_DIFICULTAD[i]
        if i == sel_dificultad:
            rect = pygame.Rect(cx - 100, y - 2, 200, 24)
            pygame.draw.rect(pantalla, (30, 30, 60), rect, border_radius=5)
            pygame.draw.rect(pantalla, col, rect, 2, border_radius=5)
            txt = f_chica.render(f"  {nombre}", True, col)
            pantalla.blit(txt, (cx - 92, y + 3))
        else:
            txt = f_chica.render(f"  {nombre}", True, (50, 50, 70))
            pantalla.blit(txt, (cx - 92, y + 3))
        y += 28

    # Descripcion de la dificultad seleccionada
    y += 5
    txt = f_chica.render(DESCRIPCIONES[sel_dificultad], True,
                         COLORES_DIFICULTAD[sel_dificultad])
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))
    y += 6
    txt = f_chica.render("W / S  para cambiar", True, (70, 70, 90))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))

    # --- Separador ---
    y += 28
    pygame.draw.line(pantalla, AZUL_PARED, (cx - 180, y), (cx + 180, y), 1)

    # --- Controles (cambian segun 1J o 2J) ---
    y += 25
    if num_jugadores == 1:
        lineas = [
            ("WASD o Flechas → Blinky (rojo)", BLINKY_COLOR),
            ("Pinky, Inky y Clyde: IA", (120, 120, 140)),
        ]
    else:
        lineas = [
            ("P1: WASD → Blinky (rojo)", BLINKY_COLOR),
            ("P2: Flechas → Pinky (rosa)", PINKY_COLOR),
            ("Inky y Clyde: siempre IA", (120, 120, 140)),
        ]
    for texto, color in lineas:
        txt = f_chica.render(texto, True, color)
        pantalla.blit(txt, txt.get_rect(center=(cx, y)))
        y += 22

    # --- Separador ---
    y += 18
    pygame.draw.line(pantalla, AZUL_PARED, (cx - 180, y), (cx + 180, y), 1)

    # --- Boton ENTER (con pulso visual) ---
    y += 30
    # Brillo oscilante: el texto pulsa entre 50% y 100% de brillo
    brillo = abs((pygame.time.get_ticks() % 1600) / 800 - 1)
    v = int(255 * (0.5 + brillo * 0.5))
    txt = f_media.render("ENTER  para jugar", True, (v, v, 0))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))

    y += 28
    txt = f_chica.render("ESC: salir  |  F11: pantalla completa", True, (50, 50, 70))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# MENU DE PAUSA
# ============================================================

def dibujar_pausa(pantalla, f_media, f_chica, f_grande, seleccion):
    """
    Dibuja el menu de pausa como overlay sobre el juego.
    Se ve el juego detras (semi-transparente) con 3 opciones:
    1) Reanudar
    2) Reiniciar partida
    3) Menu principal
    """
    # Overlay oscuro semi-transparente
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)  # 180/255 de opacidad
    overlay.fill(NEGRO)
    pantalla.blit(overlay, (0, 0))

    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2

    # Titulo
    txt = f_grande.render("PAUSA", True, BLANCO)
    pantalla.blit(txt, txt.get_rect(center=(cx, cy - 70)))

    pygame.draw.line(pantalla, AZUL_PARED,
                     (cx - 100, cy - 45), (cx + 100, cy - 45), 1)

    # Opciones
    y = cy - 20
    for i, opcion in enumerate(PAUSA_OPCIONES):
        col_op = AMARILLO if i == seleccion else (120, 120, 140)
        prefijo = "> " if i == seleccion else "  "
        txt = f_media.render(f"{prefijo}{opcion}", True, col_op)
        pantalla.blit(txt, txt.get_rect(center=(cx, y)))
        y += 36

    # Instrucciones
    pygame.draw.line(pantalla, AZUL_PARED,
                     (cx - 100, y + 5), (cx + 100, y + 5), 1)
    y += 20
    txt = f_chica.render("W/S elegir | ENTER confirmar", True, (80, 80, 100))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))
    y += 18
    txt = f_chica.render("ESC o P para reanudar", True, (80, 80, 100))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# HUD (barra de informacion inferior)
# ============================================================

def dibujar_hud(pantalla, f_media, f_chica, pacman, mapa,
                power_timer, dificultad, num_jugadores):
    """
    Dibuja la barra de informacion inferior:
    - Izquierda: puntos acumulados + iconos de vidas
    - Centro: dificultad + puntos restantes
    - Derecha: barra de power mode (si esta activo)
    """
    y_base = MAPA_FILAS * TILE_SIZE

    # Fondo de la barra
    pygame.draw.rect(pantalla, HUD_BG, (0, y_base, ANCHO, HUD_ALTO))
    pygame.draw.line(pantalla, AZUL_PARED, (0, y_base), (ANCHO, y_base), 2)

    # Izquierda: puntos
    txt = f_media.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
    pantalla.blit(txt, (12, y_base + 4))

    # Izquierda: iconos de vidas (mini Pac-Mans)
    for i in range(pacman.vidas):
        lx = 12 + i * 28
        ly = y_base + 34
        pygame.draw.circle(pantalla, AMARILLO, (lx, ly), 7)
        pygame.draw.polygon(pantalla, NEGRO, [
            (lx, ly), (lx + 9, ly - 3), (lx + 9, ly + 3)])

    # Centro: dificultad y jugadores
    etiqueta = f"{NOMBRES_DIFICULTAD[dificultad]} | {num_jugadores}J"
    txt = f_chica.render(etiqueta, True, COLORES_DIFICULTAD[dificultad])
    pantalla.blit(txt, txt.get_rect(center=(ANCHO // 2, y_base + 14)))

    # Centro: puntos restantes
    txt = f_chica.render(f"Rest: {mapa.puntos_restantes}", True, HUD_TEXTO)
    pantalla.blit(txt, txt.get_rect(center=(ANCHO // 2, y_base + 34)))

    # Derecha: barra de power mode
    if power_timer > 0:
        bar_x = ANCHO - 115
        bar_y = y_base + 8
        bar_w = 100
        bar_h = 8
        ratio = power_timer / TIEMPO_ASUSTADO  # 1.0 = lleno, 0.0 = vacio
        # Fondo de la barra
        pygame.draw.rect(pantalla, (40, 40, 60),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        # Barra de progreso
        pygame.draw.rect(pantalla, AMARILLO,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h),
                         border_radius=4)
        # Etiqueta
        txt = f_chica.render("POWER", True, AMARILLO)
        pantalla.blit(txt, (bar_x + 28, bar_y + 10))


def dibujar_boton_pausa(pantalla, f_chica):
    """
    Dibuja un boton visual de pausa en la esquina superior derecha.
    Pulsa sutilmente para llamar la atencion.
    """
    bx = ANCHO - 90
    by = 8
    bw = 75
    bh = 24

    # Pulso sutil del brillo
    t = pygame.time.get_ticks()
    brillo = 0.6 + 0.4 * abs((t % 2000) / 1000 - 1)
    col = (int(100 * brillo), int(100 * brillo), int(160 * brillo))

    # Recuadro
    rect = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(pantalla, (20, 20, 40), rect, border_radius=4)
    pygame.draw.rect(pantalla, col, rect, 1, border_radius=4)

    # Texto
    txt = f_chica.render("[P] Pausa", True, col)
    pantalla.blit(txt, (bx + 10, by + 4))


# ============================================================
# OVERLAYS (textos sobre el juego)
# ============================================================

def dibujar_ready(pantalla, f_media):
    """Muestra 'READY!' en el centro de la pantalla."""
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2
    txt = f_media.render("READY!", True, AMARILLO)
    pantalla.blit(txt, txt.get_rect(center=(cx, cy + 20)))


def dibujar_stats(pantalla, f_media, f_chica, f_grande,
                  stats, pacman, num_jugadores, titulo, color_titulo):
    """
    Muestra la pantalla de estadisticas al final de la partida.
    Se usa tanto para Game Over como para Victoria.
    Muestra: puntos, dots, power pellets, fantasmas comidos,
    dificultad, tiempo jugado.
    """
    # Overlay oscuro
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    pantalla.blit(overlay, (0, 0))

    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2

    # Titulo (GAME OVER o VICTORIA!)
    txt = f_grande.render(titulo, True, color_titulo)
    pantalla.blit(txt, txt.get_rect(center=(cx, cy - 120)))

    # Estadisticas
    y = cy - 65
    lineas = [
        (f"Puntos: {pacman.puntuacion}", BLANCO),
        (f"Dots: {stats['dots']}/{stats['total_dots']}", (180, 180, 200)),
        (f"Power pellets: {stats['power_pellets']}/4", (180, 180, 200)),
        (f"Fantasmas comidos: {stats['fantasmas_comidos']}", (180, 180, 200)),
        (f"Dificultad: {NOMBRES_DIFICULTAD[pacman.dificultad]} | "
         f"{num_jugadores}J", COLORES_DIFICULTAD[pacman.dificultad]),
        (f"Tiempo: {format_tiempo(stats['tiempo_frames'])}", (180, 180, 200)),
    ]
    for texto, color in lineas:
        txt = f_chica.render(texto, True, color)
        pantalla.blit(txt, txt.get_rect(center=(cx, y)))
        y += 24

    # Separador e instrucciones
    y += 12
    pygame.draw.line(pantalla, AZUL_PARED, (cx - 120, y), (cx + 120, y), 1)
    y += 15
    txt = f_chica.render("R: menu  |  ESC: salir", True, (100, 100, 120))
    pantalla.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# GAME LOOP PRINCIPAL
# ============================================================

def main():
    """
    Funcion principal del juego.
    Inicializa Pygame, crea la ventana, y ejecuta el game loop.
    El game loop se repite 60 veces por segundo y hace 3 cosas:
    1) Procesar eventos (teclado, mouse, cerrar ventana)
    2) Actualizar la logica del juego
    3) Renderizar todo en pantalla
    """

    # Inicializar mixer de audio antes que Pygame para mejor rendimiento
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()

    # Crear ventana resizable (se puede estirar con el mouse)
    window_w, window_h = ANCHO, ALTO
    pantalla = pygame.display.set_mode(
        (window_w, window_h), pygame.RESIZABLE)
    pygame.display.set_caption("Pac-Scape")

    # Buffer interno: todo se dibuja aca primero (tamano fijo del juego).
    # Despues se escala al tamano de la ventana. Esto permite
    # redimensionar sin afectar la logica del juego.
    buffer = pygame.Surface((ANCHO, ALTO))

    reloj = pygame.time.Clock()

    # 3 tamanos de fuente para diferentes usos
    f_grande = pygame.font.Font(None, 52)  # Titulos (PAC-SCAPE, GAME OVER)
    f_media  = pygame.font.Font(None, 30)  # Texto normal (menus, botones)
    f_chica  = pygame.font.Font(None, 22)  # Texto pequeno (instrucciones, stats)

    sonidos = Sonidos()

    # Diccionario que mapea dificultad a funcion de IA
    ias_pacman = {
        DIFIC_TONTA: ia_pacman_tonta,
        DIFIC_TEMEROSA: ia_pacman_temerosa,
        DIFIC_ASTUTA: ia_pacman_astuta,
        DIFIC_MAESTRA: ia_pacman_maestra,
    }

    CLYDE_ESQUINA = (1, 29)  # Esquina donde Clyde se esconde

    # ---- Variables de estado del juego ----
    fullscreen = False          # Pantalla completa activa?
    estado = ESTADO_MENU        # Estado actual del juego
    sel_dificultad = DIFIC_TONTA  # Dificultad seleccionada en el menu
    num_jugadores = 2           # Numero de jugadores (1 o 2)
    dificultad = DIFIC_TONTA    # Dificultad de la partida actual
    pausa_sel = 0               # Opcion seleccionada en el menu de pausa

    # Variables de la partida (se crean al iniciar)
    mapa = pacman = fantasmas = None
    blinky = pinky = inky = clyde = None
    streak_comer = 0     # Contador de fantasmas comidos en racha
    power_timer = 0      # Frames restantes de power mode
    timer_estado = 0     # Timer para estados temporales (listo, muriendo)
    stats = {}           # Estadisticas de la partida actual

    # ============================================================
    # GAME LOOP: se repite 60 veces por segundo hasta cerrar
    # ============================================================
    corriendo = True
    while corriendo:

        # ---- FASE 1: PROCESAR EVENTOS ----
        # Los eventos son acciones del usuario (teclas, mouse, cerrar ventana)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False  # Clic en la X de la ventana

            # Resize de ventana: actualizar tamano
            elif evento.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    window_w, window_h = evento.w, evento.h
                    pantalla = pygame.display.set_mode(
                        (window_w, window_h), pygame.RESIZABLE)

            elif evento.type == pygame.KEYDOWN:

                # F11: alternar pantalla completa
                if evento.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        pantalla = pygame.display.set_mode(
                            (0, 0), pygame.FULLSCREEN)
                        window_w, window_h = pantalla.get_size()
                    else:
                        pantalla = pygame.display.set_mode(
                            (ANCHO, ALTO), pygame.RESIZABLE)
                        window_w, window_h = ANCHO, ALTO

                # ============ ESTADO: MENU ============
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
                        # Iniciar partida
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

                # ============ ESTADO: LISTO ============
                elif estado == ESTADO_LISTO:
                    if evento.key == pygame.K_ESCAPE:
                        sel_dificultad = dificultad
                        estado = ESTADO_MENU

                # ============ ESTADO: JUGANDO ============
                elif estado == ESTADO_JUGANDO:
                    # P o ESC abre el menu de pausa
                    if evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        pausa_sel = 0
                        estado = ESTADO_PAUSA

                # ============ ESTADO: PAUSA ============
                elif estado == ESTADO_PAUSA:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        pausa_sel = (pausa_sel - 1) % 3
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        pausa_sel = (pausa_sel + 1) % 3
                    elif evento.key == pygame.K_RETURN:
                        # Ejecutar la opcion seleccionada
                        if pausa_sel == 0:
                            estado = ESTADO_JUGANDO   # Reanudar
                        elif pausa_sel == 1:
                            # Reiniciar partida (mismas opciones)
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
                            estado = ESTADO_MENU       # Volver al menu
                    elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        estado = ESTADO_JUGANDO        # Reanudar rapido

                # ============ ESTADO: GAME OVER / VICTORIA ============
                elif estado in (ESTADO_GAME_OVER, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        sel_dificultad = dificultad
                        estado = ESTADO_MENU
                    elif evento.key == pygame.K_ESCAPE:
                        corriendo = False

        # ---- FASE 2: ACTUALIZAR LOGICA ----

        # ============ ESTADO: LISTO ============
        # Cuenta regresiva antes de empezar (muestra "READY!")
        if estado == ESTADO_LISTO:
            timer_estado -= 1
            if timer_estado <= 0:
                # Activar invencibilidad inicial
                pacman.invincible = True
                pacman.tiempo_invencible = TIEMPO_INVENCIBLE
                estado = ESTADO_JUGANDO

        # ============ ESTADO: JUGANDO ============
        elif estado == ESTADO_JUGANDO:
            stats['tiempo_frames'] += 1
            teclas = pygame.key.get_pressed()

            # --- Blinky: controlado por P1 (WASD) ---
            # En modo 1J, tambien acepta Flechas
            if teclas[pygame.K_w] or (
                    num_jugadores == 1 and teclas[pygame.K_UP]):
                blinky.direccion_siguiente = ARRIBA
            elif teclas[pygame.K_s] or (
                    num_jugadores == 1 and teclas[pygame.K_DOWN]):
                blinky.direccion_siguiente = ABAJO
            elif teclas[pygame.K_a] or (
                    num_jugadores == 1 and teclas[pygame.K_LEFT]):
                blinky.direccion_siguiente = IZQUIERDA
            elif teclas[pygame.K_d] or (
                    num_jugadores == 1 and teclas[pygame.K_RIGHT]):
                blinky.direccion_siguiente = DERECHA

            # --- Pinky: controlado por P2 (Flechas) en 2J, IA en 1J ---
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
                # En 1J, Pinky tiene IA (corta 4 tiles adelante)
                if pinky.asustado:
                    ia_asustado(pinky, pacman.tile_col,
                                pacman.tile_fila, mapa)
                else:
                    ia_pinky(pinky, mapa,
                             pacman.tile_col, pacman.tile_fila,
                             pacman.direccion)

            # --- Pac-Man IA ---
            # Llama a la funcion de IA segun la dificultad elegida
            ias_pacman[dificultad](pacman, mapa, fantasmas)

            # --- Inky IA (flanqueador, usa posicion de Blinky) ---
            if inky.asustado:
                ia_asustado(inky, pacman.tile_col, pacman.tile_fila, mapa)
            else:
                ia_inky(inky, mapa,
                        pacman.tile_col, pacman.tile_fila,
                        pacman.direccion,
                        blinky.tile_col, blinky.tile_fila)

            # --- Clyde IA (cobarde: persigue lejos, huye cerca) ---
            if clyde.asustado:
                ia_asustado(clyde, pacman.tile_col, pacman.tile_fila, mapa)
            else:
                ia_clyde(clyde, mapa,
                         pacman.tile_col, pacman.tile_fila,
                         *CLYDE_ESQUINA)

            # --- Actualizar posiciones de todos ---
            pacman.update(mapa)
            for f in fantasmas:
                f.update(mapa)

            # --- Sonidos de comer ---
            if pacman.comio_punto:
                stats['dots'] += 1
                sonidos.chomp()
            if pacman.comio_power:
                stats['power_pellets'] += 1
                sonidos.play_power()

            # --- Activar power mode ---
            if pacman.activar_power:
                pacman.activar_power = False
                for f in fantasmas:
                    f.poner_asustado(TIEMPO_ASUSTADO)
                streak_comer = 0
                power_timer = TIEMPO_ASUSTADO

            # --- Actualizar timer de power mode ---
            if power_timer > 0:
                power_timer -= 1

            # --- Colisiones Pac-Man vs Fantasmas ---
            for f in fantasmas:
                if not f.activo or f.ojos_solo:
                    continue
                if not colisionan(pacman, f):
                    continue

                if f.asustado:
                    # Pac-Man come al fantasma (power mode activo)
                    pts = FANTASMA_PTS[min(streak_comer,
                                          len(FANTASMA_PTS) - 1)]
                    pacman.puntuacion += pts
                    f.ser_comido()
                    streak_comer += 1
                    stats['fantasmas_comidos'] += 1
                    sonidos.play_eat_ghost()
                elif not pacman.invincible:
                    # Fantasma atrapa a Pac-Man
                    pacman.registrar_muerte()  # Marcar zona peligrosa
                    pacman.vidas -= 1
                    pacman.iniciar_muerte()
                    sonidos.play_death()
                    estado = ESTADO_MURIENDO
                    timer_estado = TIEMPO_MURIENDO
                    break

            # --- Condicion de victoria ---
            if mapa.puntos_restantes <= 0:
                estado = ESTADO_VICTORIA

        # ============ ESTADO: MURIENDO ============
        # Espera a que termine la animacion de muerte
        elif estado == ESTADO_MURIENDO:
            pacman.update(mapa)  # Avanzar animacion de muerte
            timer_estado -= 1
            if timer_estado <= 0:
                if pacman.vidas <= 0:
                    estado = ESTADO_GAME_OVER
                else:
                    # Todavia tiene vidas: respawn
                    pacman.reiniciar_posicion()
                    for f in fantasmas:
                        f.reiniciar()
                    power_timer = 0
                    streak_comer = 0
                    timer_estado = TIEMPO_LISTO
                    estado = ESTADO_LISTO
                    sonidos.play_ready()

        # ---- FASE 3: RENDERIZAR ----
        # Todo se dibuja al buffer interno primero,
        # despues se escala al tamano de la ventana.

        buffer.fill(NEGRO)

        if estado == ESTADO_MENU:
            # Solo mostrar el menu
            dibujar_menu(buffer, f_grande, f_media, f_chica,
                         sel_dificultad, num_jugadores)
        else:
            # Dibujar el juego (mapa + Pac-Man + fantasmas)
            mapa.render(buffer)
            pacman.render(buffer)
            for f in fantasmas:
                f.render(buffer)

            # HUD siempre visible durante el juego
            dibujar_hud(buffer, f_media, f_chica, pacman, mapa,
                        power_timer, dificultad, num_jugadores)

            # Boton de pausa: visible durante juego y "READY!"
            if estado in (ESTADO_JUGANDO, ESTADO_LISTO):
                dibujar_boton_pausa(buffer, f_chica)

            # Overlays segun el estado
            if estado == ESTADO_LISTO:
                dibujar_ready(buffer, f_media)
            elif estado == ESTADO_PAUSA:
                dibujar_pausa(buffer, f_media, f_chica, f_grande, pausa_sel)
            elif estado == ESTADO_GAME_OVER:
                dibujar_stats(buffer, f_media, f_chica, f_grande,
                              stats, pacman, num_jugadores,
                              "GAME OVER", (255, 0, 0))
            elif estado == ESTADO_VICTORIA:
                dibujar_stats(buffer, f_media, f_chica, f_grande,
                              stats, pacman, num_jugadores,
                              "VICTORIA!", AMARILLO)

        # Escalar buffer al tamano de ventana y mostrar
        scaled, offx, offy = escalar_a_ventana(
            buffer, window_w, window_h)
        pantalla.fill(NEGRO)
        pantalla.blit(scaled, (offx, offy))
        pygame.display.flip()

        # Controlar velocidad: maximo 60 frames por segundo
        reloj.tick(FPS)

    # Salir limpiamente
    pygame.quit()
    sys.exit()


# Punto de entrada: solo ejecutar main() si este archivo
# se corre directamente (no si se importa desde otro archivo)
if __name__ == "__main__":
    main()