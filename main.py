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
import efectos

Mapa._construir_paredes = efectos.construir_paredes_retro

# ============================================================
# CLASES AUXILIARES
# ============================================================

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


# ============================================================
# HIGH SCORE
# ============================================================

def cargar_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f).get("high_score", 0)
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
    # Escalar manteniendo la relacion de aspecto para evitar deformacion
    escala = min(vw / ANCHO, vh / ALTO)
    nw = int(ANCHO * escala)
    nh = int(ALTO * escala)
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
        f = Fantasma(col, fila, VEL_FANTASMA, GHOST_COLORES[i],
                     GHOST_NOMBRES[i], SALIDA_DELAYS[i])
        fantasmas.append(f)
        
    fantasmas[idx_p1].es_jugador = True
    fantasmas[idx_p1].salida_delay_inicial = 0
    fantasmas[idx_p1].timer_salida = 0
    
    if idx_p2 is not None:
        fantasmas[idx_p2].es_jugador = True
        fantasmas[idx_p2].salida_delay_inicial = 0
        fantasmas[idx_p2].timer_salida = 0
        
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


def dibujar_separador(p, cx, y, ancho=190):
    """Linea horizontal decorativa para dividir secciones."""
    pygame.draw.line(p, AZUL_PARED, (cx - ancho, y), (cx + ancho, y), 1)


def dibujar_pulso(p, fuente, texto, cx, y, color_base):
    """Texto que pulsa sutilmente (para botones)."""
    brillo = abs((pygame.time.get_ticks() % 1600) / 800 - 1)
    r = int(color_base[0] * (0.5 + brillo * 0.5))
    g = int(color_base[1] * (0.5 + brillo * 0.5))
    b = int(color_base[2] * (0.5 + brillo * 0.5))
    txt = fuente.render(texto, True, (r, g, b))
    p.blit(txt, txt.get_rect(center=(cx, y)))


def crear_nivel(nivel, dificultad, idx_p1, idx_p2, pacman):
    mapa = Mapa()
    fantasmas = []
    for i in range(4):
        col, fila = GHOST_INICIOS[i]
        fantasmas.append(
            Fantasma(col, fila, VEL_FANTASMA, GHOST_COLORES[i],
                     GHOST_NOMBRES[i], SALIDA_DELAYS[i]))
    fantasma_p1 = fantasmas[idx_p1]
    fantasma_p2 = fantasmas[idx_p2] if idx_p2 is not None else None
    pacman.x = PACMAN_INICIO[0] * TILE_SIZE + TILE_SIZE // 2
    pacman.y = PACMAN_INICIO[1] * TILE_SIZE + TILE_SIZE // 2
    pacman.direccion = IZQUIERDA
    pacman.direccion_siguiente = QUIETO
    pacman.muriendo = False
    pacman.frame_muerte = 0
    pacman.activar_power = False
    pacman.invincible = False
    pacman.tiempo_invencible = 0
    return mapa, fantasmas, fantasma_p1, fantasma_p2


def aplicar_elroy(fantasmas, mapa):
    blinky = next((f for f in fantasmas if f.nombre == "Blinky"), None)
    if not blinky or not blinky.activo or blinky.ojos_solo:
        return
    if not blinky.en_centro_tile():
        return
    if mapa.puntos_restantes <= ELROY_UMBRAL_2:
        blinky.velocidad = ELROY_VEL_2
    elif mapa.puntos_restantes <= ELROY_UMBRAL_1:
        blinky.velocidad = ELROY_VEL_1
    else:
        blinky.velocidad = VEL_FANTASMA


def obtener_duracion_power(nivel):
    return max(NIVEL_PODER_MINIMO,
               TIEMPO_ASUSTADO - (nivel - 1) * NIVEL_PODER_REDUCCION)


def obtener_fruta_nivel(nivel):
    idx = (nivel - 1) % len(NIVEL_FRUTAS)
    return NIVEL_FRUTAS[idx]


# ============================================================
# MENU PASO 1: JUGADORES
# ============================================================

def dibujar_menu_paso_jugadores(p, f_titulo, f_media, f_chica, num_jugadores, high_score, w, h):
    cx = w // 2
    sp = h / 20.0
    y = sp * 2
    
    txt = f_titulo.render("PAC-SCAPE", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += sp * 1.5
    txt = f_chica.render("4 FANTASMAS  vs  PAC-MAN IA", True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    if high_score > 0:
        y += sp * 0.8
        txt = f_chica.render(f"HIGH SCORE: {high_score}", True, AMARILLO)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp
    txt = f_chica.render("MODO DE JUEGO", True, (90, 90, 120))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp * 1.5
    flecha_col = (150, 150, 200)
    if num_jugadores > 1:
        txt = f_media.render("<", True, flecha_col)
        p.blit(txt, (cx - w*0.15, y - 4))
    if num_jugadores == 1:
        txt = f_media.render("1 JUGADOR", True, (100, 220, 255))
    else:
        txt = f_media.render("2 JUGADORES", True, (255, 220, 100))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    if num_jugadores < 2:
        txt = f_media.render(">", True, flecha_col)
        p.blit(txt, (cx + w*0.15 - 15, y - 4))
        
    y += sp
    txt = f_chica.render("A / D  para cambiar", True, (70, 70, 90))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp
    txt = f_chica.render("Fantasmas disponibles:", True, (90, 90, 120))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp * 2
    gap = w * 0.15
    start_x = cx - (gap * 3) // 2
    for i in range(4):
        fx = start_x + i * gap
        dibujar_fantasma_mini(p, fx, y, int(h * 0.05), GHOST_COLORES[i])
        txt = f_chica.render(GHOST_NOMBRES[i], True, GHOST_COLORES[i])
        p.blit(txt, txt.get_rect(center=(fx, y + sp*1.5)))
        
    y += sp * 3
    txt = f_chica.render(f"{GHOST_ROLES[0]} | {GHOST_ROLES[1]} | {GHOST_ROLES[2]} | {GHOST_ROLES[3]}", True, (70, 70, 90))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp
    txt = f_chica.render("Los otros seran controlados por IA", True, (100, 100, 130))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp * 1.5
    dibujar_pulso(p, f_media, "ENTER  continuar", cx, y, (255, 255, 0))
    y += sp
    txt = f_chica.render("ESC: salir  |  F11: pantalla completa", True, (50, 50, 70))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# MENU PASO 2: FANTASMAS
# ============================================================

def dibujar_menu_paso_fantasmas(p, f_titulo, f_media, f_chica, num_jugadores, sel_p1, sel_p2, w, h):
    cx = w // 2
    sp = h / 20.0
    y = sp * 2
    
    txt = f_titulo.render("PAC-SCAPE", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += sp * 1.5
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp
    if num_jugadores == 1:
        txt = f_media.render("ELIGE TU FANTASMA", True, BLANCO)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += sp
        txt = f_chica.render("A / D  para navegar", True, (90, 90, 120))
        p.blit(txt, txt.get_rect(center=(cx, y)))
    else:
        txt = f_media.render("ELIGE TUS FANTASMAS", True, BLANCO)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += sp
        txt = f_chica.render("P1: A / D    P2: Flechas", True, (90, 90, 120))
        p.blit(txt, txt.get_rect(center=(cx, y)))
        
    y += sp * 1.5
    box_w = w * 0.18
    box_h = h * 0.25
    gap = w * 0.02
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
        
        if es_p1: borde_col, grosor = BLANCO, 3
        elif es_p2: borde_col, grosor = AMARILLO, 3
        else: borde_col, grosor = (40, 40, 60), 1
        pygame.draw.rect(p, borde_col, rect, grosor, border_radius=8)
        
        dibujar_fantasma_mini(p, bx, by + box_h * 0.3, int(h * 0.06), GHOST_COLORES[i])
        
        txt = f_media.render(GHOST_NOMBRES[i], True, GHOST_COLORES[i])
        p.blit(txt, txt.get_rect(center=(bx, by + box_h * 0.6)))
        
        txt = f_chica.render(GHOST_ROLES[i], True, (90, 90, 110))
        p.blit(txt, txt.get_rect(center=(bx, by + box_h * 0.8)))
        
        if es_p1: badge_col, badge_txt = BLANCO, "P1"
        elif es_p2: badge_col, badge_txt = AMARILLO, "P2"
        else: badge_col, badge_txt = (60, 60, 80), "IA"
        txt = f_chica.render(badge_txt, True, badge_col)
        p.blit(txt, txt.get_rect(center=(bx, by + box_h * 0.95)))
        
    y += box_h + sp
    dibujar_separador(p, cx, y, w * 0.3)
    y += sp
    
    if num_jugadores == 1:
        txt = f_chica.render(GHOST_DETALLES[sel_p1], True, GHOST_COLORES[sel_p1])
        p.blit(txt, txt.get_rect(center=(cx, y)))
    else:
        txt = f_chica.render(f"P1: {GHOST_DETALLES[sel_p1]}", True, GHOST_COLORES[sel_p1])
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += sp * 0.8
        txt = f_chica.render(f"P2: {GHOST_DETALLES[sel_p2]}", True, GHOST_COLORES[sel_p2])
        p.blit(txt, txt.get_rect(center=(cx, y)))
        
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    y += sp
    
    no_controlados = [GHOST_NOMBRES[i] for i in range(4) if i != sel_p1 and (num_jugadores == 1 or i != sel_p2)]
    txt = f_chica.render(f"IA controla: {', '.join(no_controlados)}", True, (100, 100, 130))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp * 1.5
    dibujar_pulso(p, f_media, "ENTER  continuar", cx, y, (255, 255, 0))
    y += sp
    txt = f_chica.render("ESC: volver", True, (50, 50, 70))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# MENU PASO 3: DIFICULTAD
# ============================================================

def dibujar_menu_paso_dificultad(p, f_titulo, f_media, f_chica, num_jugadores, sel_dificultad, idx_p1, idx_p2, w, h):
    cx = w // 2
    sp = h / 20.0
    y = sp * 2
    
    txt = f_titulo.render("PAC-SCAPE", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += sp * 1.5
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp
    texto_sel = f"P1: {GHOST_NOMBRES[idx_p1]}"
    if num_jugadores == 2 and idx_p2 is not None:
        texto_sel += f"  |  P2: {GHOST_NOMBRES[idx_p2]}"
    txt = f_chica.render(texto_sel, True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp
    txt = f_chica.render("DIFICULTAD PAC-MAN", True, (90, 90, 120))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp * 1.5
    box_w = w * 0.3
    for i, nombre in enumerate(NOMBRES_DIFICULTAD):
        col = COLORES_DIFICULTAD[i]
        rect = pygame.Rect(cx - box_w // 2, y - sp*0.5, box_w, sp)
        if i == sel_dificultad:
            pygame.draw.rect(p, (30, 30, 60), rect, border_radius=6)
            pygame.draw.rect(p, col, rect, 2, border_radius=6)
            txt = f_media.render(nombre, True, col)
        else:
            txt = f_media.render(nombre, True, (50, 50, 70))
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += sp * 1.5
        
    y += sp * 0.5
    txt = f_chica.render(DESCRIPCIONES[sel_dificultad], True, COLORES_DIFICULTAD[sel_dificultad])
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += sp
    txt = f_chica.render("W / S  para cambiar", True, (70, 70, 90))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    
    y += sp
    dibujar_separador(p, cx, y, w * 0.3)
    
    y += sp * 1.5
    dibujar_pulso(p, f_media, "ENTER  para jugar", cx, y, (255, 255, 0))
    y += sp
    txt = f_chica.render("ESC: volver", True, (50, 50, 70))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# PAUSA
# ============================================================

def dibujar_pausa(p, f_media, f_chica, f_titulo, seleccion):
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    p.blit(overlay, (0, 0))
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2
    txt = f_titulo.render("PAUSA", True, BLANCO)
    p.blit(txt, txt.get_rect(center=(cx, cy - 60)))
    dibujar_separador(p, cx, cy - 38, 100)
    y = cy - 15
    for i, opcion in enumerate(PAUSA_OPCIONES):
        col_op = AMARILLO if i == seleccion else (120, 120, 140)
        prefijo = "> " if i == seleccion else "  "
        txt = f_media.render(f"{prefijo}{opcion}", True, col_op)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += 34
    dibujar_separador(p, cx, y + 5, 100)
    y += 18
    txt = f_chica.render("W/S elegir | ENTER confirmar", True, (80, 80, 100))
    p.blit(txt, txt.get_rect(center=(cx, y)))
    y += 16
    txt = f_chica.render("ESC o P para reanudar", True, (80, 80, 100))
    p.blit(txt, txt.get_rect(center=(cx, y)))


# ============================================================
# HUD
# ============================================================

def dibujar_hud(p, f_media, f_chica, pacman, mapa, fantasmas,
                power_timer, dificultad, num_jugadores,
                idx_p1, idx_p2, high_score, nivel):
    y_base = MAPA_FILAS * TILE_SIZE
    pygame.draw.rect(p, HUD_BG, (0, y_base, ANCHO, HUD_ALTO))
    pygame.draw.line(p, AZUL_PARED, (0, y_base), (ANCHO, y_base), 2)

    # Izquierda: puntos + vidas
    txt = f_media.render(f"Puntos: {pacman.puntuacion}", True, BLANCO)
    p.blit(txt, (10, y_base + 3))
    for i in range(pacman.vidas):
        lx = 10 + i * 22
        ly = y_base + 32
        pygame.draw.circle(p, AMARILLO, (lx, ly), 7)
        pygame.draw.polygon(p, NEGRO, [
            (lx, ly), (lx + 9, ly - 4), (lx + 9, ly + 4)])

    # Centro
    p1_l = GHOST_NOMBRES[idx_p1][:3]
    if num_jugadores == 2 and idx_p2 is not None:
        p2_l = GHOST_NOMBRES[idx_p2][:3]
        centro1 = f"P1:{p1_l} P2:{p2_l} S{nivel}"
    else:
        centro1 = f"P1:{p1_l} S{nivel} 1J"
    txt = f_chica.render(centro1, True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(ANCHO // 2, y_base + 15)))
    txt = f_chica.render(f"Rest: {mapa.puntos_restantes}   HI: {high_score}", True, HUD_TEXTO)
    p.blit(txt, txt.get_rect(center=(ANCHO // 2, y_base + 35)))

    # Derecha: power bar o habilidades
    bar_x = ANCHO - 110
    bar_y = y_base + 6
    bar_w = 95
    bar_h = 6
    
    if power_timer > 0:
        dur_power = obtener_duracion_power(nivel)
        ratio = power_timer / dur_power
        pygame.draw.rect(p, (40, 40, 60),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(p, AMARILLO,
                         (bar_x, bar_y, int(bar_w * ratio), bar_h),
                         border_radius=3)
        txt = f_chica.render("POWER", True, AMARILLO)
        p.blit(txt, (bar_x + 26, bar_y + 8))
    else:
        # Cooldown P1
        f1 = fantasmas[idx_p1]
        ratio1 = 1.0 - (f1.cooldown_habilidad / f1.max_cooldown)
        col1 = GHOST_COLORES[idx_p1] if ratio1 == 1.0 else (80, 80, 80)
        pygame.draw.rect(p, (20, 20, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(p, col1, (bar_x, bar_y, int(bar_w * ratio1), bar_h), border_radius=3)
        txt = f_chica.render("DASH P1", True, col1)
        p.blit(txt, (bar_x + 22, bar_y + 8))
        
        # Cooldown P2
        if num_jugadores == 2 and idx_p2 is not None:
            bar_y += 20
            f2 = fantasmas[idx_p2]
            ratio2 = 1.0 - (f2.cooldown_habilidad / f2.max_cooldown)
            col2 = GHOST_COLORES[idx_p2] if ratio2 == 1.0 else (80, 80, 80)
            pygame.draw.rect(p, (20, 20, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            pygame.draw.rect(p, col2, (bar_x, bar_y, int(bar_w * ratio2), bar_h), border_radius=3)
            txt = f_chica.render("DASH P2", True, col2)
            p.blit(txt, (bar_x + 22, bar_y + 8))


def dibujar_boton_pausa(p, f_chica):
    bx = ANCHO - 82
    by = 6
    bw = 70
    bh = 20
    t = pygame.time.get_ticks()
    brillo = 0.6 + 0.4 * abs((t % 2000) / 1000 - 1)
    col = (int(100 * brillo), int(100 * brillo), int(160 * brillo))
    rect = pygame.Rect(bx, by, bw, bh)
    pygame.draw.rect(p, (20, 20, 40), rect, border_radius=4)
    pygame.draw.rect(p, col, rect, 1, border_radius=4)
    txt = f_chica.render("[P] Pausa", True, col)
    p.blit(txt, (bx + 8, by + 3))


# ============================================================
# OVERLAYS
# ============================================================

def dibujar_ready(p, f_media, f_chica, num_jugadores, idx_p1, idx_p2, nivel):
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2
    txt = f_media.render("READY!", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, cy - 12)))
    txt = f_chica.render(f"STAGE {nivel}", True, (150, 150, 180))
    p.blit(txt, txt.get_rect(center=(cx, cy + 8)))
    sub = f"P1: {GHOST_NOMBRES[idx_p1]}"
    if num_jugadores == 2 and idx_p2 is not None:
        sub += f"  |  P2: {GHOST_NOMBRES[idx_p2]}"
    txt = f_chica.render(sub, True, (120, 120, 150))
    p.blit(txt, txt.get_rect(center=(cx, cy + 26)))


def dibujar_nivel_completo(p, f_media, f_chica, f_titulo, nivel, puntuacion):
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    p.blit(overlay, (0, 0))
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2
    txt = f_titulo.render(f"STAGE {nivel}", True, AMARILLO)
    p.blit(txt, txt.get_rect(center=(cx, cy - 35)))
    txt = f_media.render("COMPLETE!", True, BLANCO)
    p.blit(txt, txt.get_rect(center=(cx, cy + 5)))
    txt = f_chica.render(f"Puntos: {puntuacion}", True, (180, 180, 200))
    p.blit(txt, txt.get_rect(center=(cx, cy + 30)))


def dibujar_stats(p, f_media, f_chica, f_titulo,
                  stats, pacman, num_jugadores, idx_p1, idx_p2,
                  high_score, nivel, titulo, color_titulo, game_over_sel=0):
    overlay = pygame.Surface((ANCHO, MAPA_FILAS * TILE_SIZE))
    overlay.set_alpha(180)
    overlay.fill(NEGRO)
    p.blit(overlay, (0, 0))
    cx = ANCHO // 2
    cy = MAPA_FILAS * TILE_SIZE // 2

    txt = f_titulo.render(titulo, True, color_titulo)
    p.blit(txt, txt.get_rect(center=(cx, cy - 145)))

    es_record = pacman.puntuacion >= high_score and pacman.puntuacion > 0
    if es_record:
        y = cy - 100
        t = pygame.time.get_ticks()
        brillo = 0.6 + 0.4 * abs((t % 1000) / 500 - 1)
        col_rec = (int(255 * brillo), int(255 * brillo), 0)
        txt = f_media.render("NUEVO RECORD!", True, col_rec)
        p.blit(txt, txt.get_rect(center=(cx, y)))

    y = cy - 65
    lineas = [
        (f"Puntos: {pacman.puntuacion}", BLANCO),
        (f"Dots: {stats['dots']}/{stats['total_dots']}", (180, 180, 200)),
        (f"Fantasmas: {stats['fantasmas_comidos']}", (180, 180, 200)),
        (f"P1: {GHOST_NOMBRES[idx_p1]} | "
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
        y += 20

    y += 8
    dibujar_separador(p, cx, y, 120)
    y += 12
    opciones = ["Volver a jugar", "Menu principal", "Salir"]
    for i, op in enumerate(opciones):
        col = AMARILLO if i == game_over_sel else (100, 100, 120)
        pref = "> " if i == game_over_sel else "  "
        txt = f_chica.render(f"{pref}{op}", True, col)
        p.blit(txt, txt.get_rect(center=(cx, y)))
        y += 20


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
    buffer = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    reloj = pygame.time.Clock()

    # Fuentes: una para titulo, una para texto normal, una para texto pequeno
    try:
        f_titulo = pygame.font.SysFont("impact", 54)
        f_media  = pygame.font.SysFont("arial", 28, bold=True)
        f_chica  = pygame.font.SysFont("arial", 20)
        f_popup  = pygame.font.SysFont("impact", 24)
    except:
        f_titulo = pygame.font.Font(None, 54)
        f_media  = pygame.font.Font(None, 28)
        f_chica  = pygame.font.Font(None, 20)
        f_popup  = pygame.font.Font(None, 24)
        
    sonidos = Sonidos()
    gestor_particulas = efectos.GestorParticulas()
    shake_frames = 0

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
    nivel = 1
    streak_comer = 0
    power_timer = 0
    timer_estado = 0
    stats = {}
    fruta = None
    fruta_aparecio = False
    popups = []
    game_over_sel = 0

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
                            nivel = 1
                            idx_p1 = sel_ghost_p1
                            idx_p2 = (sel_ghost_p2
                                      if num_jugadores == 2 else None)
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
                        sonidos.detener_siren()
                        menu_paso = MENU_PASO_DIFICULTAD
                        estado = ESTADO_MENU

                elif estado == ESTADO_JUGANDO:
                    if evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        sonidos.detener_siren()
                        pausa_sel = 0
                        estado = ESTADO_PAUSA

                elif estado == ESTADO_NIVEL_COMPLETO:
                    pass

                elif estado == ESTADO_PAUSA:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        pausa_sel = (pausa_sel - 1) % 3
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        pausa_sel = (pausa_sel + 1) % 3
                    elif evento.key == pygame.K_RETURN:
                        if pausa_sel == 0:
                            estado = ESTADO_JUGANDO
                        elif pausa_sel == 1:
                            nivel = 1
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
                            sonidos.detener_siren()
                            menu_paso = MENU_PASO_DIFICULTAD
                            estado = ESTADO_MENU
                    elif evento.key in (pygame.K_ESCAPE, pygame.K_p):
                        estado = ESTADO_JUGANDO

                elif estado == ESTADO_GAME_OVER:
                    if evento.key in (pygame.K_w, pygame.K_UP):
                        game_over_sel = (game_over_sel - 1) % 3
                        sonidos.chomp()
                    elif evento.key in (pygame.K_s, pygame.K_DOWN):
                        game_over_sel = (game_over_sel + 1) % 3
                        sonidos.chomp()
                    elif evento.key == pygame.K_RETURN:
                        sonidos.detener_siren()
                        if game_over_sel == 0:
                            # Volver a jugar
                            mapa, pacman, fantasmas, fantasma_p1, fantasma_p2 = crear_juego(
                                sel_dificultad, idx_p1, idx_p2 if num_jugadores == 2 else None)
                            nivel = 1
                            streak_comer = 0
                            power_timer = 0
                            stats = stats_vacias(mapa)
                            fruta = None
                            fruta_aparecio = False
                            popups = []
                            estado = ESTADO_LISTO
                            timer_estado = TIEMPO_LISTO
                            sonidos.play_ready()
                        elif game_over_sel == 1:
                            menu_paso = MENU_PASO_JUGADORES
                            estado = ESTADO_MENU
                        elif game_over_sel == 2:
                            corriendo = False
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

            # Habilidades
            if num_jugadores >= 1 and fantasma_p1:
                if teclas[pygame.K_SPACE]:
                    fantasma_p1.usar_habilidad(mapa)
            if num_jugadores == 2 and fantasma_p2:
                if teclas[pygame.K_RETURN] or teclas[pygame.K_RSHIFT]:
                    fantasma_p2.usar_habilidad(mapa)

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

            if num_jugadores == 2 and fantasma_p2:
                if teclas[pygame.K_UP]:
                    fantasma_p2.direccion_siguiente = ARRIBA
                elif teclas[pygame.K_DOWN]:
                    fantasma_p2.direccion_siguiente = ABAJO
                elif teclas[pygame.K_LEFT]:
                    fantasma_p2.direccion_siguiente = IZQUIERDA
                elif teclas[pygame.K_RIGHT]:
                    fantasma_p2.direccion_siguiente = DERECHA

            ias_pacman[sel_dificultad](pacman, mapa, fantasmas)
            for f in fantasmas:
                if f is fantasma_p1 or f is fantasma_p2:
                    continue
                aplicar_ia_fantasma(f, pacman, mapa, fantasmas,
                                    CLYDE_ESQUINA)

            aplicar_elroy(fantasmas, mapa)

            if power_timer > 0:
                sonidos.iniciar_siren_power()
            else:
                sonidos.iniciar_siren_normal()

            pacman.update(mapa)
            for f in fantasmas:
                f.update(mapa)

            if pacman.comio_punto:
                stats['dots'] += 1
                sonidos.chomp()
                gestor_particulas.emitir(pacman.x, pacman.y, PUNTO_COLOR, 3)
            if pacman.comio_power:
                stats['power_pellets'] += 1
                sonidos.play_power()
                gestor_particulas.emitir(pacman.x, pacman.y, AMARILLO, 10)

            if pacman.activar_power:
                pacman.activar_power = False
                dur_power = obtener_duracion_power(nivel)
                for f in fantasmas:
                    f.poner_asustado(dur_power)
                streak_comer = 0
                power_timer = dur_power

            if power_timer > 0:
                power_timer -= 1

            if not fruta_aparecio and fruta is None:
                dots_comidos = stats['total_dots'] - mapa.puntos_restantes
                if dots_comidos >= int(stats['total_dots'] * FRUTA_UMBRAL):
                    nombre, color, puntos = obtener_fruta_nivel(nivel)
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

            for f in fantasmas:
                if not f.activo or f.ojos_solo or f.esperando:
                    continue
                if not colisionan(pacman, f):
                    continue
                if f.asustado:
                    pts = FANTASMA_PTS[min(streak_comer,
                                          len(FANTASMA_PTS) - 1)]
                    pacman.puntuacion += pts
                    popups.append(PopUp(f.x, f.y, f"+{pts}", BLANCO))
                    f.ser_comido()
                    streak_comer += 1
                    stats['fantasmas_comidos'] += 1
                    sonidos.play_eat_ghost()
                    shake_frames = 8
                elif not pacman.invincible:
                    pacman.registrar_muerte()
                    pacman.vidas -= 1
                    pacman.iniciar_muerte()
                    sonidos.detener_siren()
                    sonidos.play_death()
                    estado = ESTADO_MURIENDO
                    timer_estado = TIEMPO_MURIENDO
                    shake_frames = 20
                    break

            for pu in popups:
                pu.update()
            popups = [pu for pu in popups if pu.activo]

            if mapa.puntos_restantes <= 0:
                sonidos.detener_siren()
                # Victoria de Pac-Man
                if pacman.puntuacion > high_score:
                    high_score = pacman.puntuacion
                    guardar_high_score(high_score)
                estado = ESTADO_GAME_OVER
                timer_estado = 0
                game_over_sel = 0

        elif estado == ESTADO_MURIENDO:
            pacman.update(mapa)
            for pu in popups:
                pu.update()
            popups = [pu for pu in popups if pu.activo]
            timer_estado -= 1
            if timer_estado <= 0:
                if pacman.vidas <= 0:
                    if pacman.puntuacion > high_score:
                        high_score = pacman.puntuacion
                        guardar_high_score(high_score)
                    sonidos.detener_siren()
                    estado = ESTADO_GAME_OVER
                    game_over_sel = 0
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

        # ============ RENDER ============
        # Fondo estilo retro cubriendo toda la ventana (se dibuja SIEMPRE)
        efectos.dibujar_grid_fondo(pantalla, window_w, window_h, (25, 25, 60))

        if estado == ESTADO_MENU:
            if menu_paso == MENU_PASO_JUGADORES:
                dibujar_menu_paso_jugadores(
                    pantalla, f_titulo, f_media, f_chica,
                    num_jugadores, high_score, window_w, window_h)
            elif menu_paso == MENU_PASO_FANTASMAS:
                dibujar_menu_paso_fantasmas(
                    pantalla, f_titulo, f_media, f_chica,
                    num_jugadores, sel_ghost_p1, sel_ghost_p2, window_w, window_h)
            elif menu_paso == MENU_PASO_DIFICULTAD:
                dibujar_menu_paso_dificultad(
                    pantalla, f_titulo, f_media, f_chica,
                    num_jugadores, sel_dificultad,
                    sel_ghost_p1, sel_ghost_p2, window_w, window_h)
        else:
            buffer.fill((0, 0, 0, 0))
            mapa.render(buffer)
            gestor_particulas.update()
            gestor_particulas.render(buffer)
            
            efectos.dibujar_aura(buffer, pacman.x, pacman.y, pacman.radio + 12, AMARILLO, GLOW_ALPHA_PACMAN)
            pacman.render(buffer)
            
            for f in fantasmas:
                if f.activo and not f.ojos_solo:
                    efectos.dibujar_aura(buffer, f.x, f.y, 18, f.color, GLOW_ALPHA_GHOST)
                f.render(buffer)
                if f.ojos_solo and f.es_jugador:
                    t = pygame.time.get_ticks()
                    if (t // 300) % 2 == 0:
                        txt = f_chica.render("REVIVIENDO...", True, BLANCO)
                        buffer.blit(txt, txt.get_rect(center=(f.x, f.y - 15)))
                
            if fruta and fruta.activa:
                fruta.render(buffer)
            for pu in popups:
                pu.render(buffer, f_popup)
            dibujar_hud(buffer, f_media, f_chica, pacman, mapa, fantasmas,
                        power_timer, sel_dificultad, num_jugadores,
                        idx_p1, idx_p2, high_score, nivel)
            if estado in (ESTADO_JUGANDO, ESTADO_LISTO):
                dibujar_boton_pausa(buffer, f_chica)
            if estado == ESTADO_LISTO:
                dibujar_ready(buffer, f_media, f_chica,
                              num_jugadores, idx_p1, idx_p2, nivel)
            elif estado == ESTADO_PAUSA:
                dibujar_pausa(buffer, f_media, f_chica, f_titulo, pausa_sel)
            elif estado == ESTADO_NIVEL_COMPLETO:
                dibujar_nivel_completo(
                    buffer, f_media, f_chica, f_titulo,
                    nivel - 1, pacman.puntuacion)
            elif estado == ESTADO_GAME_OVER:
                if pacman.vidas <= 0:
                    mensaje_victoria = "¡TÚ GANAS!"
                    color_victoria = ROSA
                else:
                    mensaje_victoria = "¡TÚ PERDISTE!"
                    color_victoria = (255, 50, 50)
                    
                dibujar_stats(buffer, f_media, f_chica, f_titulo,
                              stats, pacman, num_jugadores,
                              idx_p1, idx_p2, high_score, nivel,
                              mensaje_victoria, color_victoria, game_over_sel)

            scaled, offx, offy = escalar_a_ventana(buffer, window_w, window_h)
            
            # Screen Shake
            sx = random.randint(-6, 6) if shake_frames > 0 else 0
            sy = random.randint(-6, 6) if shake_frames > 0 else 0
            if shake_frames > 0:
                shake_frames -= 1
                
            pantalla.blit(scaled, (offx + sx, offy + sy))
        
        # Efecto CRT sutil (scanlines)
        if hasattr(efectos, 'crt_overlay') and (efectos.crt_overlay.get_size() != (window_w, window_h)):
            efectos.crt_overlay = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
            for i in range(0, window_h, 3):
                pygame.draw.line(efectos.crt_overlay, (0, 0, 0, 40), (0, i), (window_w, i), 1)
        elif not hasattr(efectos, 'crt_overlay'):
            efectos.crt_overlay = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
            for i in range(0, window_h, 3):
                pygame.draw.line(efectos.crt_overlay, (0, 0, 0, 40), (0, i), (window_w, i), 1)
                
        pantalla.blit(efectos.crt_overlay, (0, 0))
        
        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()