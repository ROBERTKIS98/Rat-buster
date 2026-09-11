# Ratbuster: World Tour 🐀

A rat-shooting arcade game with **300 city levels** — 50 in Asia, 70 in
Africa, 70 in Europe, and 110 across the Americas, Oceania, and the
Caribbean. Rats scurry in from the edge of the screen toward burrows —
shoot them before they reach cover. Clear 25 rats to beat a city; leftover
time and bonus kills carry over into the next one. Progress is saved
automatically.

Built with **Python + [Kivy](https://kivy.org)** so it can be packaged into
a real Android APK with [Buildozer](https://github.com/kivy/buildozer).

## Getting the APK

You don't need to build anything yourself:

1. Go to the **Actions** tab of this repository.
2. Open the latest successful **"Build Android APK"** run.
3. Download the `ratbuster-apk` artifact — that's your installable `.apk`.

If you push a tag like `v1.0.0`, the workflow also attaches the APK to a
**GitHub Release**, so it's directly downloadable from the repo's Releases
page without digging through Actions.

> The APK is built automatically by GitHub's own servers every time this
> repo is pushed to (see `.github/workflows/build-apk.yml`). Building an
> Android APK requires the Android SDK/NDK toolchain (several GB of
> downloads), so it isn't something you build inside a typical dev sandbox
> — GitHub Actions does the heavy lifting for you.

## Running it on a desktop first (recommended)

Before waiting on an APK build, it's much faster to just run the game
directly with Python:

```bash
pip install -r requirements.txt
python tools/generate_images.py   # only needed once, or after editing art
python tools/generate_sounds.py   # only needed once, or after editing sound
python main.py
```

## Building the APK yourself (Linux)

```bash
pip install buildozer cython
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf \
    libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev
buildozer android debug
```

The first build downloads the Android SDK/NDK and will take a while. The
resulting APK lands in `bin/`.

## Project layout

```
main.py                  Kivy app: screens, game loop, persistence
cities.py                 The 300-city dataset + continent theming
difficulty.py             Level difficulty curve (rats, speed, time)
tools/generate_images.py  Procedurally draws the rat sprites & city
                           backdrops with Pillow (no external art assets)
tools/generate_sounds.py  Synthesizes the sound effects with numpy
                           (no sampled/recorded audio)
assets/images/            Generated PNGs (rat frames, holes, 6 continent
                           backdrops, icon, splash screen)
assets/sounds/            Generated WAVs (shot, squeak, escape, level
                           clear/fail, click)
buildozer.spec            Android packaging configuration
.github/workflows/        CI that builds & publishes the APK
```

## Why the art and sound are all generated, not downloaded

Everything visual and audible in `assets/` is produced by the two scripts
in `tools/` — the rat sprites and city backdrops are drawn with Pillow
(vector shapes, gradients, and supersampled anti-aliasing), and the sound
effects are synthesized waveforms (noise bursts, sine sweeps, chimes) built
with numpy. Nothing is a downloaded photo, sample pack, or third-party
asset, so there are no licensing questions about redistributing it in this
public repo or inside the APK. If you'd rather use hand-drawn art or
recorded SFX, drop replacement files into `assets/images` / `assets/sounds`
using the same filenames and skip re-running the generator scripts.

## Gameplay notes

- Each city requires **25 kills** to clear, within a time limit that
  shrinks slightly as you progress (45s down to a 22s floor).
- Difficulty scales with level: more burrows, more rats on screen at once,
  and faster rats.
- Clearing a city with time or bonus kills to spare carries up to **20
  bonus seconds** and **10 bonus kills** into the next city.
- Miss the 25-kill target before time runs out and you can retry the same
  city (no bonus carried into a retry).
- The City Map screen lets you replay any city you've already unlocked.
