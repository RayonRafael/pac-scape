from collections import deque
from entidad import Entidad
from constantes import *
import random
import math


# ============================================================
# PATHFINDING (BFS en grilla)
# ============================================================

def bfs(origen_col, origen_fila, destino_col, destino_fila, mapa, es_fantasma=False):
    """Devuelve la lista de direcciones para ir de A a B, o [] si no hay camino."""
    if (origen_col, origen_fila) == (destino_col, destino_fila):
        return []
    cola = deque()
    cola.append(((origen_col, origen_fila), []))
    visitados = {(origen_col, origen_fila)}
    while cola:
        (col, fila), camino = cola.popleft()
        for d in [ARRIBA, ABAJO, IZQUIERDA, DERECHA]:
            nc = Entidad._wrap_col(col + d[0])
            nf = fila + d[1]
            if (nc, nf) in visitados:
                continue
            if not mapa.es_transitable(nc, nf, es_fantasma):
                continue
            nuevo_camino = camino + [d]
            if (nc, nf) == (destino_col, destino_fila):
                return nuevo_camino
            visitados.add((nc, nf))
            cola.append(((nc, nf), nuevo_camino))
    return []


def bfs_evitando(origen_col, origen_fila, destino_col, destino_fila, mapa,
                  peligro_grid, umbral_peligro=0.3):
    """BFS que evita tiles peligrosos (para IA maestra)."""
    if (origen_col, origen_fila) == (destino_col, destino_fila):
        return []
    cola = deque()
    cola.append(((origen_col, origen_fila), []))
    visitados = {(origen_col, origen_fila)}
    while cola:
        (col, fila), camino = cola.popleft()
        for d in [ARRIBA, ABAJO, IZQUIERDA, DERECHA]:
            nc = Entidad._wrap_col(col + d[0])
            nf = fila + d[1]
            if (nc, nf) in visitados:
                continue
            if not mapa.es_transitable(nc, nf):
                continue
            if peligro_grid[nf][nc] > umbral_peligro and (nc, nf) != (destino_col, destino_fila):
                continue
            nuevo_camino = camino + [d]
            if (nc, nf) == (destino_col, destino_fila):
                return nuevo_camino
            visitados.add((nc, nf))
            cola.append(((nc, nf), nuevo_camino))
    # Fallback: ignorar peligro si no hay camino seguro
    return bfs(origen_col, origen_fila, destino_col, destino_fila, mapa)


# ============================================================
# IA PAC-MAN
# ============================================================

def ia_pacman_tonta(pacman, mapa, fantasmas=None):
    """Solo esquiva paredes. Previene salir recto sin fin."""
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


def ia_pacman_temerosa(pacman, mapa, fantasmas):
    """Si un fantasma activo esta a <5 tiles, huye de el. Sino, actua como tonta."""
    if not pacman.en_centro_tile():
        return

    peligrosos = []
    for f in fantasmas:
        if not f.activo or f.asustado:
            continue
        dist = abs(f.tile_col - pacman.tile_col) + abs(f.tile_fila - pacman.tile_fila)
        if dist < 5:
            peligrosos.append(f)

    if not peligrosos:
        ia_pacman_tonta(pacman, mapa, fantasmas)
        return

    # Elegir la direccion que maximiza la distancia al fantasma mas cercano
    dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
    reverso = (-pacman.direccion[0], -pacman.direccion[1])
    mejor_dir = None
    mejor_dist = -1

    for d in dirs:
        if d == reverso:
            continue
        nc = Entidad._wrap_col(pacman.tile_col + d[0])
        nf = pacman.tile_fila + d[1]
        if not mapa.es_transitable(nc, nf):
            continue
        # Distancia al fantasma mas cercano desde ese tile
        min_dist = min(
            (nc - f.tile_col) ** 2 + (nf - f.tile_fila) ** 2
            for f in peligrosos
        )
        if min_dist > mejor_dist:
            mejor_dist = min_dist
            mejor_dir = d

    if mejor_dir:
        pacman.direccion_siguiente = mejor_dir
    else:
        ia_pacman_tonta(pacman, mapa, fantasmas)


def _encontrar_punto_seguro(pacman, mapa, fantasmas, peligro_grid=None):
    """Encuentra el punto/pellet mas lejano de todos los fantasmas activos."""
    fantasmas_activos = [f for f in fantasmas if f.activo and not f.asustado]
    mejor_punto = None
    mejor_score = -1

    for f in range(MAPA_FILAS):
        for c in range(MAPA_COLS):
            celda = mapa.grid[f][c]
            if celda not in (PUNTO, POWER):
                continue
            # Distancia minima a cualquier fantasma
            if fantasmas_activos:
                dist_min = min(
                    (c - fg.tile_col) ** 2 + (f - fg.tile_fila) ** 2
                    for fg in fantasmas_activos
                )
            else:
                dist_min = 9999

            score = dist_min
            # Penalizar si hay peligro
            if peligro_grid is not None:
                score -= peligro_grid[f][c] * 200

            if score > mejor_score:
                mejor_score = score
                mejor_punto = (c, f)

    return mejor_punto


def ia_pacman_astuta(pacman, mapa, fantasmas):
    """Pathfinding hacia el punto mas seguro + esquiva fantasmas cercanos."""
    if not pacman.en_centro_tile():
        return

    # Si hay un fantasma muy cerca, priorizar huir
    peligrosos = []
    for f in fantasmas:
        if not f.activo or f.asustado:
            continue
        dist = abs(f.tile_col - pacman.tile_col) + abs(f.tile_fila - pacman.tile_fila)
        if dist < 4:
            peligrosos.append(f)

    if peligrosos:
        dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
        reverso = (-pacman.direccion[0], -pacman.direccion[1])
        mejor_dir = None
        mejor_dist = -1
        for d in dirs:
            if d == reverso:
                continue
            nc = Entidad._wrap_col(pacman.tile_col + d[0])
            nf = pacman.tile_fila + d[1]
            if not mapa.es_transitable(nc, nf):
                continue
            min_dist = min(
                (nc - f.tile_col) ** 2 + (nf - f.tile_fila) ** 2
                for f in peligrosos
            )
            if min_dist > mejor_dist:
                mejor_dist = min_dist
                mejor_dir = d
        if mejor_dir:
            pacman.direccion_siguiente = mejor_dir
            return

    # Buscar punto seguro y pathfindear
    objetivo = _encontrar_punto_seguro(pacman, mapa, fantasmas)
    if objetivo is None:
        ia_pacman_tonta(pacman, mapa, fantasmas)
        return

    camino = bfs(pacman.tile_col, pacman.tile_fila, objetivo[0], objetivo[1], mapa)
    if camino:
        pacman.direccion_siguiente = camino[0]
    else:
        ia_pacman_tonta(pacman, mapa, fantasmas)


def ia_pacman_maestra(pacman, mapa, fantasmas):
    """Igual que astuta + evita zonas donde ha muerto antes."""
    if not pacman.en_centro_tile():
        return

    # Si hay un fantasma muy cerca, priorizar huir
    peligrosos = []
    for f in fantasmas:
        if not f.activo or f.asustado:
            continue
        dist = abs(f.tile_col - pacman.tile_col) + abs(f.tile_fila - pacman.tile_fila)
        if dist < 5:
            peligrosos.append(f)

    if peligrosos:
        dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
        reverso = (-pacman.direccion[0], -pacman.direccion[1])
        mejor_dir = None
        mejor_dist = -1
        for d in dirs:
            if d == reverso:
                continue
            nc = Entidad._wrap_col(pacman.tile_col + d[0])
            nf = pacman.tile_fila + d[1]
            if not mapa.es_transitable(nc, nf):
                continue
            min_dist = min(
                (nc - f.tile_col) ** 2 + (nf - f.tile_fila) ** 2
                for f in peligrosos
            )
            # Bonus: tambien considerar peligro del grid
            peligro_local = pacman.peligro_grid[nf][nc]
            score = min_dist - peligro_local * 100
            if score > mejor_dist:
                mejor_dist = score
                mejor_dir = d
        if mejor_dir:
            pacman.direccion_siguiente = mejor_dir
            return

    # Buscar punto seguro considerando peligro
    objetivo = _encontrar_punto_seguro(pacman, mapa, fantasmas, pacman.peligro_grid)
    if objetivo is None:
        ia_pacman_tonta(pacman, mapa, fantasmas)
        return

    camino = bfs_evitando(
        pacman.tile_col, pacman.tile_fila,
        objetivo[0], objetivo[1],
        mapa, pacman.peligro_grid
    )
    if camino:
        pacman.direccion_siguiente = camino[0]
    else:
        ia_pacman_tonta(pacman, mapa, fantasmas)


# ============================================================
# IA FANTASMAS
# ============================================================

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
    _ir_hacia(fantasma, pac_col, pac_fila, mapa)


def ia_pinky(fantasma, mapa, pac_col, pac_fila, pac_dir):
    tc = pac_col + pac_dir[0] * 4
    tf = pac_fila + pac_dir[1] * 4
    _ir_hacia(fantasma, tc, tf, mapa)


def ia_inky(fantasma, mapa, pac_col, pac_fila, pac_dir, blinky_col, blinky_fila):
    pivot_col = pac_col + pac_dir[0] * 2
    pivot_fila = pac_fila + pac_dir[1] * 2
    objetivo_col = pivot_col + (pivot_col - blinky_col)
    objetivo_fila = pivot_fila + (pivot_fila - blinky_fila)
    _ir_hacia(fantasma, objetivo_col, objetivo_fila, mapa)


def ia_clyde(fantasma, mapa, pac_col, pac_fila, esquina_col, esquina_fila):
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