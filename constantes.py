# ============================================================
# constantes.py
# ============================================================

# --- Ventana y grilla ---
TILE_SIZE   = 24
MAPA_COLS   = 28
MAPA_FILAS  = 31
HUD_ALTO    = 50
ANCHO       = MAPA_COLS * TILE_SIZE
ALTO        = MAPA_FILAS * TILE_SIZE + HUD_ALTO
FPS         = 60

# --- Simbolos del mapa ---
PARED  = '#'
PUNTO  = '.'
POWER  = 'o'
VACIO  = ' '
PUERTA = '-'

# --- Colores generales ---
NEGRO         = (0, 0, 0)
PARED_RELLENO = (5, 5, 40)
AZUL_PARED    = (33, 33, 222)
AMARILLO      = (255, 255, 0)
BLANCO        = (255, 255, 255)
ROSA          = (255, 184, 255)
PUNTO_COLOR   = (255, 183, 174)
HUD_BG        = (15, 15, 35)
HUD_TEXTO     = (180, 180, 200)

# --- Colores de fantasmas ---
BLINKY_COLOR  = (255, 0, 0)
PINKY_COLOR   = (255, 184, 255)
INKY_COLOR    = (0, 255, 255)
CLYDE_COLOR   = (255, 184, 81)
ASUSTADO_COLOR = (33, 33, 222)
PUPILA_COLOR  = (33, 33, 100)

# --- Velocidad (px/frame, divide TILE_SIZE) ---
VEL_PACMAN   = 2
VEL_FANTASMA = 2

# --- Direcciones (dx, dy) en tiles ---
ARRIBA    = (0, -1)
ABAJO     = (0, 1)
IZQUIERDA = (-1, 0)
DERECHA   = (1, 0)
QUIETO    = (0, 0)

# --- Duraciones (frames a 60fps) ---
TIEMPO_ASUSTADO     = 480
TIEMPO_INVENCIBLE   = 180
TIEMPO_DESAPARECIDO = 300

# --- Game states ---
ESTADO_MENU      = "menu"
ESTADO_JUGANDO   = "jugando"
ESTADO_GAME_OVER = "game_over"
ESTADO_VICTORIA  = "victoria"

# --- Posiciones iniciales (col, fila) ---
PACMAN_INICIO = (14, 23)
BLINKY_INICIO = (14, 5)
PINKY_INICIO  = (6, 29)
INKY_INICIO   = (21, 5)
CLYDE_INICIO  = (21, 29)

# --- Puntuacion ---
PUNTO_PTS    = 10
POWER_PTS    = 50
FANTASMA_PTS = [200, 400, 800, 1600]

# --- Dificultades Pac-Man ---
DIFIC_TONTA     = 0
DIFIC_TEMEROSA  = 1
DIFIC_ASTUTA    = 2
DIFIC_MAESTRA   = 3
NOMBRES_DIFICULTAD = ["Tonta", "Temerosa", "Astuta", "Maestra"]
COLORES_DIFICULTAD = [
    (100, 255, 100),   # verde
    (255, 255, 100),   # amarillo
    (255, 160, 60),    # naranja
    (255, 60, 60),     # rojo
]
DESCRIPCIONES = [
    "Solo esquiva paredes",
    "Huye si un fantasma esta cerca",
    "Pathfinding + evita fantasmas",
    "Memoriza zonas de peligro",
]