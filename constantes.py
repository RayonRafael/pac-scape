# ============================================================
# constantes.py
# ============================================================

TILE_SIZE   = 24
MAPA_COLS   = 28
MAPA_FILAS  = 31
HUD_ALTO    = 50
ANCHO       = MAPA_COLS * TILE_SIZE
ALTO        = MAPA_FILAS * TILE_SIZE + HUD_ALTO
FPS         = 60

PARED  = '#'
PUNTO  = '.'
POWER  = 'o'
VACIO  = ' '
PUERTA = '-'

NEGRO         = (0, 0, 0)
FONDO_JUEGO   = (5, 5, 15)  # Fondo general retro (en vez de negro puro)
PARED_RELLENO = (10, 10, 50)
AZUL_PARED    = (50, 80, 255)
PARED_BRILLO  = (100, 150, 255)
AMARILLO      = (255, 230, 0)
BLANCO        = (255, 255, 255)
ROSA          = (255, 100, 255)
PUNTO_COLOR   = (255, 200, 150)
HUD_BG        = (10, 10, 25)
HUD_TEXTO     = (200, 200, 220)

BLINKY_COLOR  = (255, 50, 50)
PINKY_COLOR   = (255, 100, 200)
INKY_COLOR    = (50, 255, 255)
CLYDE_COLOR   = (255, 160, 50)
ASUSTADO_COLOR = (50, 100, 255)
PUPILA_COLOR  = (20, 20, 80)

GLOW_ALPHA_GHOST = 80
GLOW_ALPHA_PACMAN = 60

VEL_PACMAN   = 2
VEL_FANTASMA = 2

ARRIBA    = (0, -1)
ABAJO     = (0, 1)
IZQUIERDA = (-1, 0)
DERECHA   = (1, 0)
QUIETO    = (0, 0)

TIEMPO_ASUSTADO     = 480
TIEMPO_INVENCIBLE   = 180
TIEMPO_DESAPARECIDO = 300
TIEMPO_LISTO        = 120
TIEMPO_MURIENDO     = 90

ESTADO_MENU      = "menu"
ESTADO_LISTO     = "listo"
ESTADO_JUGANDO   = "jugando"
ESTADO_MURIENDO  = "muriendo"
ESTADO_PAUSA     = "pausa"
ESTADO_GAME_OVER = "game_over"
ESTADO_VICTORIA  = "victoria"

PACMAN_INICIO = (14, 23)
BLINKY_INICIO = (14, 5)
PINKY_INICIO  = (6, 29)
INKY_INICIO   = (21, 5)
CLYDE_INICIO  = (21, 29)

PUNTO_PTS    = 10
POWER_PTS    = 50
FANTASMA_PTS = [200, 400, 800, 1600]

DIFIC_TONTA     = 0
DIFIC_TEMEROSA  = 1
DIFIC_ASTUTA    = 2
DIFIC_MAESTRA   = 3
NOMBRES_DIFICULTAD = ["Tonta", "Temerosa", "Astuta", "Maestra"]
COLORES_DIFICULTAD = [
    (100, 255, 100),
    (255, 255, 100),
    (255, 160, 60),
    (255, 60, 60),
]
DESCRIPCIONES = [
    "Solo esquiva paredes",
    "Huye si un fantasma esta cerca",
    "Pathfinding + evita fantasmas",
    "Memoriza zonas de peligro",
]

PAUSA_OPCIONES = ["Reanudar", "Reiniciar partida", "Menu principal"]

# ============================================================
# MENU PASOS
# ============================================================

MENU_PASO_JUGADORES  = 0
MENU_PASO_FANTASMAS  = 1
MENU_PASO_DIFICULTAD = 2

# ============================================================
# DATOS DE FANTASMAS PARA EL MENU
# ============================================================

GHOST_NOMBRES = ["Blinky", "Pinky", "Inky", "Clyde"]
GHOST_COLORES = [BLINKY_COLOR, PINKY_COLOR, INKY_COLOR, CLYDE_COLOR]
GHOST_INICIOS = [BLINKY_INICIO, PINKY_INICIO, INKY_INICIO, CLYDE_INICIO]
GHOST_ROLES = [
    "Perseguidor directo",
    "Anticipador",
    "Flanqueador",
    "El cobarde",
]
GHOST_DETALLES = [
    "Siempre va directo hacia Pac-Man",
    "Intenta cortar 4 tiles adelante",
    "Ataca por el costado con ayuda de Blinky",
    "Persigue de lejos, huye de cerca",
]

# ============================================================
# FRUTAS COLECCIONABLES
# ============================================================

FRUTA_POSICION = (14, 17)
FRUTA_DURACION = 600
FRUTA_UMBRAL   = 0.7
FRUTA_DATOS = [
    ("Cereza",   (220, 20, 60),  100),
    ("Frutilla", (255, 80, 100), 300),
    ("Naranja",  (255, 160, 60), 500),
]

# ============================================================
# SALIDA ESCALONADA DE FANTASMAS (frames)
# ============================================================

SALIDA_DELAYS = [0, 90, 240, 420]

# ============================================================
# HIGH SCORE
# ============================================================

HIGH_SCORE_FILE = "highscore.json"

# ============================================================
# POP-UP DE PUNTOS
# ============================================================

POPUP_DURACION = 60

# ============================================================
# NIVELES / PROGRESION
# ============================================================

ESTADO_NIVEL_COMPLETO = "nivel_completo"
NIVEL_DURACION_TRANSICION = 150
NIVEL_PODER_REDUCCION    = 60
NIVEL_PODER_MINIMO       = 120

NIVEL_FRUTAS = [
    ("Cereza",   (220, 20, 60),  100),
    ("Frutilla", (255, 80, 100), 300),
    ("Naranja",  (255, 160, 60), 500),
    ("Manzana",  (200, 50, 50),  700),
]

# ============================================================
# MODO ELROY (Blinky se acelera al final del nivel)
# ============================================================

ELROY_UMBRAL_1 = 20
ELROY_UMBRAL_2 = 10
ELROY_VEL_1    = 3
ELROY_VEL_2    = 4