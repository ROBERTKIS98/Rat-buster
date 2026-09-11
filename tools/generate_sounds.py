"""
Synthesizes all sound effects for Ratbuster: World Tour using pure math
(numpy) -- no sampled/recorded audio, so there is zero licensing risk in
redistributing these inside the GitHub repo / APK.

Run:  python tools/generate_sounds.py
Output: assets/sounds/*.wav
"""
import os
import numpy as np
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sounds")
os.makedirs(OUT, exist_ok=True)

SR = 44100


def write_wav(name, samples):
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    path = os.path.join(OUT, name)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", name, f"{len(samples)/SR:.2f}s")


def envelope(n, attack, release):
    e = np.ones(n)
    a = int(attack * SR)
    r = int(release * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    if r > 0:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def shot_sound():
    dur = 0.16
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = np.random.uniform(-1, 1, n)
    thump = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 28)
    crack = noise * np.exp(-t * 45)
    sig = crack * 0.75 + thump * 0.6
    sig *= envelope(n, 0.001, 0.1)
    write_wav("shot.wav", sig)


def squeak_sound():
    dur = 0.18
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    freq = 1500 + 900 * (t / dur)
    sig = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    sig += 0.3 * np.sin(2 * np.pi * np.cumsum(freq * 2) / SR)
    sig *= envelope(n, 0.005, 0.12)
    write_wav("squeak.wav", sig * 0.6)


def escape_sound():
    dur = 0.14
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    freq = 900 - 500 * (t / dur)
    sig = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    sig *= envelope(n, 0.002, 0.1)
    write_wav("escape.wav", sig * 0.35)


def level_clear_sound():
    notes = [523.25, 659.25, 783.99, 1046.5]  # C5 E5 G5 C6 major arpeggio
    seg = 0.13
    n_seg = int(seg * SR)
    sig = np.zeros(0)
    for f in notes:
        t = np.linspace(0, seg, n_seg, endpoint=False)
        tone = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2 * t)
        tone *= envelope(n_seg, 0.005, 0.09)
        sig = np.concatenate([sig, tone])
    write_wav("level_clear.wav", sig * 0.5)


def level_fail_sound():
    notes = [392.0, 329.63, 261.63]  # G4 E4 C4 descending
    seg = 0.18
    n_seg = int(seg * SR)
    sig = np.zeros(0)
    for f in notes:
        t = np.linspace(0, seg, n_seg, endpoint=False)
        tone = np.sin(2 * np.pi * f * t) * (1 - 0.3 * t / seg)
        tone *= envelope(n_seg, 0.01, 0.12)
        sig = np.concatenate([sig, tone])
    write_wav("level_fail.wav", sig * 0.5)


def click_sound():
    dur = 0.05
    n = int(dur * SR)
    t = np.linspace(0, dur, n, endpoint=False)
    sig = np.sin(2 * np.pi * 900 * t) * np.exp(-t * 90)
    write_wav("click.wav", sig * 0.4)


if __name__ == "__main__":
    shot_sound()
    squeak_sound()
    escape_sound()
    level_clear_sound()
    level_fail_sound()
    click_sound()
    print("Done.")
