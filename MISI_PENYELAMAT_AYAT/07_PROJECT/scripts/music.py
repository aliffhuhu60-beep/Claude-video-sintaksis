"""Penjana muzik & kesan bunyi bebas royalti (sintesis prosedur, dijana sendiri).
Output: 02_AUDIO/music/*.wav (48 kHz stereo)."""
import numpy as np, wave, os, sys

SR = 48000
OUT = sys.argv[1] if len(sys.argv) > 1 else "02_AUDIO/music"
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)


def write(name, x):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    peak = np.max(np.abs(x)) + 1e-9
    x = x / peak * 0.89
    w = wave.open(os.path.join(OUT, name), "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()


def t_(d):
    return np.arange(int(d * SR)) / SR


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.3):
    e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    na = max(na, 1)
    e[:na] = np.linspace(0, 1, na)
    if nd: e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def reverb(x, dur=2.5, mix=0.35, seed=1):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    ir = r.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir[0] = 0
    out = []
    for ch in range(2):
        irc = np.roll(ir, ch * 37) if ch else ir
        L = len(x) + n
        N = 1 << (L - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(x[:, ch], N) * np.fft.rfft(irc, N), N)[:len(x)]
        y /= (np.max(np.abs(y)) + 1e-9)
        out.append(y)
    wet = np.stack(out, 1) * (np.max(np.abs(x)) + 1e-9)
    return x * (1 - mix) + wet * mix


def lowpass(x, fc):
    # one-pole
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter  # noqa
    return lfilter([1 - a], [1, -a], x, axis=0)


try:
    from scipy.signal import lfilter  # noqa
except ImportError:
    os.system("pip install -q scipy >/dev/null 2>&1")


def pad(notes, dur, bright=0.3, detune=0.15):
    t = t_(dur)
    x = np.zeros(len(t))
    for n in notes:
        f = midi(n)
        for d in (-detune, 0, detune):
            ff = f * 2 ** (d / 12)
            ph = rng.uniform(0, 6.28)
            x += np.sin(2 * np.pi * ff * t + ph) + bright * 0.5 * np.sin(4 * np.pi * ff * t + ph) + bright * 0.2 * np.sin(6 * np.pi * ff * t)
    return x / (len(notes) * 3)


def pluck(f, dur, decay=3.0, bright=0.5):
    t = t_(dur)
    e = np.exp(-t * decay) * np.minimum(1, t / 0.004)
    return e * (np.sin(2 * np.pi * f * t) + bright * 0.4 * np.sin(4 * np.pi * f * t) * np.exp(-t * 4) + bright * 0.15 * np.sin(6 * np.pi * f * t) * np.exp(-t * 7))


def piano(f, dur, vel=1.0):
    t = t_(dur)
    e = np.exp(-t * 1.6) * np.minimum(1, t / 0.003)
    x = sum((0.6 ** k) * np.sin(2 * np.pi * f * (k + 1) * t * (1 + 0.0004 * k)) * np.exp(-t * (1 + k)) for k in range(5))
    return vel * e * x


def place(buf, sig, at, pan=0.0):
    i = int(at * SR)
    if i >= len(buf): return
    s = sig[: len(buf) - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(s), 0] += s * l * 1.414
    buf[i:i + len(s), 1] += s * r * 1.414


def stereo(x):
    return np.stack([x, x], 1)


def fade(x, fi=1.0, fo=2.0):
    n = len(x)
    e = np.ones(n)
    a, b = int(fi * SR), int(fo * SR)
    if a: e[:a] = np.linspace(0, 1, a) ** 2
    if b: e[-b:] = np.linspace(1, 0, b) ** 2
    return x * e[:, None]


# ---------- Kesan bunyi ----------
def impact():
    t = t_(4)
    boom = np.sin(2 * np.pi * (40 + 80 * np.exp(-t * 6)) * t) * np.exp(-t * 1.5)
    noise = rng.standard_normal(len(t)) * np.exp(-t * 9)
    noise = lowpass(noise, 900)
    x = stereo(boom * 1.0 + noise * 0.6)
    return reverb(x, 3.5, 0.4)


def whoosh(d=0.9, up=True):
    t = t_(d)
    n = rng.standard_normal(len(t))
    e = np.sin(np.pi * t / d) ** 2
    # sweeping band via variable lowpass blend
    lo = lowpass(n, 400); hi = n - lowpass(n, 2500)
    k = t / d if up else 1 - t / d
    x = (lo * (1 - k) + hi * k * 0.6) * e
    L = x * (1 - 0.5 * k); R = x * (0.5 + 0.5 * k)
    return reverb(np.stack([L, R], 1), 1.0, 0.25)


def riser(d=3.0):
    t = t_(d)
    n = rng.standard_normal(len(t))
    hp = n - lowpass(n, 1500)
    tone = np.sin(2 * np.pi * (200 + 600 * (t / d) ** 2) * t) * 0.2
    e = (t / d) ** 2
    return reverb(stereo((hp * 0.5 + tone) * e), 1.5, 0.3)


def success():
    buf = np.zeros((int(2.5 * SR), 2))
    for i, n in enumerate([72, 76, 79, 84]):
        place(buf, pluck(midi(n), 2.0, 3, 0.8) * 0.6, i * 0.08, pan=-0.3 + 0.2 * i)
    sp = np.zeros(len(buf))
    t = t_(2.5)
    sp += np.sin(2 * np.pi * midi(96) * t) * np.exp(-t * 5) * 0.2
    buf += stereo(sp)
    return reverb(buf, 1.8, 0.3)


def fail():
    t = t_(0.9)
    f = 180 * (1 - 0.3 * t)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * 1.5 * t) * 0.3
    x = lowpass(x * np.exp(-t * 3) * np.minimum(1, t / 0.01), 1800)
    return reverb(stereo(x), 0.8, 0.2)


def achievement():
    buf = np.zeros((int(6 * SR), 2))
    seq = [(67, 0), (72, 0.15), (76, 0.3), (79, 0.45), (84, 0.7)]
    for n, at in seq:
        place(buf, pluck(midi(n), 3, 2.0, 0.9) * 0.5, at, pan=rng.uniform(-.4, .4))
    chord = pad([60, 64, 67, 72, 76], 5, bright=0.6) * env_adsr(int(5 * SR), 0.05, 0.5, 0.6, 2.5)
    place(buf, chord * 0.7, 0.7)
    t = t_(5)
    sparkle = sum(np.sin(2 * np.pi * midi(n) * t) * np.exp(-((t - d) * 8) ** 2) for n, d in [(96, 1.0), (100, 1.2), (103, 1.4), (108, 1.6)])
    place(buf, sparkle * 0.15, 0.7)
    return reverb(buf, 3, 0.4)


def pop():
    t = t_(0.25)
    x = np.sin(2 * np.pi * (900 - 600 * t / 0.25) * t) * np.exp(-t * 25)
    return stereo(x * 0.6)


def tick():
    t = t_(0.08)
    return stereo(np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 80) * 0.5)


# ---------- Muzik latar ----------
def intro_suspense(d=62):
    buf = np.zeros((int(d * SR), 2))
    t = t_(d)
    drone = (np.sin(2 * np.pi * midi(38) * t) + 0.5 * np.sin(2 * np.pi * midi(45) * t + 0.3 * np.sin(2 * np.pi * 0.1 * t)))
    drone *= 0.35 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t) ** 2)
    buf += stereo(drone)
    # pulsing heartbeat
    for k in np.arange(0.5, 20, 1.0):
        th = t_(0.5)
        place(buf, np.sin(2 * np.pi * 55 * th) * np.exp(-th * 14) * 0.9, k)
        place(buf, np.sin(2 * np.pi * 50 * th) * np.exp(-th * 16) * 0.6, k + 0.25)
    # dissonant shimmer
    sh = pad([62, 63, 69], 20, bright=0.2) * np.linspace(0, 1, int(20 * SR)) * 0.4
    place(buf, sh, 0)
    # after 20s: wider, hopeful minor->major pad
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64], [45, 52, 57, 60]]
    for i in range(int((d - 20) // 5) + 1):
        c = chords[i % 4]
        place(buf, pad(c, 6.5, 0.4) * env_adsr(int(6.5 * SR), 1.5, 0.5, 0.8, 2.0) * 0.5, 20 + i * 5)
    for i, at in enumerate(np.arange(20, d - 2, 0.5)):
        c = chords[int((at - 20) // 5) % 4]
        place(buf, pluck(midi(c[i % 4] + 12), 1.2, 4, 0.4) * 0.18, at, pan=0.5 * np.sin(i))
    buf = reverb(buf, 3.5, 0.35)
    return fade(buf, 2.0, 4.0)


def documentary(d=180, seed=3, tempo=0.6):
    r = np.random.default_rng(seed)
    buf = np.zeros((int(d * SR), 2))
    prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    bar = 4.0
    for b in range(int(d / bar) + 1):
        c = prog[b % 4]
        place(buf, pad([c[0] - 12] + c, bar + 2, 0.25) * env_adsr(int((bar + 2) * SR), 1.0, 0.5, 0.7, 2.0) * 0.35, b * bar)
        for k in range(int(bar / tempo)):
            if r.random() < 0.75:
                n = c[r.integers(0, 3)] + 12 * r.integers(0, 2)
                place(buf, piano(midi(n), 2.5, 0.25), b * bar + k * tempo, pan=r.uniform(-0.5, 0.5))
    buf = reverb(buf, 3.0, 0.4, seed)
    return fade(buf, 3, 4)


def ambient(d=240, seed=5):
    buf = np.zeros((int(d * SR), 2))
    prog = [[50, 57, 62, 66], [47, 54, 59, 62], [43, 50, 55, 59], [45, 52, 57, 61]]
    bar = 8.0
    for b in range(int(d / bar) + 1):
        place(buf, pad(prog[b % 4], bar + 4, 0.15, 0.1) * env_adsr(int((bar + 4) * SR), 3, 0.5, 0.8, 4) * 0.4, b * bar)
    buf = reverb(buf, 4, 0.5, seed)
    return fade(buf, 3, 4)


def adventure(d=180, seed=9):
    r = np.random.default_rng(seed)
    buf = np.zeros((int(d * SR), 2))
    bpm = 112; beat = 60 / bpm
    prog = [[60, 64, 67], [57, 60, 64], [53, 57, 60], [55, 59, 62]]  # C Am F G
    nbars = int(d / (4 * beat)) + 1
    for b in range(nbars):
        c = prog[b % 4]; t0 = b * 4 * beat
        place(buf, pad(c, 4 * beat + 1, 0.4) * env_adsr(int((4 * beat + 1) * SR), 0.2, 0.3, 0.7, 0.8) * 0.25, t0)
        # bass
        for k in range(4):
            place(buf, pluck(midi(c[0] - 24), beat * 0.9, 5, 0.3) * 0.55, t0 + k * beat)
        # arp (8ths)
        pat = [0, 1, 2, 1, 0, 2, 1, 2]
        for k in range(8):
            n = c[pat[k]] + 12
            place(buf, pluck(midi(n), 0.6, 7, 0.9) * 0.22, t0 + k * beat / 2, pan=0.4 if k % 2 else -0.4)
        # light percussion: kick + shaker
        for k in range(4):
            th = t_(0.3)
            if k % 2 == 0:
                place(buf, np.sin(2 * np.pi * (50 + 70 * np.exp(-th * 30)) * th) * np.exp(-th * 12) * 0.5, t0 + k * beat)
            sh = r.standard_normal(int(0.06 * SR)) * np.exp(-np.linspace(0, 8, int(0.06 * SR))) * 0.08
            place(buf, sh - lowpass(sh, 4000), t0 + k * beat + beat / 2)
    buf = reverb(buf, 1.6, 0.22, seed)
    return fade(buf, 1.5, 3)


def outro_inspire(d=75):
    buf = np.zeros((int(d * SR), 2))
    prog = [[48, 55, 60, 64], [55, 59, 62, 67], [57, 60, 64, 69], [53, 57, 60, 65]]  # C G Am F
    bar = 3.2
    for b in range(int(d / bar) + 1):
        c = prog[b % 4]
        place(buf, pad([c[0] - 12] + c, bar + 2, 0.35) * env_adsr(int((bar + 2) * SR), 0.8, 0.4, 0.75, 1.8) * 0.4, b * bar)
        for k in range(8):
            n = c[[1, 2, 3, 2, 1, 3, 2, 3][k]] + 12
            place(buf, piano(midi(n), 2.0, 0.22), b * bar + k * bar / 8, pan=0.3 * np.sin(k))
    buf = reverb(buf, 3.5, 0.4, 11)
    return fade(buf, 2, 6)


if __name__ == "__main__":
    write("sfx_impact.wav", impact())
    write("sfx_whoosh.wav", whoosh())
    write("sfx_whoosh_down.wav", whoosh(0.7, False))
    write("sfx_riser.wav", riser())
    write("sfx_success.wav", success())
    write("sfx_fail.wav", fail())
    write("sfx_achievement.wav", achievement())
    write("sfx_pop.wav", pop())
    write("sfx_tick.wav", tick())
    write("mus_intro_suspense.wav", intro_suspense())
    write("mus_documentary.wav", documentary(200))
    write("mus_ambient.wav", ambient(420))
    write("mus_adventure.wav", adventure(200))
    write("mus_outro.wav", outro_inspire())
    print("done")
