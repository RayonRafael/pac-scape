# ============================================================
# VENTANA Y GRILLA
# ============================================================

TILE_SIZE   = 24              # Tamano de cada celda en pixeles
MAPA_COLS   = 28              # Cantidad de columnas del mapa
MAPA_FILAS  = 31              # Cantidad de filas del mapa
HUD_ALTO    = 50              # Altura de la barra de informacion inferior
ANCHO       = MAPA_COLS * TILE_SIZE              # Ancho de la ventana (672px)
ALTO        = MAPA_FILAS * TILE_SIZE + HUD_ALTO  # Alto de la ventana (794px)
FPS         = 60              # Frames por segundo (suavidad de la animacion)

# ============================================================
# SIMBOLOS DEL MAPA
# ============================================================
# Cada caracter en el mapa.txt significa algo diferente.
# Se usan para construir el laberinto y saber que hay en cada celda.
# ============================================================

PARED  = '#'  # Pared solida, nadie puede pasar
PUNTO  = '.'  # Punto comestible (10 puntos)
POWER  = 'o'  # Power pellet (50 puntos, activa power mode)
VACIO  = ' '  # Espacio vacio, se puede caminar pero no hay punto
PUERTA = '-'  # Puerta de la casa de fantasmas (solo fantasmas pasan)

# ============================================================
# COLORES
# ============================================================
# Todos los colores del juego definidos como tuplas RGB (Rojo, Verde, Azul).
# Cada valor va de 0 (apagado) a 255 (maximo brillo).
# Ejemplo: (255, 255, 0) = rojo + verde = amarillo.
# ============================================================

# Colores generales
NEGRO         = (0, 0, 0)        # Fondo de la ventana
PARED_RELLENO = (5, 5, 40)       # Interior de las paredes (casi negro con tinte azul)
AZUL_PARED    = (33, 33, 222)    # Bordes de las paredes
AMARILLO      = (255, 255, 0)    # Color de Pac-Man
BLANCO        = (255, 255, 255)  # Texto y ojos de fantasmas
ROSA          = (255, 184, 255)  # Puerta de la casa de fantasmas
PUNTO_COLOR   = (255, 183, 174)  # Color de los puntos y power pellets
HUD_BG        = (15, 15, 35)     # Fondo de la barra de informacion
HUD_TEXTO     = (180, 180, 200)  # Texto secundario del HUD

# Colores de cada fantasma
BLINKY_COLOR  = (255, 0, 0)      # Blinky: rojo
PINKY_COLOR   = (255, 184, 255)  # Pinky: rosa
INKY_COLOR    = (0, 255, 255)    # Inky: cian (celeste)
CLYDE_COLOR   = (255, 184, 81)   # Clyde: naranja
ASUSTADO_COLOR = (33, 33, 222)   # Color cuando estan asustados (azul)
PUPILA_COLOR  = (33, 33, 100)    # Color de las pupilas de los fantasmas


# ============================================================
# VELOCIDADES
# ============================================================
# Velocidad en pixeles por frame. DEBE dividir exactamente a TILE_SIZE.
# Ejemplo: TILE_SIZE=24, velocidad=2 → se mueve 2px por frame,
# tarda 12 frames en cruzar una celda (24/2 = 12).
# Si la velocidad no divide al tile, las entidades nunca
# llegarian exactamente al centro de una celda.
# ============================================================

VEL_PACMAN   = 2   # Pixeles por frame de Pac-Man
VEL_FANTASMA = 2   # Pixeles por frame de los fantasmas

# ============================================================
# DIRECCIONES
# ============================================================
# Cada direccion es una tupla (dx, dy) en unidades de tiles.
# dx = cambio en columnas, dy = cambio en filas.
# Nota: en pantalla, Y crece hacia abajo (fila 0 arriba, fila 30 abajo).
# ============================================================

ARRIBA    = (0, -1)   # Mover 0 columnas, -1 fila (hacia arriba)
ABAJO     = (0, 1)    # Mover 0 columnas, +1 fila (hacia abajo)
IZQUIERDA = (-1, 0)   # Mover -1 columnas, 0 filas (hacia la izquierda)
DERECHA   = (1, 0)    # Mover +1 columnas, 0 filas (hacia la derecha)
QUIETO    = (0, 0)    # Sin movimiento

# ============================================================
# DURACIONES (en frames a 60fps)
# ============================================================
# 60 frames = 1 segundo. Entonces:
#   TIEMPO_ASUSTADO = 480 frames = 8 segundos
#   TIEMPO_INVENCIBLE = 180 frames = 3 segundos
# ============================================================

TIEMPO_ASUSTADO     = 480   # Cuanto dura el power mode (fantasmas azules)
TIEMPO_INVENCIBLE   = 180   # Cuanto parpadea Pac-Man al reaparecer
TIEMPO_DESAPARECIDO = 300   # Cuanto tarda un fantasma en reaparecer tras ser comido
TIEMPO_LISTO        = 120   # Cuanto se muestra "READY!" antes de cada ronda
TIEMPO_MURIENDO     = 90    # Cuanto dura la animacion de muerte de Pac-Man

# ============================================================
# ESTADOS DEL JUEGO
# ============================================================
# El juego tiene 7 estados posibles.
# ============================================================

ESTADO_MENU      = "menu"       
ESTADO_LISTO     = "listo"     
ESTADO_JUGANDO   = "jugando"    
ESTADO_MURIENDO  = "muriendo"   
ESTADO_PAUSA     = "pausa"      
ESTADO_GAME_OVER = "game_over" 
ESTADO_VICTORIA  = "victoria" 

# ============================================================
# POSICIONES INICIALES (columna, fila)
# ============================================================

PACMAN_INICIO = (14, 23)  # Centro del mapa, zona baja
BLINKY_INICIO = (14, 5)   # Centro-arriba
PINKY_INICIO  = (6, 29)   # Esquina inferior izquierda
INKY_INICIO   = (21, 5)   # Derecha-arriba
CLYDE_INICIO  = (21, 29)  # Esquina inferior derecha

# ============================================================
# PUNTUACION
# ============================================================

PUNTO_PTS    = 10                     # Puntos por comer un punto normal
POWER_PTS    = 50                     # Puntos por comer un power pellet
FANTASMA_PTS = [200, 400, 800, 1600]  # Puntos por comer fantasmas en racha

# ============================================================
# DIFICULTADES DE PAC-MAN
# ============================================================
# Cada uno usa un algoritmo diferente (definido en ia.py).
# ============================================================

DIFIC_TONTA     = 0   # Elige al azar, solo evita paredes
DIFIC_TEMEROSA  = 1   # Huye si un fantasma se acerca
DIFIC_ASTUTA    = 2   # Pathfinding + evasion de fantasmas
DIFIC_MAESTRA   = 3   # Todo lo anterior + memoria de zonas peligrosas

# Nombres que se muestran en el menu
NOMBRES_DIFICULTAD = ["Tonta", "Temerosa", "Astuta", "Maestra"]

# Color de cada dificultad (para el menu y el HUD)
COLORES_DIFICULTAD = [
    (100, 255, 100),   # Tonta: verde (facil)
    (255, 255, 100),   # Temerosa: amarillo
    (255, 160, 60),    # Astuta: naranja
    (255, 60, 60),     # Maestra: rojo (dificil)
]

# Descripcion corta de cada dificultad (aparece en el menu)
DESCRIPCIONES = [
    "Solo esquiva paredes",
    "Huye si un fantasma esta cerca",
    "Pathfinding + evita fantasmas",
    "Memoriza zonas de peligro",
]

# Opciones del menu de pausa
PAUSA_OPCIONES = ["Reanudar", "Reiniciar partida", "Menu principal"]