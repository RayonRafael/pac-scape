from entidad import Entidad
from constantes import *
import random


def ia_pacman_tonta(pacman, mapa):
    if not pacman.en_centro_tile():
        return
    dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
    reverso = (-pacman.direccion[0], -pacman.direccion[1])
    validas = []
    for d in dirs:
        if d == reverso:
            continue
        nc = Entidad._wrap_col(pacman.tile_col + d[0])
        nf = pacman.tile_fila + d[1]
        if mapa.es_transitable(nc, nf):
            validas.append(d)
    if not validas:
        nc = Entidad._wrap_col(pacman.tile_col + reverso[0])
        nf = pacman.tile_fila + reverso[1]
        if mapa.es_transitable(nc, nf):
            pacman.direccion_siguiente = reverso
    elif len(validas) == 1:
        pacman.direccion_siguiente = validas[0]
    else:
        if pacman.direccion in validas and random.random() < 0.7:
            pacman.direccion_siguiente = pacman.direccion
        else:
            pacman.direccion_siguiente = random.choice(validas)


def _ir_hacia(fantasma, objetivo_col, objetivo_fila, mapa):
    if not fantasma.en_centro_tile():
        return
    dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
    reverso = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir = None
    mejor_dist = float('inf')
    for d in dirs:
        if d == reverso:
            continue
        nc = Entidad._wrap_col(fantasma.tile_col + d[0])
        nf = fantasma.tile_fila + d[1]
        if not mapa.es_transitable(nc, nf, es_fantasma=True):
            continue
        dist = (nc - objetivo_col) ** 2 + (nf - objetivo_fila) ** 2
        if dist < mejor_dist:
            mejor_dist = dist
            mejor_dir = d
    if mejor_dir:
        fantasma.direccion_siguiente = mejor_dir
    else:
        nc = Entidad._wrap_col(fantasma.tile_col + reverso[0])
        nf = fantasma.tile_fila + reverso[1]
        if mapa.es_transitable(nc, nf, es_fantasma=True):
            fantasma.direccion_siguiente = reverso


def ia_blinky(fantasma, mapa, pac_col, pac_fila):
    """Blinky: persigue directo a Pac-Man."""
    _ir_hacia(fantasma, pac_col, pac_fila, mapa)


def ia_pinky(fantasma, mapa, pac_col, pac_fila, pac_dir):
    """Pinky: intenta cortar 4 tiles adelante de Pac-Man."""
    tc = pac_col + pac_dir[0] * 4
    tf = pac_fila + pac_dir[1] * 4
    _ir_hacia(fantasma, tc, tf, mapa)


def ia_inky(fantasma, mapa, pac_col, pac_fila, pac_dir, blinky_col, blinky_fila):
    """
    Inky: flanqueador.
    1) Toma el tile 2 adelante de Pac-Man
    2) Dibuja vector desde Blinky hasta ese tile
    3) Dobla el vector => ese es el objetivo de Inky
    Resultado: si Blinky persigue de frente, Inky ataca por el flanco.
    """
    pivot_col = pac_col + pac_dir[0] * 2
    pivot_fila = pac_fila + pac_dir[1] * 2
    objetivo_col = pivot_col + (pivot_col - blinky_col)
    objetivo_fila = pivot_fila + (pivot_fila - blinky_fila)
    _ir_hacia(fantasma, objetivo_col, objetivo_fila, mapa)


def ia_clyde(fantasma, mapa, pac_col, pac_fila, esquina_col, esquina_fila):
    """
    Clyde: el cobarde.
    Si Pac-Man esta a mas de 8 tiles -> persigue directo.
    Si esta a menos de 8 -> huye a su esquina.
    """
    dist = abs(fantasma.tile_col - pac_col) + abs(fantasma.tile_fila - pac_fila)
    if dist > 8:
        _ir_hacia(fantasma, pac_col, pac_fila, mapa)
    else:
        _ir_hacia(fantasma, esquina_col, esquina_fila, mapa)


def ia_asustado(fantasma, objetivo_col, objetivo_fila, mapa):
    if not fantasma.en_centro_tile():
        return
    dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
    reverso = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir = None
    mejor_dist = -1
    for d in dirs:
        if d == reverso:
            continue
        nc = Entidad._wrap_col(fantasma.tile_col + d[0])
        nf = fantasma.tile_fila + d[1]
        if not mapa.es_transitable(nc, nf, es_fantasma=True):
            continue
        dist = (nc - objetivo_col) ** 2 + (nf - objetivo_fila) ** 2
        if dist > mejor_dist:
            mejor_dist = dist
            mejor_dir = d
    if mejor_dir:
        fantasma.direccion_siguiente = mejor_dir
    else:
        nc = Entidad._wrap_col(fantasma.tile_col + reverso[0])
        nf = fantasma.tile_fila + reverso[1]
        if mapa.es_transitable(nc, nf, es_fantasma=True):
            fantasma.direccion_siguiente = reverso