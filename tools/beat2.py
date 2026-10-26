"""Original upbeat background loop (no samples, fully synthesized)."""
import numpy as np, wave, sys
np.random.seed(7)

SR = 44100
BPM = int(sys.argv[2]) if len(sys.argv)>2 else 112
DUR = float(sys.argv[4]) if len(sys.argv)>4 else 15.6
beat = 60 / BPM
n = int(SR * DUR)
out = np.zeros(n)

def add(sig, t):
    i = int(t * SR)
    if i >= n: return
    j = min(n, i + len(sig))
    out[i:j] += sig[: j - i]

def env(length, a=0.005, d=0.25):
    t = np.arange(int(length * SR)) / SR
    e = np.minimum(1, t / a) * np.exp(-t / d)
    return t, e

def kick():
    t, e = env(0.35, 0.001, 0.12)
    f = 50 + 90 * np.exp(-t * 30)
    return 0.9 * np.sin(2 * np.pi * np.cumsum(f) / SR) * e

def snare():
    t, e = env(0.2, 0.001, 0.06)
    return 0.35 * (np.random.randn(len(t)) * e + 0.4 * np.sin(2 * np.pi * 190 * t) * e)

def hat():
    t, e = env(0.05, 0.0005, 0.015)
    noise = np.random.randn(len(t))
    noise = np.diff(np.concatenate([[0], noise]))  # crude highpass
    return 0.12 * noise * e

def pluck(freq, length=0.45, vol=0.18):
    t, e = env(length, 0.003, 0.18)
    s = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * 2 * freq * t) + 0.15 * np.sin(2 * np.pi * 3 * freq * t)
    return vol * s * e

def pad(freqs, length, vol=0.05):
    t = np.arange(int(length * SR)) / SR
    e = np.minimum(1, t / 0.08) * np.minimum(1, (length - t) / 0.15)
    s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    return vol * s * e

TR = int(sys.argv[3]) if len(sys.argv)>3 else 0
def note(m): return 440 * 2 ** ((m + TR - 69) / 12)

# I–V–vi–IV in C, one chord per bar
prog = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
bass = [36, 43, 45, 41]
arp = [0, 1, 2, 1, 2, 1, 0, 2]

bar = 4 * beat
nbars = int(DUR / bar) + 1
for b in range(nbars):
    t0 = b * bar
    ch = prog[b % 4]
    add(pad([note(m) for m in ch], bar), t0)
    add(pluck(note(bass[b % 4]), 0.6, 0.3), t0)
    add(pluck(note(bass[b % 4]), 0.4, 0.22), t0 + 2.5 * beat)
    for k in range(8):
        add(pluck(note(ch[arp[k]] + 12), 0.3, 0.09), t0 + k * beat / 2)
    for k in range(4):
        add(kick(), t0 + k * beat)
        if k % 2 == 1: add(snare(), t0 + k * beat)
    for k in range(8):
        add(hat(), t0 + k * beat / 2 + beat / 4)

# fade in/out, normalize
fi, fo = int(0.01 * SR), int(0.4 * SR)
out[:fi] *= np.linspace(0, 1, fi)
out[-fo:] *= np.linspace(1, 0, fo)
out = out / np.max(np.abs(out)) * 0.8
pcm = (out * 32767).astype(np.int16)
stereo = np.repeat(pcm[:, None], 2, axis=1)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(stereo.tobytes())
