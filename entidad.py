# ============================================================
# entidad.py
# ============================================================
# Clase base para TODO lo que se mueve en el mapa (Pac-Man y fantasmas).
# Implementa el sistema de movimiento tile-based con interpolacion suave.
#
# "Tile-based" = la posicion logica siempre esta alineada a la grilla.
# "Interpolacion suave" = el movimiento entre tiles es fluido (pixeles).
#
# Es como si la entidad siempre estuviera en el centro de una celda,
# pero cuando se mueve a la siguiente, lo hace pixel por pixel.
# ============================================================

from constantes import *


class Entidad:
    """
    Clase base con movimiento por grilla y soporte para tuneles.
    PacMan y Fantasma heredan de esta clase.
    """

    def __init__(self, col, fila, velocidad):
        # Posicion en PIXELES (no en tiles)
        # Se calcula: columna * tamano_tile + centro_del_tile
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = fila * TILE_SIZE + TILE_SIZE // 2

        self.velocidad = velocidad       # Pixeles que se mueve por frame
        self.direccion = QUIETO          # Direccion actual de movimiento
        self.direccion_siguiente = QUIETO  # Direccion que se aplicara al llegar al centro

    # ============================================================
    # PROPIEDADES DE GRILLA
    # ============================================================
    # Convierten la posicion en pixeles a coordenadas de grilla (tiles).
    # Ejemplo: si x=360 y TILE_SIZE=24, tile_col = 360/24 = 15
    # ============================================================

    @property
    def tile_col(self):
        """En que columna de la grilla estoy."""
        return self.x // TILE_SIZE

    @property
    def tile_fila(self):
        """En que fila de la grilla estoy."""
        return self.y // TILE_SIZE

    def en_centro_tile(self):
        """
        Devuelve True si la entidad esta exactamente en el centro
        de una celda. Este es el unico momento donde puede cambiar
        de direccion (como en el juego original).
        """
        cx = self.tile_col * TILE_SIZE + TILE_SIZE // 2
        cy = self.tile_fila * TILE_SIZE + TILE_SIZE // 2
        return self.x == cx and self.y == cy

    # ============================================================
    # LOGICA DE TUNELES
    # ============================================================

    @staticmethod
    def _wrap_col(col):
        """
        Envuelve la columna para atravesar los tuneles laterales.
        Si vas a la izquierda del mapa (col < 0), apareces a la derecha.
        Si vas a la derecha (col >= 28), apareces a la izquierda.
        Esto es el "wrap-around" clasico de Pac-Man.
        """
        if col < 0:
            return MAPA_COLS - 1
        if col >= MAPA_COLS:
            return 0
        return col

    # ============================================================
    # UPDATE (logica de movimiento)
    # ============================================================

    def update(self, mapa, es_fantasma=False):
        """
        Actualiza la posicion de la entidad cada frame.
        El movimiento tiene 3 fases:
        1) Intentar girar (solo en el centro de un tile)
        2) Comprobar si hay pared adelante
        3) Avanzar en la direccion actual
        """

        # --- FASE 1: Intentar girar ---
        # Si estamos en el centro de un tile Y el jugador (o la IA)
        # pidio cambiar de direccion, intentamos hacerlo.
        if self.en_centro_tile() and self.direccion_siguiente != QUIETO:
            dx, dy = self.direccion_siguiente
            nc = self._wrap_col(self.tile_col + dx)
            nf = self.tile_fila + dy
            # Solo girar si la nueva direccion no tiene pared
            if mapa.es_transitable(nc, nf, es_fantasma):
                self.direccion = self.direccion_siguiente
                self.direccion_siguiente = QUIETO  # Consumir la orden

        # --- FASE 2: Comprobar pared adelante ---
        # Si estamos en el centro del tile y hay una pared
        # en la direccion actual, nos detenemos.
        if self.en_centro_tile():
            dx, dy = self.direccion
            if (dx, dy) != (0, 0):
                nc = self._wrap_col(self.tile_col + dx)
                nf = self.tile_fila + dy
                if not mapa.es_transitable(nc, nf, es_fantasma):
                    return  # Hay pared, no movernos

        # --- FASE 3: Avanzar ---
        # Mover la posicion en pixeles segun la direccion y velocidad.
        dx, dy = self.direccion
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad

        # --- FASE 4: Wrap de tuneles ---
        # Si nos salimos de la pantalla por los lados,
        # aparecemos por el otro lado.
        max_x = MAPA_COLS * TILE_SIZE
        if self.x < 0:
            self.x += max_x
        elif self.x >= max_x:
            self.x -= max_x