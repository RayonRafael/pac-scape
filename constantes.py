# ============================================================
# constantes.py — Todos los valores tunables del juego
# ============================================================

# --- Ventana y grilla ---
TILE_SIZE   = 24
MAPA_COLS   = 28
MAPA_FILAS  = 31
HUD_ALTO    = 50
ANCHO       = MAPA_COLS * TILE_SIZE              # 672
ALTO        = MAPA_FILAS * TILE_SIZE + HUD_ALTO  # 794
FPS         = 60

# --- Simbolos del mapa ---
PARED  = '#'
PUNTO  = '.'
POWER  = 'o'
VACIO  = ' '
PUERTA = '-'

# --- Colores ---
NEGRO         = (0, 0, 0)
PARED_RELLENO = (5, 5, 40)
AZUL_PARED    = (33, 33, 222)
AMARILLO      = (255, 255, 0)
BLANCO        = (255, 255, 255)
ROSA          = (255, 184, 255)
PUNTO_COLOR   = (255, 183, 174)
HUD_BG        = (15, 15, 35)
HUD_TEXTO     = (180, 180, 200)

# --- Velocidad (px/frame, debe dividir a TILE_SIZE) ---
VEL_PACMAN = 2

# --- Direcciones como (dx, dy) en tiles ---
ARRIBA    = (0, -1)
ABAJO     = (0, 1)
IZQUIERDA = (-1, 0)
DERECHA   = (1, 0)
QUIETO    = (0, 0)