"""
Archivo principal del juego Pac-Scape.
Contiene el bucle principal (Game Loop), el manejo de eventos (teclado) y la Maquina de Estados 
(Menu, Jugando, Pausa, Game Over).
"""
from objetos import PopUp, Fruta
from utils import *
from ui import *
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

