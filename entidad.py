# ============================================================
# entidad.py — Clase base con movimiento tile-based + tuneles
# ============================================================
from constantes import *


class Entidad:
    """
    Movimiento por grilla con interpolacion suave.
    La posicion logica siempre esta alineada al centro de un tile.
    """

    def __init__(self, col, fila, velocidad):
        self.x = col * TILE_SIZE + TILE_SIZE // 2
        self.y = fila * TILE_SIZE + TILE_SIZE // 2
        self.velocidad = velocidad
        self.direccion = QUIETO
        self.direccion_siguiente = QUIETO

    # ---- propiedades de grilla ----
    @property
    def tile_col(self):
        return self.x // TILE_SIZE

    @property
    def tile_fila(self):
        return self.y // TILE_SIZE

    def en_centro_tile(self):
        cx = self.tile_col * TILE_SIZE + TILE_SIZE // 2
        cy = self.tile_fila * TILE_SIZE + TILE_SIZE // 2
        return self.x == cx and self.y == cy

    # ---- logica de tuneles ----
    @staticmethod
    def _wrap_col(col):
        """Envuelve la columna para atravesar tuneles laterales."""
        if col < 0:
            return MAPA_COLS - 1
        if col >= MAPA_COLS:
            return 0
        return col

    # ---- update ----
    def update(self, mapa, es_fantasma=False):
        # 1) En el centro del tile: intentar girar
        if self.en_centro_tile() and self.direccion_siguiente != QUIETO:
            dx, dy = self.direccion_siguiente
            nc = self._wrap_col(self.tile_col + dx)
            nf = self.tile_fila + dy
            if mapa.es_transitable(nc, nf, es_fantasma):
                self.direccion = self.direccion_siguiente
                self.direccion_siguiente = QUIETO

        # 2) En el centro del tile: comprobar pared adelante
        if self.en_centro_tile():
            dx, dy = self.direccion
            if (dx, dy) != (0, 0):
                nc = self._wrap_col(self.tile_col + dx)
                nf = self.tile_fila + dy
                if not mapa.es_transitable(nc, nf, es_fantasma):
                    return  # hay pared, no se mueve

        # 3) Avanzar
        dx, dy = self.direccion
        self.x += dx * self.velocidad
        self.y += dy * self.velocidad

        # 4) Wrap de pixel para tuneles
        max_x = MAPA_COLS * TILE_SIZE
        if self.x < 0:
            self.x += max_x
        elif self.x >= max_x:
            self.x -= max_x