"""
Maneja toda la Interfaz Grafica del Usuario (GUI).
Aqui se dibujan los menus, el HUD, los textos flotantes y las pantallas de finalizacion.
"""
import pygame
from constantes import *
from utils import format_tiempo, obtener_duracion_power

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

