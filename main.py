import pygame
import sys
import json
import os
import random
from constantes import *
from mapa import Mapa
from pacman import PacMan
from fantasma import Fantasma
from ia import (
    ia_pacman_tonta, ia_pacman_temerosa,
    ia_pacman_astuta, ia_pacman_maestra,
    ia_blinky, ia_pinky, ia_inky, ia_clyde, ia_asustado,
)
from sonidos import Sonidos


# ============================================================
# CLASES AUXILIARES
# ============================================================

class PopUp:
    """Texto flotante que aparece al comer un fantasma o fruta."""
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
        surface.blit(txt, txt.get_rect(center=(int(self.x), int(self.y))))


class Fruta:
    """Fruta coleccionable que aparece temporalmente en el mapa."""
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
        # Cuerpo
        pygame.draw.circle(surface, self.color, (self.x, self.y), r)
        # Tallo
        pygame.draw.line(surface, (0, 100, 0),
                        (self.x, self.y - r),
                        (self.x + 2, self.y - r - 4), 2)
        # Brillo
        sr = max(1, r // 4)
        pygame.draw.circle(surface, (255, 255, 255),
                          (self.x - r // 3, self.y - r // 3), sr)
        # Parpadeo cuando esta por desaparecer (ultimos 2 seg)
        if self.timer < 120 and (self.timer // 10) % 2 == 0:
            pygame.draw.circle(surface, NEGRO, (self.x, self.y), r + 1)


# ============================================================
# HIGH SCORE
# ============================================================

def cargar_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except Exception:
            pass
    return 0


def guardar_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump({"high_score": score}, f)
    except Exception:
        pass


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def colisionan(e1, e2, radio=TILE_SIZE * 0.7):
    dx = e1.x - e2.x
    dy = e1.y - e2.y
    return (dx * dx + dy * dy) < radio * radio


def format_tiempo(frames):
    s = frames // 60
    return f"{s // 60}:{s % 60:02d}"


def escalar_a_ventana(interna, vw, vh):
    escala = min(vw / ANCHO, vh / ALTO)
    nw = int(ANCHO * escala)
    nh = int(Alto_escalado := int(ALTO * escala))
    x = (vw - nw) // 2
    y = (vh - nh) // 2
    return pygame.transform.scale(interna, (nw, nh)), x, y


def crear_juego(dificultad, idx_p1, idx_p2=None):
    mapa = Mapa()
    pacman = PacMan()
    pacman.dificultad = dificultad
    fantasmas = []
    for i in range(4):
        col, fila = GHOST_INICIOS[i]
        fantasmas.append(
            Fantasma(col, fila, VEL_FANTASMA, GHOST_COLORES[i],
                     GHOST_NOMBRES[i], SALIDA_DELAYS[i]))
    return mapa, pacman, fantasmas, fantasmas[idx_p1], (
        fantasmas[idx_p2] if idx_p2 is not None else None)


def stats_vacias(mapa):
    return {
        'dots': 0, 'power_pellets': 0,
        'fantasmas_comidos': 0,
        'tiempo_frames': 0,
        'total_dots': mapa.puntos_restantes,
    }


def aplicar_ia_fantasma(f, pacman, mapa, fantasmas, clyde_esquina):
    if f.nombre == "Blinky":
        if f.asustado:
            ia_asustado(f, pacman.tile_col, pacman.tile_fila, mapa)
        else:
            ia_blinky(f, mapa, pacman.tile_col, pacman.tile_fila)
    elif f.nombre == "Pinky":
        if f.asustado:
            ia_asustado(f, pacman.tile_col, pacman.tile_fila, mapa)
        else:
            ia_pinky(f, mapa, pacman.tile_col, pacman.tile_fila,
                     pacman.direccion)
    elif f.nombre == "Inky":
        blinky_obj = next((g for g in fantasmas if g.nombre == "Blinky"), None)
        if f.asustado:
            ia_asustado(f, pacman.tile_col, pacman.tile_fila, mapa)
        elif blinky_obj:
            ia_inky(f, mapa, pacman.tile_col, pacman.tile_fila,
                    pacman.direccion, blinky_obj.tile_col, blinky_obj.tile_fila)
    elif f.nombre == "Clyde":
        if f.asustado:
            ia_asustado(f, pacman.tile_col, pacman.tile_fila, mapa)
        else:
            ia_clyde(f, mapa, pacman.tile_col, pacman.tile_fila,
                     *clyde_esquina)


def dibujar_fantasma_mini(surface, cx, cy, tamano, color):
    r = tamano // 2
    pygame.draw.circle(surface, color, (cx, cy - r // 4), r)
    pygame.draw.rect(surface, color,
                     (cx - r, cy - r // 4, r * 2, r + r // 4))
    onda_r = max(2, r // 3)
    for i in range(3):
        ox = cx - r + onda_r + i * (r * 2 // 3)
        oy = cy + r
        pygame.draw.circle(surface, color, (ox, oy), onda_r)
    for sign in [-1, 1]:
        ex = cx + sign * (r // 3)
        ey = cy - r // 3
        ew = max(3, r // 3)
        eh = max(4, r // 2)
        pygame.draw.ellipse(surface, BLANCO,
                            (ex - ew, ey - eh // 2, ew * 2, eh))
        pygame.draw.circle(surface, PUPILA_COLOR,
                           (ex + sign, ey + 1), max(1, r // 6))


# ============================================================
# MENU PASO 1: JUGADORES
# ============================================================

def dibujar_menu_paso_jugadores(p, f_grande, f_media, f_chica,
                                 num_jugadores, high_score):
    p.fill(NEGRO)
    cx = ANCHO // 2

    y = 40
    txt = f_grande.render("PAC-SCAPE", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 35
    txt = f_chica.render("4 FANTASMAS  vs  PAC-MAN IA", True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(cx, y)))

    # High score
    if high_score > 0:
        y += 20
        txt = f_chica.render(f"HIGH SCORE: {high_score}", True, AMARILLO)
        p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 25
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)

    y += 25
    txt = f_chica.render("MODO DE JUEGO", True, (90, 90, 120))
    p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 30
    flecha_col = (150, 150, 200)
    if num_jugadores > 1:
        txt = f_grande.render("<", True, flecha_col)
        p.blit(txt, (cx - 100, y - 5))
    if num_jugadores == 1:
        txt = f_grande.render("1 JUGADOR", True, (100, 220, 255))
    else:
        txt = f_grande.render("2 JUGADORES", True, (255, 220, 100))
    p.blit(txt, txt.get_rect(center=(cx, y + 2)))
    if num_jugadores < 2:
        txt = f_grande.render(">", True, flecha_col)
        p.blit(txt, (cx + 80, y - 5))

    y += 40
    txt = f_chica.render("A / D  para cambiar", True, (70, 70, 90))
    p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 30
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)

    y += 25
    txt = f_chica.render("Fantasmas disponibles:", True, (90, 90, 120))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 32
    gap = 110
    start_x = cx - (gap * 3) // 2
    for i in range(4):
        fx = start_x + i * gap
        dibujar_fantasma_mini(p, fx, y, 36, GHOST_COLORES[i])
        txt = f_chica.render(GHOST_NOMBRES[i], True, GHOST_COLORES[i])
        p.blit(txt, txt.get_rect(center=(fx, y + 28)))
        txt = f_chica.render(GHOST_ROLES[i], True, (70, 70, 90))
        p.blit(txt, txt.get_rect(center=(fx, y + 43)))

    y += 75
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)

    y += 22
    if num_jugadores == 1:
        txt = f_chica.render("En el siguiente paso eliges tu fantasma",
                             True, (150, 150, 180))
    else:
        txt = f_chica.render("Ambos jugadores eligen su fantasma",
                             True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 18
    txt = f_chica.render("Los otros seran controlados por IA",
                         True, (100, 100, 130))
    p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 28
    brillo = abs((pygame.time.get_ticks() % 1600) / 800 - 1)
    v = int(255 * (0.5 + brillo * 0.5))
    txt = f_media.render("ENTER  continuar", True, (v, v, 0))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 28
    txt = f_chica.render("ESC: salir  |  F11: pantalla completa",
                         True, (50, 50, 70))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# MENU PASO 2: FANTASMAS
# ============================================================

def dibujar_menu_paso_fantasmas(p, f_grande, f_media, f_chica,
                                 num_jugadores, sel_p1, sel_p2):
    p.fill(NEGRO)
    cx = ANCHO // 2

    y = 25
    txt = f_media.render("PAC-SCAPE", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 28
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)

    y += 18
    if num_jugadores == 1:
        txt = f_media.render("ELIGE TU FANTASMA", True, BLANCO)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += 22
        txt = f_chica.render("A / D  para navegar", True, (90, 90, 120))
        p.blit(txt, txt.get_rect(center=(cx, y)))
    else:
        txt = f_media.render("ELIGE TUS FANTASMAS", True, BLANCO)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += 20
        txt = f_chica.render("P1: A / D    P2: Flechas", True, (90, 90, 120))
        p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 32
    box_w = 120
    box_h = 145
    gap = 15
    total_w = 4 * box_w + 3 * gap
    start_x = cx - total_w // 2 + box_w // 2

    for i in range(4):
        bx = start_x + i * (box_w + gap)
        by = y
        es_p1 = (i == sel_p1)
        es_p2 = (num_jugadores == 2 and i == sel_p2)

        bg = (25, 25, 55) if (es_p1 or es_p2) else (15, 15, 30)
        rect = pygame.Rect(bx - box_w // 2, by, box_w, box_h)
        pygame.draw.rect(p, bg, rect, border_radius=8)

        if es_p1:
            borde_col, grosor = BLANCO, 3
        elif es_p2:
            borde_col, grosor = AMARILLO, 3
        else:
            borde_col, grosor = (40, 40, 60), 1
        pygame.draw.rect(p, borde_col, rect, grosor, border_radius=8)

        dibujar_fantasma_mini(p, bx, by + 48, 52, GHOST_COLORES[i])

        txt = f_chica.render(GHOST_NOMBRES[i], True, GHOST_COLORES[i])
        p.blit(txt, txt.get_rect(center=(bx, by + 90)))
        txt = f_chica.render(GHOST_ROLES[i], True, (90, 90, 110))
        p.blit(txt, txt.get_rect(center=(bx, by + 108)))

        if es_p1:
            badge_col, badge_txt = BLANCO, "P1"
        elif es_p2:
            badge_col, badge_txt = AMARILLO, "P2"
        else:
            badge_col, badge_txt = (60, 60, 80), "IA"
        txt = f_chica.render(badge_txt, True, badge_col)
        p.blit(txt, txt.get_rect(center=(bx, by + 130)))

    y += box_h + 15
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)
    y += 10

    if num_jugadores == 1:
        txt = f_chica.render(GHOST_DETALLES[sel_p1], True,
                             GHOST_COLORES[sel_p1])
        p.blit(txt, txt.get_rect(center=(cx, y)))
    else:
        txt = f_chica.render(
            f"P1: {GHOST_DETALLES[sel_p1]}", True, GHOST_COLORES[sel_p1])
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += 16
        txt = f_chica.render(
            f"P2: {GHOST_DETALLES[sel_p2]}", True, GHOST_COLORES[sel_p2])
        p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 22
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)
    y += 12
    no_controlados = []
    for i in range(4):
        if i == sel_p1:
            continue
        if num_jugadores == 2 and i == sel_p2:
            continue
        no_controlados.append(GHOST_NOMBRES[i])
    txt = f_chica.render(
        f"IA controla: {', '.join(no_controlados)}", True, (100, 100, 130))
    p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 25
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)
    y += 16
    brillo = abs((pygame.time.get_ticks() % 1600) / 800 - 1)
    v = int(255 * (0.5 + brillo * 0.5))
    txt = f_media.render("ENTER  continuar", True, (v, v, 0))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 22
    txt = f_chica.render("ESC: volver", True, (50, 50, 70))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# MENU PASO 3: DIFICULTAD
# ============================================================

def dibujar_menu_paso_dificultad(p, f_grande, f_media, f_chica,
                                  num_jugadores, sel_dificultad,
                                  idx_p1, idx_p2):
    p.fill(NEGRO)
    cx = ANCHO // 2

    y = 30
    txt = f_media.render("PAC-SCAPE", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 28
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)

    y += 16
    p1_col = GHOST_COLORES[idx_p1]
    texto_sel = f"P1: {GHOST_NOMBRES[idx_p1]}"
    if num_jugadores == 2 and idx_p2 is not None:
        texto_sel += f"  |  P2: {GHOST_NOMBRES[idx_p2]}"
    txt = f_chica.render(texto_sel, True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 20
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)

    y += 20
    txt = f_chica.render("DIFICULTAD PAC-MAN", True, (90, 90, 120))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 24

    for i, nombre in enumerate(NOMBRES_DIFICULTAD):
        col = COLORES_DIFICULTAD[i]
        if i == sel_dificultad:
            rect = pygame.Rect(cx - 100, y - 2, 200, 24)
            pygame.draw.rect(p, (30, 30, 60), rect, border_radius=5)
            pygame.draw.rect(p, col, rect, 2, border_radius=5)
            txt = f_chica.render(f"  {nombre}", True, col)
            p.blit(txt, (cx - 92, y + 3))
        else:
            txt = f_chica.render(f"  {nombre}", True, (50, 50, 70))
            p.blit(txt, (cx - 92, y + 3))
        y += 28

    y += 4
    txt = f_chica.render(DESCRIPCIONES[sel_dificultad], True,
                         COLORES_DIFICULTAD[sel_dificultad])
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 6
    txt = f_chica.render("W / S  para cambiar", True, (70, 70, 90))
    p.blit(txt, txt.get_rect(center=(cx, y)))

    y += 28
    pygame.draw.line(p, AZUL_PARED, (cx - 190, y), (cx + 190, y), 1)
    y += 18
    brillo = abs((pygame.time.get_ticks() % 1600) / 800 - 1)
    v = int(255 * (0.5 + brillo * 0.5))
    txt = f_media.render("ENTER  para jugar", True, (v, v, 0))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 26
    txt = f_chica.render("ESC: volver", True, (50, 50, 70))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# PAUSA, HUD, OVERLAYS
# ============================================================

def dibujar_pausa(p, f_media, f_chica, f_grande, seleccion):
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    p.blit(overlay, (0, 0))
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2
    txt = f_grande.render("PAUSA", True, BLANCO)
    p.blit(txt, txt.get_rect(center=(cx, cy - 70)))
    pygame.draw.line(p, AZUL_PARED,
                     (cx - 100, cy - 45), (cx + 100, cy - 45), 1)
    y = cy - 20
    for i, opcion in enumerate(PAUSA_OPCIONES):
        col_op = AMARILLO if i == seleccion else (120, 120, 140)
        prefijo = "> " if i == seleccion else "  "
        txt = f_media.render(f"{prefijo}{opcion}", True, col_op)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += 36
    pygame.draw.line(p, AZUL_PARED,
                     (cx - 100, y + 5), (cx + 100, y + 5), 1)
    y += 20
    txt = f_chica.render("W/S elegir | ENTER confirmar", True, (80, 80, 100))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 18
    txt = f_chica.render("ESC o P para reanudar", True, (80, 80, 100))
    p.blit(txt, txt.get_rect(center=(cx, y)))


def dibujar_hud(p, f_media, f_chica, pacman, mapa,
                power_timer, dificultad, num_jugadores,
                idx_p1, idx_p2, high_score):
    y_base = MAPA_FILAS * TILE_SIZE
    pygame.draw.rect(p, HUD_BG, (0, y_base, ANCHO, HUD_ALTO))
    pygame.draw.line(p, AZUL_PARED, (0, y_base), (ANCHO, y_base), 2)

    # Izquierda: puntos
    txt = f_media.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
    p.blit(txt, (12, y_base + 4))

    # Izquierda: vidas
    for i in range(pacman.vidas):
        lx = 12 + i * 28
        ly = y_base + 34
        pygame.draw.circle(p, AMARILLO, (lx, ly), 7)
        pygame.draw.polygon(p, NEGRO, [
            (lx, ly), (lx + 9, ly - 3), (lx + 9, ly + 3)])

    # Centro: info
    p1_label = f"P1:{GHOST_NOMBRES[idx_p1][:3]}"
    if num_jugadores == 2 and idx_p2 is not None:
        p2_label = f"P2:{GHOST_NOMBRES[idx_p2][:3]}"
        etiqueta = f"{p1_label} {p2_label} {NOMBRES_DIFICULTAD[dificultad][:3]}"
    else:
        etiqueta = f"{p1_label} {NOMBRES_DIFICULTAD[dificultad][:3]}|1J"
    txt = f_chica.render(etiqueta, True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(ANCHO // 2, y_base + 10)))

    txt = f_chica.render(f"Rest: {mapa.puntos_restantes}", True, HUD_TEXTO)
    p.blit(txt, txt.get_rect(center=(ANCHO // 2, y_base + 28)))

    # High score
    hi_str = f"HI:{high_score}"
    txt = f_chica.render(hi_str, True, (200, 200, 100))
    p.blit(txt, txt.get_rect(center=(ANCHO // 2, y_base + 42)))

    # Derecha: power bar
    if power_timer > 0:
        bar_x = ANCHO - 115
        bar_y = y_base + 8
        bar_w = 100
        bar_h = 8
        ratio = power_timer / TIEMPO_ASUSTADO
        pygame.draw.rect(p, (40, 40, 60),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(p, AMARILLO,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h),
                         border_radius=4)
        txt = f_chica.render("POWER", True, AMARILLO)
        p.blit(txt, (bar_x + 28, bar_y + 10))


def dibujar_boton_pausa(p, f_chica):
    bx = ANCHO - 90
    by = 8
    bw = 75
    bh = 24
    t = pygame.time.get_ticks()
    brillo = 0.6 + 0.4 * abs((t % 2000) / 1000 - 1)
    col = (int(100 * brillo), int(100 * brillo), int(160 * brillo))
    rect = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(p, (20, 20, 40), rect, border_radius=4)
    pygame.draw.rect(p, col, rect, 1, border_radius=4)
    txt = f_chica.render("[P] Pausa", True, col)
    p.blit(txt, (bx + 10, by + 4))


def dibujar_ready(p, f_media, f_chica, num_jugadores, idx_p1, idx_p2):
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2
    txt = f_media.render("READY!", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, cy - 10)))
    sub = f"P1: {GHOST_NOMBRES[idx_p1]}"
    if num_jugadores == 2 and idx_p2 is not None:
        sub += f"  |  P2: {GHOST_NOMBRES[idx_p2]}"
    txt = f_chica.render(sub, True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(cx, cy + 25)))


def dibujar_stats(p, f_media, f_chica, f_grande,
                  stats, pacman, num_jugadores, idx_p1, idx_p2,
                  high_score, titulo, color_titulo):
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    p.blit(overlay, (0, 0))
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2

    txt = f_grande.render(titulo, True, color_titulo)
    p.blit(txt, txt.get_rect(center=(cx, cy - 130)))

    # Nuevo record?
    es_record = pacman.puntuacion >= high_score and pacman.puntuacion > 0
    if es_record:
        y = cy - 95
        t = pygame.time.get_ticks()
        brillo = 0.6 + 0.4 * abs((t % 1000) / 500 - 1)
        col_rec = (int(255 * brillo), int(255 * brillo), 0)
        txt = f_media.render("NUEVO RECORD!", True, col_rec)
        p.blit(txt, txt.get_rect(center=(cx, y)))

    y = cy - 70
    lineas = [
        (f"Puntos: {pacman.puntuacion}", BLANCO),
        (f"High Score: {max(high_score, pacman.puntuacion)}", AMARILLO),
        (f"Dots: {stats['dots']}/{stats['total_dots']}", (180, 180, 200)),
        (f"Power pellets: {stats['power_pellets']}/4", (180, 180, 200)),
        (f"Fantasmas comidos: {stats['fantasmas_comidos']}", (180, 180, 200)),
        (f"P1: {GHOST_NOMBRES[idx_p1]}  |  "
         f"{NOMBRES_DIFICULTAD[pacman.dificultad]}",
         COLORES_DIFICULTAD[pacman.dificultad]),
        (f"Tiempo: {format_tiempo(stats['tiempo_frames'])}", (180, 180, 200)),
    ]
    if num_jugadores == 2 and idx_p2 is not None:
        lineas.insert(5, (f"P2: {GHOST_NOMBRES[idx_p2]}",
                          GHOST_COLORES[idx_p2]))
    for texto, color in lineas:
        txt = f_chica.render(texto, True, color)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += 22

    y += 10
    pygame.draw.line(p, AZUL_PARED, (cx - 120, y), (cx + 120, y), 1)
    y += 12
    txt = f_chica.render("R: menu  |  ESC: salir", True, (100, 100, 120))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# MAIN
# ============================================================

def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()

    window_w, window_h = ANCHO, ALTO
    pantalla = pygame.display.set_mode(
        (window_w, window_h), pygame.RESIZABLE)
    pygame.display.set_caption("Pac-Scape")

    buffer = pygame.Surface((ANCHO, ALTO))
    reloj = pygame.time.Clock()
    f_grande = pygame.font.Font(None, 52)
    f_media  = pygame.font.Font(None, 30)
    f_chica  = pygame.font.Font(None, 22)
    f_popup  = pygame.font.Font(None, 26)
    sonidos = Sonidos()

    ias_pacman = {
        DIFIC_TONTA: ia_pacman_tonta,
        DIFIC_TEMEROSA: ia_pacman_temerosa,
        DIFIC_ASTUTA: ia_pacman_astuta,
        DIFIC_MAESTRA: ia_pacman_maestra,
    }
    CLYDE_ESQUINA = (1, 29)

    fullscreen = False
    estado = ESTADO_MENU
    menu_paso = MENU_PASO_JUGADORES
    num_jugadores = 2
    sel_ghost_p1 = 0
    sel_ghost_p2 = 1
    sel_dificultad = DIFIC_TONTA
    pausa_sel = 0

    high_score = cargar_high_score()

    mapa = pacman = fantasmas = None
    fantasma_p1 = fantasma_p2 = None
    idx_p1 = idx_p2 = 0
    streak_comer = 0
    power_timer = 0
    timer_estado = 0
    stats = {}

    # Nuevas variables de juego
    fruta = None
    fruta_aparecio = False
    popups = []

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

            elif evento.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    window_w, window_h = evento.w, evento.h
                    pantalla = pygame.display.set_mode(
                        (window_w, window_h), pygame.RESIZABLE)

            elif evento.type == pygame.KEYDOWN:
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

                if estado == ESTADO_MENU:
                    if menu_paso == MENU_PASO_JUGADORES:
                        if evento.key in (pygame.K_a, pygame.K_LEFT):
                            if num_jugadores > 1:
                                num_jugadores = 1
                        elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                            if num_jugadores < 2:
                                num_jugadores = 2
                                for i in range(4):
                                    if i != sel_ghost_p1:
                                        sel_ghost_p2 = i
                                        break
                        elif evento.key == pygame.K_RETURN:
                            menu_paso = MENU_PASO_FANTASMAS
                        elif evento.key == pygame.K_ESCAPE:
                            corriendo = False

                    elif menu_paso == MENU_PASO_FANTASMAS:
                        if evento.key in (pygame.K_a, pygame.K_LEFT):
                            new = (sel_ghost_p1 - 1) % 4
                            if num_jugadores == 2:
                                while new == sel_ghost_p2:
                                    new = (new - 1) % 4
                            sel_ghost_p1 = new
                        elif evento.key in (pygame.K_d, pygame.K_RIGHT):
                            new = (sel_ghost_p1 + 1) % 4
                            if num_jugadores == 2:
                                while new == sel_ghost_p2:
                                    new = (new + 1) % 4
                            sel_ghost_p1 = new
                        if num_jugadores == 2:
                            if evento.key == pygame.K_UP:
                                new = (sel_ghost_p2 - 1) % 4
                                while new == sel_ghost_p1:
                                    new = (new - 1) % 4
                                sel_ghost_p2 = new
                            elif evento.key == pygame.K_DOWN:
                                new = (sel_ghost_p2 + 1) % 4
                                while new == sel_ghost_p1:
                                    new = (new + 1) % 4
                                sel_ghost_p2 = new
                        if evento.key == pygame.K_RETURN:
                            menu_paso = MENU_PASO_DIFICULTAD
                        elif evento.key == pygame.K_ESCAPE:
                            menu_paso = MENU_PASO_JUGADORES

                    elif menu_paso == MENU_PASO_DIFICULTAD:
                        if evento.key in (pygame.K_w, pygame.K_UP):
                            sel_dificultad = (sel_dificultad - 1) % 4
                        elif evento.key in (pygame.K_s, pygame.K_DOWN):
                            sel_dificultad = (sel_dificultad + 1) % 4
                        elif evento.key == pygame.K_RETURN:
                            idx_p1 = sel_ghost_p1
                            idx_p2 = sel_ghost_p2 if num_jugadores == 2 else None
                            mapa, pacman, fantasmas, fantasma_p1, fantasma_p2 = \
                                crear_juego(sel_dificultad, idx_p1, idx_p2)
                            streak_comer = 0
                            power_timer = 0
                            stats = stats_vacias(mapa)
                            fruta = None
                            fruta_aparecio = False
                            popups = []
                            timer_estado = TIEMPO_LISTO
                            estado = ESTADO_LISTO
                            sonidos.play_ready()
                        elif evento.key == pygame.K_ESCAPE:
                            menu_paso = MENU_PASO_FANTASMAS

                elif estado == ESTADO_LISTO:
                    if evento.key == pygame.K_ESCAPE:
                        menu_paso = MENU_PASO_DIFICULTAD
                        estado = ESTADO_MENU

                elif estado == ESTADO_JUGANDO:
                    if evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        pausa_sel = 0
                        estado = ESTADO_PAUSA

                elif estado == ESTADO_PAUSA:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        pausa_sel = (pausa_sel - 1) % 3
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        pausa_sel = (pausa_sel + 1) % 3
                    elif evento.key == pygame.K_RETURN:
                        if pausa_sel == 0:
                            estado = ESTADO_JUGANDO
                        elif pausa_sel == 1:
                            idx_p1 = sel_ghost_p1
                            idx_p2 = sel_ghost_p2 if num_jugadores == 2 else None
                            mapa, pacman, fantasmas, fantasma_p1, fantasma_p2 = \
                                crear_juego(sel_dificultad, idx_p1, idx_p2)
                            streak_comer = 0
                            power_timer = 0
                            stats = stats_vacias(mapa)
                            fruta = None
                            fruta_aparecio = False
                            popups = []
                            timer_estado = TIEMPO_LISTO
                            estado = ESTADO_LISTO
                            sonidos.play_ready()
                        elif pausa_sel == 2:
                            menu_paso = MENU_PASO_DIFICULTAD
                            estado = ESTADO_MENU
                    elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        estado = ESTADO_JUGANDO

                elif estado in (ESTADO_GAME_OVER, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        menu_paso = MENU_PASO_DIFICULTAD
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

            # P1
            if teclas[pygame.K_w] or (
                    num_jugadores == 1 and teclas[pygame.K_UP]):
                fantasma_p1.direccion_siguiente = ARRIBA
            elif teclas[pygame.K_s] or (
                    num_jugadores == 1 and teclas[pygame.K_DOWN]):
                fantasma_p1.direccion_siguiente = ABAJO
            elif teclas[pygame.K_a] or (
                    num_jugadores == 1 and teclas[pygame.K_LEFT]):
                fantasma_p1.direccion_siguiente = IZQUIERDA
            elif teclas[pygame.K_d] or (
                    num_jugadores == 1 and teclas[pygame.K_RIGHT]):
                fantasma_p1.direccion_siguiente = DERECHA

            # P2
            if num_jugadores == 2 and fantasma_p2:
                if teclas[pygame.K_UP]:
                    fantasma_p2.direccion_siguiente = ARRIBA
                elif teclas[pygame.K_DOWN]:
                    fantasma_p2.direccion_siguiente = ABAJO
                elif teclas[pygame.K_LEFT]:
                    fantasma_p2.direccion_siguiente = IZQUIERDA
                elif teclas[pygame.K_RIGHT]:
                    fantasma_p2.direccion_siguiente = DERECHA

            # IA Pac-Man
            ias_pacman[sel_dificultad](pacman, mapa, fantasmas)

            # IA fantasmas no controlados
            for f in fantasmas:
                if f is fantasma_p1 or f is fantasma_p2:
                    continue
                aplicar_ia_fantasma(f, pacman, mapa, fantasmas,
                                    CLYDE_ESQUINA)

            # Updates
            pacman.update(mapa)
            for f in fantasmas:
                f.update(mapa)

            # Sonidos de comer
            if pacman.comio_punto:
                stats['dots'] += 1
                sonidos.chomp()
            if pacman.comio_power:
                stats['power_pellets'] += 1
                sonidos.play_power()

            # Power mode
            if pacman.activar_power:
                pacman.activar_power = False
                for f in fantasmas:
                    f.poner_asustado(TIEMPO_ASUSTADO)
                streak_comer = 0
                power_timer = TIEMPO_ASUSTADO

            if power_timer > 0:
                power_timer -= 1

            # ---- FRUTA ----
            if not fruta_aparecio and fruta is None:
                dots_comidos = stats['total_dots'] - mapa.puntos_restantes
                if dots_comidos >= int(stats['total_dots'] * FRUTA_UMBRAL):
                    tipo = random.randint(0, len(FRUTA_DATOS) - 1)
                    nombre, color, puntos = FRUTA_DATOS[tipo]
                    fruta = Fruta(nombre, color, puntos, *FRUTA_POSICION)
                    fruta_aparecio = True

            if fruta:
                fruta.update()
                if not fruta.activa:
                    fruta = None
                elif colisionan(pacman, fruta):
                    pacman.puntuacion += fruta.puntos
                    popups.append(PopUp(fruta.x, fruta.y,
                                        f"+{fruta.puntos}", fruta.color))
                    sonidos.play_fruta()
                    fruta = None

            # ---- COLISIONES ----
            for f in fantasmas:
                if not f.activo or f.ojos_solo or f.esperando:
                    continue
                if not colisionan(pacman, f):
                    continue
                if f.asustado:
                    pts = FANTASMA_PTS[min(streak_comer,
                                          len(FANTASMA_PTS) - 1)]
                    pacman.puntuacion += pts
                    # Pop-up en la posicion del fantasma
                    popups.append(PopUp(f.x, f.y, f"+{pts}", BLANCO))
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

            # ---- POP-UPS ----
            for pu in popups:
                pu.update()
            popups = [pu for pu in popups if pu.activo]

            # Victoria
            if mapa.puntos_restantes <= 0:
                estado = ESTADO_VICTORIA

        elif estado == ESTADO_MURIENDO:
            pacman.update(mapa)
            for pu in popups:
                pu.update()
            popups = [pu for pu in popups if pu.activo]
            timer_estado -= 1
            if timer_estado <= 0:
                if pacman.vidas <= 0:
                    # Guardar high score
                    if pacman.puntuacion > high_score:
                        high_score = pacman.puntuacion
                        guardar_high_score(high_score)
                    estado = ESTADO_GAME_OVER
                else:
                    pacman.reiniciar_posicion()
                    for f in fantasmas:
                        f.reiniciar()
                    power_timer = 0
                    streak_comer = 0
                    fruta = None
                    fruta_aparecio = False
                    timer_estado = TIEMPO_LISTO
                    estado = ESTADO_LISTO
                    sonidos.play_ready()

        elif estado == ESTADO_VICTORIA:
            if pacman.puntuacion > high_score:
                high_score = pacman.puntuacion
                guardar_high_score(high_score)

        # ============ RENDER ============
        buffer.fill(NEGRO)

        if estado == ESTADO_MENU:
            if menu_paso == MENU_PASO_JUGADORES:
                dibujar_menu_paso_jugadores(
                    buffer, f_grande, f_media, f_chica,
                    num_jugadores, high_score)
            elif menu_paso == MENU_PASO_FANTASMAS:
                dibujar_menu_paso_fantasmas(
                    buffer, f_grande, f_media, f_chica,
                    num_jugadores, sel_ghost_p1, sel_ghost_p2)
            elif menu_paso == MENU_PASO_DIFICULTAD:
                dibujar_menu_paso_dificultad(
                    buffer, f_grande, f_media, f_chica,
                    num_jugadores, sel_dificultad,
                    sel_ghost_p1, sel_ghost_p2)
        else:
            mapa.render(buffer)
            pacman.render(buffer)
            for f in fantasmas:
                f.render(buffer)

            # Fruta
            if fruta and fruta.activa:
                fruta.render(buffer)

            # Pop-ups
            for pu in popups:
                pu.render(buffer, f_popup)

            dibujar_hud(buffer, f_media, f_chica, pacman, mapa,
                        power_timer, sel_dificultad, num_jugadores,
                        idx_p1, idx_p2, high_score)

            if estado in (ESTADO_JUGANDO, ESTADO_LISTO):
                dibujar_boton_pausa(buffer, f_chica)
            if estado == ESTADO_LISTO:
                dibujar_ready(buffer, f_media, f_chica,
                              num_jugadores, idx_p1, idx_p2)
            elif estado == ESTADO_PAUSA:
                dibujar_pausa(buffer, f_media, f_chica, f_grande, pausa_sel)
            elif estado == ESTADO_GAME_OVER:
                dibujar_stats(buffer, f_media, f_chica, f_grande,
                              stats, pacman, num_jugadores,
                              idx_p1, idx_p2, high_score,
                              "GAME OVER", (255, 0, 0))
            elif estado == ESTADO_VICTORIA:
                dibujar_stats(buffer, f_media, f_chica, f_grande,
                              stats, pacman, num_jugadores,
                              idx_p1, idx_p2, high_score,
                              "VICTORIA!", AMARILLO)

        scaled, offx, offy = escalar_a_ventana(buffer, window_w, window_h)
        pantalla.fill(NEGRO)
        pantalla.blit(scaled, (offx, offy))
        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()