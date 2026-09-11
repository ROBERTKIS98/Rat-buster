"""
Generates all image assets for Ratbuster: World Tour.

Everything here is procedurally drawn with Pillow -- no third-party artwork,
so it is 100% safe to redistribute in the GitHub repo / APK. Images are
drawn at 4x resolution and downsampled with LANCZOS to get soft,
anti-aliased edges instead of jagged canvas shapes.

Run:  python tools/generate_images.py
Output: assets/images/*.png
"""
import math
import random
import os
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images")
os.makedirs(OUT, exist_ok=True)

SS = 4  # supersampling factor


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def save(img, name, size):
    img = img.resize(size, Image.LANCZOS)
    img.save(os.path.join(OUT, name))
    print("wrote", name, size)


# --------------------------------------------------------------------------
# RAT SPRITE (two running frames)
# --------------------------------------------------------------------------
def draw_rat(leg_phase=0):
    W, H = 240, 150
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    s = SS

    fur_dark = (66, 58, 50)
    fur_mid = (128, 116, 101)
    fur_light = (176, 165, 148)
    pink = (207, 141, 145)
    pink_dark = (168, 100, 105)

    cx, cy = 118 * s, 82 * s

    # --- tail: tapered wedge instead of a thin line so it survives downscale ---
    tail_wave = 8 * math.sin(leg_phase * math.pi) * s
    tx0, ty0 = cx - 74 * s, cy + 2 * s
    tx1, ty1 = cx - 118 * s, cy + 14 * s + tail_wave
    tx2, ty2 = cx - 150 * s, cy + 2 * s - tail_wave
    d.polygon(
        [(tx0, ty0 - 4 * s), (tx1, ty1 - 2 * s), (tx2, ty2), (tx1, ty1 + 2 * s), (tx0, ty0 + 4 * s)],
        fill=fur_dark,
    )

    # --- back leg cluster (far leg lifted+light, near leg planted+dark) ---
    swing = 10 * s * math.sin(leg_phase * math.pi)
    back_x = cx - 34 * s
    d.line([(back_x - 4 * s, cy + 24 * s), (back_x - 10 * s + swing, cy + 40 * s)], fill=fur_light, width=int(4.5 * s))
    d.ellipse([back_x - 15 * s + swing, cy + 37 * s, back_x - 4 * s + swing, cy + 46 * s], fill=fur_light)
    d.line([(back_x + 6 * s, cy + 26 * s), (back_x + 2 * s - swing, cy + 50 * s)], fill=fur_dark, width=int(6.5 * s))
    d.ellipse([back_x - 6 * s - swing, cy + 46 * s, back_x + 9 * s - swing, cy + 57 * s], fill=fur_dark)

    # --- body ---
    body_box = [cx - 80 * s, cy - 36 * s, cx + 50 * s, cy + 34 * s]
    d.ellipse(body_box, fill=fur_mid)

    # belly / underside shading (soft gradient darkening lower half)
    shadow_mask = Image.new("L", img.size, 0)
    sd = ImageDraw.Draw(shadow_mask)
    sd.ellipse(body_box, fill=255)
    grad = Image.new("L", img.size, 0)
    gd = ImageDraw.Draw(grad)
    band = int(72 * s)
    for i in range(band):
        v = int(255 * (i / band))
        gd.line([(0, int(cy - 36 * s) + i), (img.size[0], int(cy - 36 * s) + i)], fill=v)
    shade = Image.composite(grad, Image.new("L", img.size, 0), shadow_mask)
    dark_overlay = Image.new("RGBA", img.size, fur_dark + (0,))
    dark_overlay.putalpha(shade.point(lambda p: int(p * 0.5)))
    img.alpha_composite(dark_overlay)
    d = ImageDraw.Draw(img)

    # top-of-back highlight streak
    d.ellipse([cx - 62 * s, cy - 34 * s, cx + 2 * s, cy - 4 * s], fill=fur_light + (100,))

    # --- front leg cluster ---
    front_x = cx + 18 * s
    d.line([(front_x - 6 * s, cy + 26 * s), (front_x - 12 * s - swing, cy + 42 * s)], fill=fur_light, width=int(4.5 * s))
    d.ellipse([front_x - 18 * s - swing, cy + 39 * s, front_x - 7 * s - swing, cy + 48 * s], fill=fur_light)
    d.line([(front_x + 4 * s, cy + 28 * s), (front_x + 8 * s + swing, cy + 52 * s)], fill=fur_dark, width=int(6.5 * s))
    d.ellipse([front_x - 2 * s + swing, cy + 48 * s, front_x + 13 * s + swing, cy + 59 * s], fill=fur_dark)

    # --- head / snout ---
    head_c = (cx + 60 * s, cy - 8 * s)
    head_r = 30 * s
    d.ellipse([head_c[0] - head_r, head_c[1] - head_r, head_c[0] + head_r, head_c[1] + head_r], fill=fur_mid)
    # snout: rounded taper (ellipse blended into a soft point) rather than a hard triangle
    d.pieslice(
        [head_c[0] - 6 * s, head_c[1] - 18 * s, head_c[0] + 30 * s, head_c[1] + 18 * s],
        -55, 55, fill=fur_light,
    )
    d.ellipse([head_c[0] + 30 * s, head_c[1] - 9 * s, head_c[0] + 52 * s, head_c[1] + 9 * s], fill=fur_light)

    # --- ears: rounder, spaced further apart, cupped inner shading ---
    ear_r = 11 * s
    for ex, ey in ((head_c[0] - 16 * s, head_c[1] - head_r + 8 * s), (head_c[0] + 8 * s, head_c[1] - head_r + 2 * s)):
        d.ellipse([ex - ear_r, ey - ear_r * 1.1, ex + ear_r, ey + ear_r * 0.9], fill=fur_dark)
        d.ellipse([ex - ear_r * 0.5, ey - ear_r * 0.35, ex + ear_r * 0.62, ey + ear_r * 0.62], fill=pink)

    # --- eye (clear of the ears, upper-front of the head) ---
    ex, ey = head_c[0] + 14 * s, head_c[1] - 4 * s
    d.ellipse([ex - 4 * s, ey - 4 * s, ex + 4 * s, ey + 4 * s], fill=(18, 16, 14))
    d.ellipse([ex - 1.5 * s, ey - 2.8 * s, ex + 0.6 * s, ey - 0.8 * s], fill=(255, 255, 255))

    # --- nose ---
    nx, ny = head_c[0] + 49 * s, head_c[1]
    d.ellipse([nx - 6 * s, ny - 5 * s, nx + 6 * s, ny + 5 * s], fill=pink_dark)

    # --- whiskers (thicker so they survive downscale) ---
    for wy in (-6, 0, 6):
        d.line(
            [(nx - 2 * s, ny + wy * 0.6 * s), (nx + 26 * s, ny + wy * s)],
            fill=(235, 232, 225, 190),
            width=max(1, int(1.1 * s)),
        )

    return img


def make_rat_frames():
    for i, phase in enumerate([0.0, 1.0]):
        img = draw_rat(phase)
        save(img, f"rat_{i}.png", (140, 88))


# --------------------------------------------------------------------------
# HOLE / BURROW SPRITE
# --------------------------------------------------------------------------
def make_hole():
    W, H = 140, 90
    img = canvas(W, H)
    d = ImageDraw.Draw(img)
    s = SS
    cx, cy = W * s / 2, H * s / 2
    d.ellipse([cx - 60 * s, cy - 8 * s, cx + 60 * s, cy + 30 * s], fill=(40, 30, 22, 160))
    d.ellipse([cx - 48 * s, cy - 18 * s, cx + 48 * s, cy + 16 * s], fill=(20, 14, 10, 235))
    d.ellipse([cx - 30 * s, cy - 10 * s, cx + 30 * s, cy + 8 * s], fill=(5, 4, 3, 255))
    # dirt rim highlight
    d.arc([cx - 50 * s, cy - 20 * s, cx + 50 * s, cy + 18 * s], 200, 340, fill=(120, 90, 60, 200), width=int(3 * s))
    save(img, "hole.png", (70, 45))


# --------------------------------------------------------------------------
# ENVIRONMENT BACKGROUNDS (one per region)
# --------------------------------------------------------------------------
def sky_gradient(img, top, bottom, horizon_frac=0.55):
    w, h = img.size
    hy = int(h * horizon_frac)
    grad = Image.new("RGBA", (1, hy), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(hy):
        t = y / max(hy - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        gd.point((0, y), fill=c + (255,))
    grad = grad.resize((w, hy))
    img.alpha_composite(grad, (0, 0))
    return hy


def ground_fill(img, color, horizon_y):
    w, h = img.size
    d = ImageDraw.Draw(img)
    d.rectangle([0, horizon_y, w, h], fill=color + (255,))
    # subtle horizontal banding for texture
    rnd = random.Random(7)
    for y in range(horizon_y, h, 6):
        shade = rnd.randint(-10, 10)
        c = tuple(max(0, min(255, ch + shade)) for ch in color)
        d.line([(0, y), (w, y)], fill=c + (60,))


def sun(img, x, y, r, color):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(6, 0, -1):
        a = int(20 * (i / 6))
        gd.ellipse([x - r * i * 0.6, y - r * i * 0.6, x + r * i * 0.6, y + r * i * 0.6], fill=color + (a,))
    gd.ellipse([x - r, y - r, x + r, y + r], fill=color + (255,))
    img.alpha_composite(glow)


def make_bg_asia():
    W, H = 1280, 720
    img = canvas(W, H)
    s = SS
    hy = sky_gradient(img, (48, 18, 30), (150, 60, 48), 0.5)
    sun(img, W * s * 0.78, hy * 0.5, 60 * s, (232, 163, 61))
    ground_fill(img, (58, 38, 26), hy)
    d = ImageDraw.Draw(img)
    # pagoda-style skyline silhouette
    rnd = random.Random(1)
    x = 0
    while x < W * s:
        bw = rnd.randint(60, 130) * s
        bh = rnd.randint(90, 260) * s
        d.rectangle([x, hy - bh, x + bw, hy + 4 * s], fill=(30, 16, 18, 230))
        # roof
        d.polygon(
            [(x - 10 * s, hy - bh), (x + bw / 2, hy - bh - 26 * s), (x + bw + 10 * s, hy - bh)],
            fill=(20, 10, 12, 240),
        )
        # lantern glow dots
        if rnd.random() > 0.4:
            d.ellipse(
                [x + bw / 2 - 5 * s, hy - bh + 12 * s, x + bw / 2 + 5 * s, hy - bh + 22 * s],
                fill=(232, 163, 61, 220),
            )
        x += bw + rnd.randint(6, 24) * s
    save(img, "bg_asia.png", (W, H))


def make_bg_africa():
    W, H = 1280, 720
    img = canvas(W, H)
    s = SS
    hy = sky_gradient(img, (40, 30, 12), (214, 140, 60), 0.55)
    sun(img, W * s * 0.5, hy * 0.55, 70 * s, (250, 200, 90))
    ground_fill(img, (92, 68, 34), hy)
    d = ImageDraw.Draw(img)
    rnd = random.Random(2)
    # acacia tree silhouettes
    for tx in (0.12, 0.32, 0.85):
        bx = W * s * tx
        trunk_h = 90 * s
        d.line([(bx, hy + 4 * s), (bx + 6 * s, hy - trunk_h)], fill=(30, 20, 10, 255), width=int(6 * s))
        d.ellipse([bx - 55 * s, hy - trunk_h - 40 * s, bx + 65 * s, hy - trunk_h + 6 * s], fill=(35, 24, 12, 240))
    # savanna grass tufts
    for _ in range(40):
        gx = rnd.uniform(0, W) * s
        gy = hy + rnd.uniform(10, H - hy / s - 10) * s
        d.line([(gx, gy), (gx - 4 * s, gy - 14 * s)], fill=(60, 46, 20, 200), width=int(1.4 * s))
        d.line([(gx, gy), (gx + 5 * s, gy - 12 * s)], fill=(60, 46, 20, 200), width=int(1.4 * s))
    save(img, "bg_africa.png", (W, H))


def make_bg_europe():
    W, H = 1280, 720
    img = canvas(W, H)
    s = SS
    hy = sky_gradient(img, (18, 30, 42), (60, 92, 110), 0.52)
    ground_fill(img, (55, 58, 50), hy)
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    x = 0
    while x < W * s:
        bw = rnd.randint(70, 150) * s
        bh = rnd.randint(120, 300) * s
        shade = rnd.randint(20, 40)
        col = (shade, shade + 6, shade + 12, 235)
        d.rectangle([x, hy - bh, x + bw, hy + 4 * s], fill=col)
        # windows
        for wy in range(int(hy - bh + 16 * s), int(hy - 10 * s), int(28 * s)):
            for wx in range(int(x + 10 * s), int(x + bw - 10 * s), int(22 * s)):
                if rnd.random() > 0.35:
                    d.rectangle([wx, wy, wx + 10 * s, wy + 14 * s], fill=(232, 200, 130, 180))
        # roof triangle for variety
        if rnd.random() > 0.5:
            d.polygon([(x - 4 * s, hy - bh), (x + bw / 2, hy - bh - 24 * s), (x + bw + 4 * s, hy - bh)], fill=(25, 18, 16, 240))
        x += bw + rnd.randint(4, 14) * s
    save(img, "bg_europe.png", (W, H))


def make_bg_americas():
    W, H = 1280, 720
    img = canvas(W, H)
    s = SS
    hy = sky_gradient(img, (10, 30, 30), (30, 90, 80), 0.5)
    ground_fill(img, (40, 55, 42), hy)
    d = ImageDraw.Draw(img)
    rnd = random.Random(4)
    x = 0
    while x < W * s:
        bw = rnd.randint(50, 110) * s
        bh = rnd.randint(140, 340) * s
        col = (18 + rnd.randint(0, 14), 40 + rnd.randint(0, 14), 40 + rnd.randint(0, 14), 235)
        d.rectangle([x, hy - bh, x + bw, hy + 4 * s], fill=col)
        for wy in range(int(hy - bh + 14 * s), int(hy - 8 * s), int(20 * s)):
            for wx in range(int(x + 6 * s), int(x + bw - 6 * s), int(16 * s)):
                if rnd.random() > 0.5:
                    d.rectangle([wx, wy, wx + 7 * s, wy + 10 * s], fill=(120, 220, 210, 160))
        x += bw + rnd.randint(4, 12) * s
    save(img, "bg_americas.png", (W, H))


def make_bg_oceania():
    W, H = 1280, 720
    img = canvas(W, H)
    s = SS
    hy = sky_gradient(img, (20, 40, 55), (80, 150, 170), 0.55)
    sun(img, W * s * 0.2, hy * 0.4, 55 * s, (255, 210, 140))
    ground_fill(img, (150, 90, 55), hy)
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    # outback rock formations
    for rx, rw, rh in ((0.55, 220, 110), (0.7, 140, 70), (0.9, 90, 50)):
        bx = W * s * rx
        d.polygon(
            [(bx - rw * s / 2, hy + 4 * s), (bx - rw * s / 3, hy - rh * s), (bx + rw * s / 3, hy - rh * s), (bx + rw * s / 2, hy + 4 * s)],
            fill=(120, 55, 30, 240),
        )
    # scrub bushes
    for _ in range(24):
        gx = rnd.uniform(0, W) * s
        gy = hy + rnd.uniform(4, 60) * s
        d.ellipse([gx - 10 * s, gy - 8 * s, gx + 10 * s, gy + 4 * s], fill=(70, 70, 30, 200))
    save(img, "bg_oceania.png", (W, H))


def make_bg_caribbean():
    W, H = 1280, 720
    img = canvas(W, H)
    s = SS
    hy = sky_gradient(img, (20, 60, 90), (120, 200, 200), 0.5)
    sun(img, W * s * 0.82, hy * 0.35, 50 * s, (255, 235, 170))
    ground_fill(img, (210, 190, 140), hy)
    d = ImageDraw.Draw(img)
    # ocean strip just above the sand
    d.rectangle([0, hy - 30 * s, W * s, hy], fill=(30, 130, 150, 200))
    rnd = random.Random(6)
    for tx in (0.08, 0.22, 0.93):
        bx = W * s * tx
        trunk_h = 130 * s
        curve = 30 * s
        d.line([(bx, hy - 10 * s), (bx + curve, hy - trunk_h)], fill=(90, 60, 30, 255), width=int(7 * s))
        for a in range(-2, 3):
            leaf_x = bx + curve + a * 16 * s
            leaf_y = hy - trunk_h - abs(a) * 6 * s
            d.line([(bx + curve, hy - trunk_h), (leaf_x, leaf_y - 20 * s)], fill=(30, 110, 60, 255), width=int(10 * s))
    save(img, "bg_caribbean.png", (W, H))


def make_icon():
    W = H = 512
    img = canvas(W, H)
    s = SS
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W * s, H * s], radius=90 * s, fill=(15, 61, 62, 255))
    # mustard glow behind the rat
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([70 * s, 70 * s, W * s - 70 * s, H * s - 70 * s], fill=(232, 163, 61, 255))
    img.alpha_composite(glow)
    rat = draw_rat(0.0)
    rat = rat.resize((int(rat.width * 1.7), int(rat.height * 1.7)), Image.LANCZOS)
    rx = (img.width - rat.width) // 2 + 10 * s
    ry = (img.height - rat.height) // 2
    img.alpha_composite(rat, (rx, ry))
    save(img, "icon.png", (512, 512))


def make_presplash():
    W, H = 960, 960
    img = canvas(W, H)
    s = SS
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W * s, H * s], fill=(11, 46, 47, 255))
    rat = draw_rat(0.0)
    rat = rat.resize((int(rat.width * 2.6), int(rat.height * 2.6)), Image.LANCZOS)
    rx = (img.width - rat.width) // 2
    ry = (img.height - rat.height) // 2 - 40 * s
    img.alpha_composite(rat, (rx, ry))
    save(img, "presplash.png", (960, 960))


if __name__ == "__main__":
    make_rat_frames()
    make_hole()
    make_bg_asia()
    make_bg_africa()
    make_bg_europe()
    make_bg_americas()
    make_bg_oceania()
    make_bg_caribbean()
    make_icon()
    make_presplash()
    print("Done.")
