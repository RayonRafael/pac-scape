"""
Funciones utilitarias y genericas.
Incluye el formateo del tiempo, el sistema de guardado del High Score y comprobacion de colisiones.
"""
import pygame
import json
import os
from constantes import *

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

def obtener_duracion_power(nivel):
    return max(NIVEL_PODER_MINIMO,
               TIEMPO_ASUSTADO - (nivel - 1) * NIVEL_PODER_REDUCCION)

def obtener_fruta_nivel(nivel):
    idx = (nivel - 1) % len(NIVEL_FRUTAS)
    return NIVEL_FRUTAS[idx]

