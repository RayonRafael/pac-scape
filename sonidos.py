# ============================================================
# sonidos.py
# ============================================================
# Genera sonidos retro usando ondas matematicas, SIN necesitar
# archivos de audio externos.
#
# Usa la libreria estandar de Python (array, math) para crear
# formas de onda (sinusoidal, cuadrada) y las convierte en
# objetos Sound de Pygame.
#
# Sonidos generados:
#   - chomp_a / chomp_b: waka-waka (dos tonos alternos)
#   - power: tono ascendente al comer power pellet
#   - eat_ghost: tono agudo ascendente al comer fantasma
#   - death: barrido descendente al morir
#   - ready: tono corto al inicio de partida
# ============================================================

import pygame
import array
import math


def _tono(freq, dur, vol=0.25, forma='sin'):
    """
    Genera un sonido con frecuencia y duracion dadas.

    Parametros:
        freq: frecuencia en Hz (261 = Do central, 440 = La)
        dur: duracion en segundos
        vol: volumen de 0.0 a 1.0
        forma: 'sin' (sinusoidal suave) o 'square' (cuadrada, mas retro)

    Como funciona:
        Crea un array de muestras de audio a 22050 Hz.
        Para cada muestra, calcula el valor de la onda
        en ese instante y lo multiplica por el volumen
        y una envolvente de decaimiento (para que no corte de golpe).
    """
    sr = 22050  # Sample rate (muestras por segundo)
    n = int(sr * dur)  # Cantidad total de muestras
    buf = array.array('h')  # 'h' = signed short (16 bits con signo)

    for i in range(n):
        t = i / sr  # Tiempo en segundos

        # Envolvente: el sonido baja un poco de volumen con el tiempo
        env = max(0, 1.0 - (i / n) * 0.3)

        if forma == 'sin':
            # Onda sinusoidal: suave, natural
            v = math.sin(2 * math.pi * freq * t)
        else:
            # Onda cuadrada: dura, retro (como los juegos de los 80)
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0

        # Convertir a valor de 16 bits (-32767 a 32767)
        buf.append(int(v * vol * env * 32767))

    return pygame.mixer.Sound(buffer=buf)


def _barrido(f1, f2, dur, vol=0.25):
    """
    Genera un sonido que cambia gradualmente de frecuencia.
    Usado para efectos como "subir de tono" o "bajar de tono".

    Parametros:
        f1: frecuencia inicial en Hz
        f2: frecuencia final en Hz
        dur: duracion en segundos
    """
    sr = 22050
    n = int(sr * dur)
    buf = array.array('h')
    phase = 0.0

    for i in range(n):
        frac = i / n  # Progreso de 0.0 a 1.0
        freq = f1 + (f2 - f1) * frac  # Interpolar frecuencia

        # Acumular fase (necesario para ondas continuas)
        phase += 2 * math.pi * freq / sr

        # Envolvente de decaimiento
        env = max(0, 1.0 - frac * 0.5)
        buf.append(int(math.sin(phase) * vol * env * 32767))

    return pygame.mixer.Sound(buffer=buf)


class Sonidos:
    """
    Administra todos los sonidos del juego.
    Si hay algun error al crear los sonidos (por ejemplo, si
    el mixer no esta disponible), desactiva el audio silenciosamente.
    """

    def __init__(self):
        self.ok = True
        try:
            # Waka-waka: dos tonos que alternan (como Pac-Man original)
            # 150Hz y 200Hz con forma cuadrada (suena retro)
            self.chomp_a = _tono(150, 0.07, 0.15, 'square')
            self.chomp_b = _tono(200, 0.07, 0.15, 'square')

            # Power pellet: barrido ascendente (sube de tono)
            self.power = _barrido(300, 600, 0.25, 0.2)

            # Comer fantasma: barrido ascendente agudo
            self.eat_ghost = _barrido(500, 900, 0.3, 0.25)

            # Muerte: barrido descendente (baja de tono)
            self.death = _barrido(500, 100, 1.0, 0.3)

            # READY: tono corto ascendente
            self.ready = _barrido(400, 700, 0.4, 0.2)

        except Exception:
            self.ok = False  # Audio no disponible, funcionar sin sonido

        self._chomp_idx = 0      # Alterna entre chomp_a y chomp_b
        self._ultimo_chomp = 0   # Timestamp del ultimo chomp

    def chomp(self):
        """
        Reproduce el sonido de comer un punto.
        Alterna entre dos tonos para crear el efecto waka-waka.
        Tiene un cooldown de 80ms para no saturar el audio.
        """
        if not self.ok:
            return
        now = pygame.time.get_ticks()
        if now - self._ultimo_chomp < 80:
            return  # Cooldown: no reproducir si fue hace menos de 80ms
        self._ultimo_chomp = now
        snd = self.chomp_a if self._chomp_idx == 0 else self.chomp_b
        self._chomp_idx = 1 - self._chomp_idx  # Alternar
        snd.play()

    def play_power(self):
        """Reproduce el sonido de comer un power pellet."""
        if self.ok:
            self.power.play()

    def play_eat_ghost(self):
        """Reproduce el sonido de comer un fantasma."""
        if self.ok:
            self.eat_ghost.play()

    def play_death(self):
        """Reproduce el sonido de muerte de Pac-Man."""
        if self.ok:
            self.death.play()

    def play_ready(self):
        """Reproduce el sonido de 'READY!' al inicio de cada ronda."""
        if self.ok:
            self.ready.play()