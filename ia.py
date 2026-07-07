from entidad import Entidad
from constantes import *
import random


def ia_pacman_tonta(pacman, mapa):
    """IA basica: prefiere seguir recto, elige al azar en intersecciones."""
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


def ia_perseguir(fantasma, objetivo_col, objetivo_fila, mapa):
    """Elige la direccion que acerca mas al objetivo."""
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


def ia_asustado(fantasma, objetivo_col, objetivo_fila, mapa):
    """Huye del objetivo (maximiza distancia)."""
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