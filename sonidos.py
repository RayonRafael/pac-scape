import pygame
import array
import math


def _tono(freq, dur, vol=0.25, forma='sin'):
    sr = 22050
    n = int(sr * dur)
    buf = array.array('h')
    for i in range(n):
        t = i / sr
        env = max(0, 1.0 - (i / n) * 0.3)
        if forma == 'sin':
            v = math.sin(2 * math.pi * freq * t)
        else:
            v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        buf.append(int(v * vol * env * 32767))
    return pygame.mixer.Sound(buffer=buf)


def _barrido(f1, f2, dur, vol=0.25):
    sr = 22050
    n = int(sr * dur)
    buf = array.array('h')
    phase = 0.0
    for i in range(n):
        frac = i / n
        freq = f1 + (f2 - f1) * frac
        phase += 2 * math.pi * freq / sr
        env = max(0, 1.0 - frac * 0.5)
        buf.append(int(math.sin(phase) * vol * env * 32767))
    return pygame.mixer.Sound(buffer=buf)


def _siren(freq_baja, freq_alta, ciclos, dur_tono, vol=0.05):
    """Genera una sirena alternando dos frecuencias. Loopable."""
    sr = 22050
    muestras_tono = int(sr * dur_tono)
    buf = array.array('h')
    for ciclo in range(ciclos):
        for freq in [freq_baja, freq_alta]:
            for i in range(muestras_tono):
                t = i / sr
                v = math.sin(2 * math.pi * freq * t)
                buf.append(int(v * vol * 32767))
    return pygame.mixer.Sound(buffer=buf)


class Sonidos:
    def __init__(self):
        self.ok = True
        try:
            self.chomp_a = _tono(150, 0.07, 0.15, 'square')
            self.chomp_b = _tono(200, 0.07, 0.15, 'square')
            self.power = _barrido(300, 600, 0.25, 0.2)
            self.eat_ghost = _barrido(500, 900, 0.3, 0.25)
            self.death = _barrido(500, 100, 1.0, 0.3)
            self.ready = _barrido(400, 700, 0.4, 0.2)
            self.fruta_snd = _tono(800, 0.15, 0.2, 'sin')
            # Sirens de fondo (se reprocen en loop)
            self.siren_normal = _siren(280, 360, 4, 0.4, 0.05)
            self.siren_power  = _siren(400, 550, 6, 0.25, 0.07)
        except Exception:
            self.ok = False
        self._chomp_idx = 0
        self._ultimo_chomp = 0
        self._siren_actual = None

    def chomp(self):
        if not self.ok:
            return
        now = pygame.time.get_ticks()
        if now - self._ultimo_chomp < 80:
            return
        self._ultimo_chomp = now
        snd = self.chomp_a if self._chomp_idx == 0 else self.chomp_b
        self._chomp_idx = 1 - self._chomp_idx
        snd.play()

    def play_power(self):
        if self.ok:
            self.power.play()

    def play_eat_ghost(self):
        if self.ok:
            self.eat_ghost.play()

    def play_death(self):
        if self.ok:
            self.death.play()

    def play_ready(self):
        if self.ok:
            self.ready.play()

    def play_fruta(self):
        if self.ok:
            self.fruta_snd.play()

    def iniciar_siren_normal(self):
        if not self.ok:
            return
        if self._siren_actual != "normal":
            self._detener_siren_actual()
            self.siren_normal.play(-1)
            self._siren_actual = "normal"

    def iniciar_siren_power(self):
        if not self.ok:
            return
        if self._siren_actual != "power":
            self._detener_siren_actual()
            self.siren_power.play(-1)
            self._siren_actual = "power"

    def detener_siren(self):
        if not self.ok:
            return
        self._detener_siren_actual()
        self._siren_actual = None

    def _detener_siren_actual(self):
        if self._siren_actual == "normal":
            self.siren_normal.stop()
        elif self._siren_actual == "power":
            self.siren_power.stop()