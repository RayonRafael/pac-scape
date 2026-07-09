"""
Inteligencia Artificial de los Fantasmas y Pac-Man.
Aqui se encuentran los algoritmos de busqueda de caminos (Pathfinding) como BFS.
"""
# ============================================================
# ia.py
# ============================================================
# Contiene TODA la inteligencia artificial del juego:
#
# 1) PATHFINDING (como encontrar caminos):
#    - bfs(): Busqueda en Anchura (camino mas corto)
#    - bfs_evitando(): BFS que evita zonas peligrosas
#
# 2) IA DE PAC-MAN (4 dificultades):
#    - Tonta: elige al azar
#    - Temerosa: huye si hay fantasmas cerca
#    - Astuta: pathfinding hacia puntos seguros
#    - Maestra: todo lo anterior + memoria de donde murio
#
# 3) IA DE FANTASMAS:
#    - Blinky: persigue directo a Pac-Man
#    - Pinky: corta 4 tiles adelante de Pac-Man
#    - Inky: flanquea usando la posicion de Blinky
#    - Clyde: persigue de lejos, huye de cerca
#    - Asustado: huye del objetivo (todos los fantasmas)
#
# Ninguna IA aprende. Son reglas matematicas fijas que se
# evaluan en cada interseccion (cuando la entidad esta
# centrada en un tile).
# ============================================================

from collections import deque
from entidad import Entidad
from constantes import *
import random


# ============================================================
# PATHFINDING
# ============================================================

def bfs(origen_col, origen_fila, destino_col, destino_fila, mapa,
        es_fantasma=False):
    """
    Busqueda en Anchura (Breadth-First Search).
    Encuentra el camino MAS CORTO entre dos puntos del mapa.

    Como funciona:
    1) Empieza en el origen
    2) Expande a todos los vecinos transitables
    3) De esos vecinos, expande a SUS vecinos
    4) Repite hasta encontrar el destino
    5) Devuelve la lista de direcciones para llegar

    Es como tirar una piedra en un lago: las ondas se expanden
    uniformemente hasta tocar el destino.

    Devuelve: lista de direcciones [(dx,dy), ...] o [] si no hay camino.
    """
    if (origen_col, origen_fila) == (destino_col, destino_fila):
        return []

    # Cola de busqueda: cada elemento es (posicion, camino_hasta_aqui)
    cola = deque()
    cola.append(((origen_col, origen_fila), []))
    visitados = {(origen_col, origen_fila)}

    while cola:
        (col, fila), camino = cola.popleft()

        # Expandir a las 4 direcciones
        for d in [ARRIBA, ABAJO, IZQUIERDA, DERECHA]:
            nc = Entidad._wrap_col(col + d[0])
            nf = fila + d[1]

            # Saltar si ya visitamos esta celda o es pared
            if (nc, nf) in visitados:
                continue
            if not mapa.es_transitable(nc, nf, es_fantasma):
                continue

            nuevo_camino = camino + [d]

            # Si llegamos al destino, devolver el camino
            if (nc, nf) == (destino_col, destino_fila):
                return nuevo_camino

            visitados.add((nc, nf))
            cola.append(((nc, nf), nuevo_camino))

    return []  # No hay camino


def bfs_evitando(origen_col, origen_fila, destino_col, destino_fila, mapa,
                  peligro_grid, umbral_peligro=0.3):
    """
    Igual que BFS pero evita celdas con alto valor de peligro.
    Usado por la IA maestra para no pasar por zonas donde murio antes.
    Si no encuentra camino seguro, hace fallback al BFS normal.
    """
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

            # Saltear celdas peligrosas (excepto el destino)
            if (peligro_grid[nf][nc] > umbral_peligro
                    and (nc, nf) != (destino_col, destino_fila)):
                continue

            nuevo_camino = camino + [d]

            if (nc, nf) == (destino_col, destino_fila):
                return nuevo_camino

            visitados.add((nc, nf))
            cola.append(((nc, nf), nuevo_camino))

    # Fallback: si no hay camino seguro, usar BFS normal
    return bfs(origen_col, origen_fila, destino_col, destino_fila, mapa)


# ============================================================
# IA PAC-MAN — TONTA
# ============================================================

def ia_pacman_tonta(pacman, mapa, fantasmas=None):
    """
    IA basica: prefiere seguir recto, elige al azar en intersecciones.
    No considera fantasmas ni puntos.
    - Si solo hay 1 opcion: va por ahi
    - Si hay varias: 70% sigue recto, 30% gira al azar
    - Si no hay opciones: da la vuelta
    """
    if not pacman.en_centro_tile():
        return

    dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
    reverso = (-pacman.direccion[0], -pacman.direccion[1])

    # Buscar direcciones validas (sin pared ni reverso)
    validas = []
    for d in dirs:
        if d == reverso:
            continue
        nc = Entidad._wrap_col(pacman.tile_col + d[0])
        nf = pacman.tile_fila + d[1]
        if mapa.es_transitable(nc, nf):
            validas.append(d)

    if not validas:
        # Sin opciones: dar la vuelta si es posible
        nc = Entidad._wrap_col(pacman.tile_col + reverso[0])
        nf = pacman.tile_fila + reverso[1]
        if mapa.es_transitable(nc, nf):
            pacman.direccion_siguiente = reverso
    elif len(validas) == 1:
        # Solo una opcion: ir por ahi
        pacman.direccion_siguiente = validas[0]
    else:
        # Varias opciones: 70% seguir recto, 30% girar al azar
        if pacman.direccion in validas and random.random() < 0.7:
            pacman.direccion_siguiente = pacman.direccion
        else:
            pacman.direccion_siguiente = random.choice(validas)


# ============================================================
# IA PAC-MAN — TEMEROSA
# ============================================================

def ia_pacman_temerosa(pacman, mapa, fantasmas):
    """
    Si un fantasma activo esta a menos de 5 tiles, huye de el.
    Sino, actua como la IA tonta.
    """
    if not pacman.en_centro_tile():
        return

    # Buscar fantasmas cercanos (activos y no asustados)
    peligrosos = []
    for f in fantasmas:
        if not f.activo or f.asustado:
            continue
        dist = abs(f.tile_col - pacman.tile_col) + abs(f.tile_fila - pacman.tile_fila)
        if dist < 5:
            peligrosos.append(f)

    # Si no hay fantasmas cerca, actuar como tonta
    if not peligrosos:
        ia_pacman_tonta(pacman, mapa, fantasmas)
        return

    # Huir: elegir la direccion que mas aleje del fantasma mas cercano
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
        # Distancia al fantasma mas cercano desde esa celda
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


# ============================================================
# IA PAC-MAN — ASTUTA
# ============================================================

def _encontrar_punto_seguro(pacman, mapa, fantasmas, peligro_grid=None):
    """
    Busca el punto/pellet mas lejano de todos los fantasmas activos.
    Opcionalmente penaliza celdas con alto valor de peligro.
    Devuelve (columna, fila) del punto o None si no hay puntos.
    """
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

            # Penalizar si hay peligro (solo para IA maestra)
            if peligro_grid is not None:
                score -= peligro_grid[f][c] * 200

            if score > mejor_score:
                mejor_score = score
                mejor_punto = (c, f)

    return mejor_punto


def ia_pacman_astuta(pacman, mapa, fantasmas):
    """
    IA avanzada:
    1) Si un fantasma esta a menos de 4 tiles, huir (como temerosa)
    2) Sino, usar BFS para ir al punto mas lejano de los fantasmas
    """
    if not pacman.en_centro_tile():
        return

    # Fase 1: evasion de emergencia
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

    # Fase 2: pathfinding hacia punto seguro
    objetivo = _encontrar_punto_seguro(pacman, mapa, fantasmas)
    if objetivo is None:
        ia_pacman_tonta(pacman, mapa, fantasmas)
        return

    # BFS para encontrar el camino mas corto al punto seguro
    camino = bfs(pacman.tile_col, pacman.tile_fila,
                 objetivo[0], objetivo[1], mapa)
    if camino:
        pacman.direccion_siguiente = camino[0]  # Primer paso del camino
    else:
        ia_pacman_tonta(pacman, mapa, fantasmas)


# ============================================================
# IA PAC-MAN — MAESTRA
# ============================================================

def ia_pacman_maestra(pacman, mapa, fantasmas):
    """
    IA experta: igual que astuta pero ademas evita zonas donde
    murio antes usando el grid de peligro.
    Si un fantasma se acerca, considera tanto la huida como el peligro.
    """
    if not pacman.en_centro_tile():
        return

    # Evasion de emergencia (considerando peligro grid)
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
            # Combinar distancia al fantasma con peligro de la zona
            peligro_local = pacman.peligro_grid[nf][nc]
            score = min_dist - peligro_local * 100
            if score > mejor_dist:
                mejor_dist = score
                mejor_dir = d
        if mejor_dir:
            pacman.direccion_siguiente = mejor_dir
            return

    # Pathfinding evitando zonas peligrosas
    objetivo = _encontrar_punto_seguro(pacman, mapa, fantasmas,
                                        pacman.peligro_grid)
    if objetivo is None:
        ia_pacman_tonta(pacman, mapa, fantasmas)
        return

    # BFS que evita zonas con alto valor de peligro
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
# IA FANTASMAS — FUNCION COMPARTIDA
# ============================================================

def _ir_hacia(fantasma, objetivo_col, objetivo_fila, mapa):
    """
    Funcion base que usan todos los fantasmas.
    Elige la direccion que mas acerca al fantasma al objetivo.
    Todos los fantasmas usan esta misma funcion, la unica
    diferencia es QUE objetivo calculan antes de llamarla.
    """
    if not fantasma.en_centro_tile():
        return

    dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
    reverso = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir = None
    mejor_dist = float('inf')

    for d in dirs:
        if d == reverso:
            continue  # No dar la vuelta si hay otra opcion
        nc = Entidad._wrap_col(fantasma.tile_col + d[0])
        nf = fantasma.tile_fila + d[1]
        if not mapa.es_transitable(nc, nf, es_fantasma=True):
            continue
        # Distancia al objetivo (cuadrado, sin raiz para ahorrar calculo)
        dist = (nc - objetivo_col) ** 2 + (nf - objetivo_fila) ** 2
        if dist < mejor_dist:
            mejor_dist = dist
            mejor_dir = d

    if mejor_dir:
        fantasma.direccion_siguiente = mejor_dir
    else:
        # Si no hay opcion, dar la vuelta
        nc = Entidad._wrap_col(fantasma.tile_col + reverso[0])
        nf = fantasma.tile_fila + reverso[1]
        if mapa.es_transitable(nc, nf, es_fantasma=True):
            fantasma.direccion_siguiente = reverso


# ============================================================
# IA FANTASMAS — INDIVIDUALES
# ============================================================

def ia_blinky(fantasma, mapa, pac_col, pac_fila):
    """
    Blinky (rojo) — El perseguidor directo.
    Objetivo: la posicion actual de Pac-Man.
    Es el mas agresivo: siempre va directo hacia ti.
    """
    _ir_hacia(fantasma, pac_col, pac_fila, mapa)


def ia_pinky(fantasma, mapa, pac_col, pac_fila, pac_dir):
    """
    Pinky (rosa) — El anticipador.
    Objetivo: 4 tiles adelante de donde Pac-Man esta mirando.
    Intenta cortar el camino en vez de perseguir por detras.
    """
    tc = pac_col + pac_dir[0] * 4
    tf = pac_fila + pac_dir[1] * 4
    _ir_hacia(fantasma, tc, tf, mapa)


def ia_inky(fantasma, mapa, pac_col, pac_fila, pac_dir,
            blinky_col, blinky_fila):
    """
    Inky (cian) — El flanqueador.
    Calcula su objetivo usando la posicion de Blinky:
    1) Toma un punto 2 tiles adelante de Pac-Man (pivot)
    2) Dibuja un vector desde Blinky hasta ese pivot
    3) Duplica ese vector
    4) El punto resultante es su objetivo

    Resultado: si Blinky persigue de frente, Inky ataca por el costado.
    Si Blinky cambia de rumbo, Inky se reajusta automaticamente.
    """
    # Paso 1: punto 2 tiles adelante de Pac-Man
    pivot_col = pac_col + pac_dir[0] * 2
    pivot_fila = pac_fila + pac_dir[1] * 2

    # Paso 2-3: duplicar el vector Blinky -> pivot
    objetivo_col = pivot_col + (pivot_col - blinky_col)
    objetivo_fila = pivot_fila + (pivot_fila - blinky_fila)

    _ir_hacia(fantasma, objetivo_col, objetivo_fila, mapa)


def ia_clyde(fantasma, mapa, pac_col, pac_fila, esquina_col, esquina_fila):
    """
    Clyde (naranja) — El cobarde.
    - Si Pac-Man esta a mas de 8 tiles (distancia Manhattan): persigue directo
    - Si esta a menos de 8 tiles: huye a su esquina asignada
    Resultado: a veces persigue, a veces desaparece. Impredecible.
    """
    # Distancia Manhattan = suma de diferencias absolutas en columnas y filas
    dist = abs(fantasma.tile_col - pac_col) + abs(fantasma.tile_fila - pac_fila)

    if dist > 8:
        # Lejos: perseguir a Pac-Man
        _ir_hacia(fantasma, pac_col, pac_fila, mapa)
    else:
        # Cerca: huir a la esquina
        _ir_hacia(fantasma, esquina_col, esquina_fila, mapa)


def ia_asustado(fantasma, objetivo_col, objetivo_fila, mapa):
    """
    IA de huida. Usan TODOS los fantasmas cuando estan asustados.
    Maximiza la distancia al objetivo (Pac-Man) en vez de minimizarla.
    """
    if not fantasma.en_centro_tile():
        return

    dirs = [ARRIBA, ABAJO, IZQUIERDA, DERECHA]
    reverso = (-fantasma.direccion[0], -fantasma.direccion[1])
    mejor_dir = None
    mejor_dist = -1  # Buscamos la MAXIMA distancia

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