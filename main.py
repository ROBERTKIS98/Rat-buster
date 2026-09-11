"""
Ratbuster: World Tour
A rat-shooting arcade game across 300 city levels, built with Kivy so it can
be packaged into an Android APK with buildozer (see buildozer.spec and
.github/workflows/build-apk.yml).

Run on desktop for testing:  python main.py
"""
import os
import math
import random

os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, InstructionGroup, PushMatrix, PopMatrix, Rotate, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from kivy.storage.jsonstore import JsonStore
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.metrics import dp

from cities import CITIES, CONTINENTS, CONTINENT_THEME, get_city
from difficulty import get_difficulty

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(ROOT, "assets", "images")
SND_DIR = os.path.join(ROOT, "assets", "sounds")

# ---------------------------------------------------------------- palette --
BG_DEEP = (0.06, 0.18, 0.18, 1)
PANEL = (0.08, 0.29, 0.29, 1)
MUSTARD = (0.91, 0.64, 0.24, 1)
RUST = (0.78, 0.33, 0.23, 1)
CREAM = (0.95, 0.94, 0.91, 1)
CREAM_DIM = (0.79, 0.77, 0.72, 1)


def img_path(name):
    return os.path.join(IMG_DIR, name)


def snd_path(name):
    return os.path.join(SND_DIR, name)


# ============================================================================
# SOUND
# ============================================================================
class SoundBank:
    _cache = {}

    @classmethod
    def play(cls, name):
        snd = cls._cache.get(name)
        if snd is None:
            path = snd_path(name)
            if not os.path.exists(path):
                return
            snd = SoundLoader.load(path)
            cls._cache[name] = snd
        if snd:
            snd.stop()
            snd.play()


# ============================================================================
# PROGRESS PERSISTENCE
# ============================================================================
class Progress:
    """Thin wrapper around a JsonStore so progress survives app restarts,
    including on Android where the store lives in the app's private data dir."""

    def __init__(self, path):
        self.store = JsonStore(path)
        if not self.store.exists("progress"):
            self.store.put("progress", furthest_level=1, carry_time=0, carry_kills=0)

    @property
    def furthest_level(self):
        return self.store.get("progress")["furthest_level"]

    @property
    def carry_time(self):
        return self.store.get("progress")["carry_time"]

    @property
    def carry_kills(self):
        return self.store.get("progress")["carry_kills"]

    def save(self, furthest_level=None, carry_time=None, carry_kills=None):
        cur = self.store.get("progress")
        if furthest_level is not None:
            cur["furthest_level"] = furthest_level
        if carry_time is not None:
            cur["carry_time"] = carry_time
        if carry_kills is not None:
            cur["carry_kills"] = carry_kills
        self.store.put("progress", **cur)

    def reset(self):
        self.store.put("progress", furthest_level=1, carry_time=0, carry_kills=0)


# ============================================================================
# A single rat: owns its own canvas InstructionGroup so it can be added /
# removed from the game canvas independently as it spawns / dies / escapes.
# ============================================================================
class Rat:
    SPRITE_W = dp(62)
    SPRITE_H = dp(39)

    def __init__(self, textures, hole, speed, xr, yr):
        self.textures = textures  # list of run-cycle frame textures
        self.frame_idx = 0
        self.frame_timer = 0.0
        self.hole = hole
        self.speed = speed
        self.xr, self.yr = xr, yr  # normalized position, yr = fraction FROM TOP
        self.alive = True
        self.escaped = False

        self.group = InstructionGroup()
        self.push = PushMatrix()
        self.rot = Rotate(angle=0, origin=(0, 0))
        self.color = Color(1, 1, 1, 1)
        self.rect = Rectangle(texture=self.textures[0], pos=(0, 0), size=(self.SPRITE_W, self.SPRITE_H))
        self.pop = PopMatrix()
        for instr in (self.push, self.rot, self.color, self.rect, self.pop):
            self.group.add(instr)

    def screen_pos(self, w, h):
        return self.xr * w, h - self.yr * h

    def update(self, w, h, dt):
        self.frame_timer += dt
        if self.frame_timer > 0.12:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.textures)
            self.rect.texture = self.textures[self.frame_idx]

        px, py = self.screen_pos(w, h)
        hx, hy = self.hole["xr"] * w, h - self.hole["yr"] * h
        dx, dy = hx - px, hy - py
        dist = math.hypot(dx, dy) or 1.0
        step = self.speed * dt
        self.xr += (dx / dist) * (step / w)
        self.yr -= (dy / dist) * (step / h)  # yr measured from top, dy positive means moving down on screen

        if dist < dp(22):
            self.escaped = True
            self.alive = False
            return

        angle = math.degrees(math.atan2(dy, dx))
        self.rot.angle = angle
        self.rot.origin = (px, py)
        self.rect.pos = (px - self.SPRITE_W / 2, py - self.SPRITE_H / 2)

    def hit_test(self, px, py, w, h, radius=None):
        radius = radius if radius is not None else dp(34)
        rx, ry = self.screen_pos(w, h)
        return math.hypot(rx - px, ry - py) <= radius


# ============================================================================
# THE GAME CANVAS WIDGET
# ============================================================================
class GameArea(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rat_textures = [
            CoreImage(img_path("rat_0.png")).texture,
            CoreImage(img_path("rat_1.png")).texture,
        ]
        self.hole_texture = CoreImage(img_path("hole.png")).texture
        self.bg_textures = {}

        self.bg_group = InstructionGroup()
        self.holes_group = InstructionGroup()
        self.crosshair_group = InstructionGroup()
        self.canvas.add(self.bg_group)
        self.canvas.add(self.holes_group)
        self.canvas.add(self.crosshair_group)

        self.rats = []
        self.holes = []
        self.continent = "Asia"
        self.running = False
        self.mouse_pos = (-1000, -1000)

        self.diff = get_difficulty(1)
        self.time_since_spawn = 999
        self.kills = 0
        self.kills_required = 25
        self.time_left = 45.0

        # callbacks set by the screen that owns us
        self.on_kill = lambda: None
        self.on_cleared = lambda: None
        self.on_time_out = lambda: None
        self.on_tick = lambda: None

        self.bind(size=self._redraw_static, pos=self._redraw_static)
        Clock.schedule_interval(self._update, 1 / 60)

    # ---------------- level setup ----------------
    def load_level(self, level, kills_start, time_start, diff):
        self.diff = diff
        self.kills = kills_start
        self.time_left = time_start
        self.time_since_spawn = 999
        city = get_city(level)
        self.continent = city["continent"]
        theme = CONTINENT_THEME[self.continent]
        if theme["bg"] not in self.bg_textures:
            self.bg_textures[theme["bg"]] = CoreImage(img_path(theme["bg"])).texture
        self.bg_texture = self.bg_textures[theme["bg"]]

        rng = random.Random(level * 7919 + 13)
        self.holes = []
        for _ in range(diff["holes"]):
            margin = 0.1
            xr = margin + rng.random() * (1 - margin * 2)
            yr = 0.58 + rng.random() * 0.32  # lower part of screen (ground), from top
            self.holes.append({"xr": xr, "yr": yr})

        for rat in self.rats:
            rat.group.clear()
        self.rats = []
        self.running = True
        self._redraw_static()

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True

    # ---------------- rendering ----------------
    def _redraw_static(self, *args):
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        self.bg_group.clear()
        if getattr(self, "bg_texture", None):
            self.bg_group.add(Color(1, 1, 1, 1))
            self.bg_group.add(Rectangle(texture=self.bg_texture, pos=self.pos, size=self.size))

        self.holes_group.clear()
        self.holes_group.add(Color(1, 1, 1, 1))
        hw, hh = dp(46), dp(30)
        for hole in self.holes:
            hx, hy = hole["xr"] * w + self.x, h - hole["yr"] * h + self.y
            self.holes_group.add(Rectangle(texture=self.hole_texture, pos=(hx - hw / 2, hy - hh / 2), size=(hw, hh)))

    def _draw_crosshair(self):
        self.crosshair_group.clear()
        x, y = self.mouse_pos
        if x < -900:
            return
        theme = CONTINENT_THEME.get(self.continent, CONTINENT_THEME["Asia"])
        self.crosshair_group.add(Color(*theme["accent"]))
        self.crosshair_group.add(Line(circle=(x, y, dp(18)), width=dp(1.6)))
        gap, length = dp(7), dp(14)
        for dx0, dy0, dx1, dy1 in (
            (-gap - length, 0, -gap, 0), (gap, 0, gap + length, 0),
            (0, -gap - length, 0, -gap), (0, gap, 0, gap + length),
        ):
            self.crosshair_group.add(Line(points=[x + dx0, y + dy0, x + dx1, y + dy1], width=dp(1.6)))

    # ---------------- game loop ----------------
    def _update(self, dt):
        w, h = self.size
        if w <= 0 or h <= 0:
            return
        self._draw_crosshair()
        if not self.running:
            return

        self.time_left -= dt
        self.on_tick()
        if self.time_left <= 0:
            self.time_left = 0
            self.running = False
            self.on_time_out()
            return

        self.time_since_spawn += dt
        if self.time_since_spawn > self.diff["spawn_gap"] and len(self.rats) < self.diff["max_rats"]:
            self._spawn_rat()
            self.time_since_spawn = 0

        still_alive = []
        for rat in self.rats:
            rat.update(w, h, dt)
            if not rat.alive:
                self.canvas.remove(rat.group)
                if rat.escaped:
                    SoundBank.play("escape.wav")
            else:
                still_alive.append(rat)
        self.rats = still_alive

    def _spawn_rat(self):
        w, h = self.size
        side = random.randint(0, 3)
        if side == 0:
            xr, yr = random.random(), -0.05
        elif side == 1:
            xr, yr = 1.05, 0.3 + random.random() * 0.5
        elif side == 2:
            xr, yr = random.random(), 1.05
        else:
            xr, yr = -0.05, 0.3 + random.random() * 0.5
        hole = random.choice(self.holes)
        speed = self.diff["speed"] * (0.85 + random.random() * 0.3) * dp(1)
        rat = Rat(self.rat_textures, hole, speed, xr, yr)
        self.rats.append(rat)
        self.canvas.add(rat.group)

    # ---------------- input ----------------
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self.mouse_pos = touch.pos
        self._try_shoot(*touch.pos)
        return True

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.mouse_pos = touch.pos
        return super().on_touch_move(touch)

    def _try_shoot(self, x, y):
        if not self.running:
            return
        w, h = self.size
        best, best_d = None, dp(40)
        for rat in self.rats:
            if not rat.alive:
                continue
            rx, ry = rat.screen_pos(w, h)
            d = math.hypot(rx - x, ry - y)
            if d < best_d:
                best_d, best = d, rat
        if best:
            best.alive = False
            self.canvas.remove(best.group)
            self.rats.remove(best)
            self.kills += 1
            SoundBank.play("shot.wav")
            SoundBank.play("squeak.wav")
            self.on_kill()
            if self.kills >= self.kills_required:
                self.on_cleared()
        else:
            SoundBank.play("shot.wav")


# ============================================================================
# MENU SCREEN
# ============================================================================
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        with root.canvas.before:
            Color(*BG_DEEP)
            self._bgrect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._sync_bg, size=self._sync_bg)

        col = BoxLayout(orientation="vertical", spacing=dp(14), padding=dp(24),
                         size_hint=(0.86, None), height=dp(340),
                         pos_hint={"center_x": 0.5, "center_y": 0.55})

        title = Label(text="RATBUSTER", font_size=dp(42), bold=True, color=MUSTARD, size_hint_y=None, height=dp(60))
        subtitle = Label(text="WORLD TOUR  --  300 CITIES", font_size=dp(14), color=CREAM_DIM, size_hint_y=None, height=dp(24))

        play_btn = Button(text="Play", font_size=dp(18), bold=True, size_hint_y=None, height=dp(52),
                           background_normal="", background_color=MUSTARD, color=(0.06, 0.1, 0.1, 1))
        play_btn.bind(on_release=self._play)

        map_btn = Button(text="City Map", font_size=dp(16), size_hint_y=None, height=dp(48),
                          background_normal="", background_color=PANEL, color=CREAM)
        map_btn.bind(on_release=self._open_map)

        reset_btn = Button(text="Reset Progress", font_size=dp(14), size_hint_y=None, height=dp(40),
                            background_normal="", background_color=RUST, color=CREAM)
        reset_btn.bind(on_release=self._reset)

        self.progress_label = Label(text="", font_size=dp(13), color=CREAM_DIM, size_hint_y=None, height=dp(30))

        col.add_widget(title)
        col.add_widget(subtitle)
        col.add_widget(Widget(size_hint_y=None, height=dp(10)))
        col.add_widget(play_btn)
        col.add_widget(map_btn)
        col.add_widget(reset_btn)
        col.add_widget(self.progress_label)
        root.add_widget(col)
        self.add_widget(root)

    def _sync_bg(self, inst, *a):
        self._bgrect.pos = inst.pos
        self._bgrect.size = inst.size

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        fl = app.progress.furthest_level
        city = get_city(fl)
        if fl <= 1:
            self.progress_label.text = f"New game -- start in {CITIES[0]['name']}"
        else:
            self.progress_label.text = f"Furthest: Level {fl} -- {city['name']}, {city['continent']}"

    def _play(self, *a):
        app = App.get_running_app()
        app.start_game(app.progress.furthest_level, use_carry=True)

    def _open_map(self, *a):
        self.manager.current = "map"

    def _reset(self, *a):
        App.get_running_app().progress.reset()
        self.on_pre_enter()


# ============================================================================
# MAP SCREEN
# ============================================================================
class CityRow(RecycleDataViewBehavior, BoxLayout):
    level = NumericProperty(0)
    name = StringProperty("")
    continent = StringProperty("")
    unlocked = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.padding = (dp(12), dp(6))
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(44)
        with self.canvas.before:
            self._c = Color(1, 1, 1, 0.0)
            self._r = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

        self.num_lbl = Label(text="", font_size=dp(13), bold=True, color=MUSTARD, size_hint_x=None, width=dp(46))
        self.name_lbl = Label(text="", font_size=dp(15), color=CREAM, halign="left", valign="middle")
        self.name_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.region_lbl = Label(text="", font_size=dp(11), color=CREAM_DIM, size_hint_x=None, width=dp(90))
        self.add_widget(self.num_lbl)
        self.add_widget(self.name_lbl)
        self.add_widget(self.region_lbl)

    def _sync(self, *a):
        self._r.pos = self.pos
        self._r.size = self.size

    def refresh_view_attrs(self, rv, index, data):
        self.level = data["level"]
        self.name = data["name"]
        self.continent = data["continent"]
        self.unlocked = data["unlocked"]
        self.num_lbl.text = f"#{self.level}"
        self.name_lbl.text = self.name if self.unlocked else f"{self.name}  [locked]"
        self.name_lbl.color = CREAM if self.unlocked else CREAM_DIM
        self.region_lbl.text = self.continent
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.unlocked:
            App.get_running_app().start_game(self.level, use_carry=(self.level == App.get_running_app().progress.furthest_level))
            return True
        return super().on_touch_down(touch)


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_tab = "Asia"
        root = BoxLayout(orientation="vertical")
        with root.canvas.before:
            Color(*BG_DEEP)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self._sync_bg, size=self._sync_bg)

        header = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(10))
        header.add_widget(Label(text="Choose a City", font_size=dp(20), bold=True, color=MUSTARD))
        back_btn = Button(text="Back", size_hint=(None, None), size=(dp(80), dp(36)),
                           background_normal="", background_color=PANEL, color=CREAM)
        back_btn.bind(on_release=lambda *a: setattr(self.manager, "current", "menu"))
        header.add_widget(back_btn)
        root.add_widget(header)

        tabs = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(8), 0), spacing=dp(6))
        self.tab_buttons = {}
        for cont in CONTINENTS:
            b = ToggleButton(text=cont, group="continent", font_size=dp(12),
                              background_normal="", background_color=PANEL, color=CREAM_DIM,
                              state="down" if cont == self.active_tab else "normal")
            b.bind(on_release=lambda inst, c=cont: self._select_tab(c))
            self.tab_buttons[cont] = b
            tabs.add_widget(b)
        root.add_widget(tabs)

        self.rv = RecycleView(size_hint=(1, 1))
        box = RecycleBoxLayout(default_size=(None, dp(44)), default_size_hint=(1, None),
                                size_hint_y=None, orientation="vertical", spacing=dp(2),
                                padding=(dp(6), dp(6)))
        box.bind(minimum_height=box.setter("height"))
        self.rv.add_widget(box)  # this auto-assigns self.rv.layout_manager = box
        self.rv.viewclass = CityRow  # must be set AFTER layout_manager exists (it's an alias property)
        root.add_widget(self.rv)

        self.add_widget(root)

    def _sync_bg(self, inst, *a):
        self._bg.pos = inst.pos
        self._bg.size = inst.size

    def _select_tab(self, cont):
        self.active_tab = cont
        self._refresh()

    def on_pre_enter(self, *args):
        self._refresh()

    def _refresh(self):
        app = App.get_running_app()
        furthest = app.progress.furthest_level
        data = []
        for c in CITIES:
            if c["continent"] != self.active_tab:
                continue
            data.append({
                "level": c["level"], "name": c["name"], "continent": c["continent"],
                "unlocked": c["level"] <= furthest,
            })
        self.rv.data = data


# ============================================================================
# OVERLAY POPUPS
# ============================================================================
def make_popup_body(title_text, lines, buttons):
    body = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(20))
    body.add_widget(Label(text=title_text, font_size=dp(24), bold=True, color=MUSTARD, size_hint_y=None, height=dp(40)))
    for line in lines:
        body.add_widget(Label(text=line, font_size=dp(14), color=CREAM_DIM, size_hint_y=None, height=dp(24)))
    btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
    for label, cb, color in buttons:
        b = Button(text=label, background_normal="", background_color=color, color=(0.06, 0.1, 0.1, 1) if color == MUSTARD else CREAM)
        b.bind(on_release=cb)
        btn_row.add_widget(b)
    body.add_widget(btn_row)
    return body


# ============================================================================
# GAME SCREEN
# ============================================================================
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level = 1
        self._popup = None

        root = FloatLayout()
        self.game_area = GameArea(size_hint=(1, 1))
        self.game_area.on_kill = self._on_kill
        self.game_area.on_cleared = self._on_cleared
        self.game_area.on_time_out = self._on_time_out
        self.game_area.on_tick = self._on_tick
        root.add_widget(self.game_area)

        # ---------------- HUD ----------------
        hud = FloatLayout(size_hint=(1, 1))

        left_col = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(190), dp(70)),
                              pos_hint={"x": 0.02, "top": 0.98}, spacing=dp(4))
        self.city_label = self._pill_label("City", dp(13))
        self.kills_label = self._pill_label("Kills 0/25", dp(13))
        self.kills_bar = ProgressBar(max=25, value=0, size_hint_y=None, height=dp(8))
        left_col.add_widget(self.city_label)
        left_col.add_widget(self.kills_label)
        left_col.add_widget(self.kills_bar)
        hud.add_widget(left_col)

        self.timer_label = Label(text="45", font_size=dp(26), bold=True, color=MUSTARD,
                                  size_hint=(None, None), size=(dp(80), dp(40)),
                                  pos_hint={"right": 0.98, "top": 0.98})
        hud.add_widget(self.timer_label)

        self.bonus_label = Label(text="", font_size=dp(11), color=CREAM_DIM,
                                  size_hint=(None, None), size=(dp(220), dp(20)),
                                  pos_hint={"right": 0.98, "top": 0.86})
        hud.add_widget(self.bonus_label)

        pause_btn = Button(text="||", font_size=dp(14), size_hint=(None, None), size=(dp(38), dp(38)),
                            pos_hint={"right": 0.98, "top": 0.99}, background_normal="",
                            background_color=(0.04, 0.15, 0.15, 0.85), color=CREAM)
        # keep pause button above timer visually by placing it at very top-right, timer just below
        pause_btn.pos_hint = {"right": 0.98, "top": 1.0}
        self.timer_label.pos_hint = {"right": 0.98, "top": 0.9}
        hud.add_widget(pause_btn)
        pause_btn.bind(on_release=self._pause)

        self.next_btn = Button(text="Next City >", font_size=dp(16), bold=True,
                                size_hint=(None, None), size=(dp(160), dp(48)),
                                pos_hint={"center_x": 0.5, "y": 0.03},
                                background_normal="", background_color=MUSTARD, color=(0.06, 0.1, 0.1, 1))
        self.next_btn.opacity = 0
        self.next_btn.disabled = True
        self.next_btn.bind(on_release=self._advance)
        hud.add_widget(self.next_btn)

        root.add_widget(hud)
        self.add_widget(root)

    def _pill_label(self, text, fs):
        lbl = Label(text=text, font_size=fs, bold=True, color=CREAM, size_hint_y=None, height=dp(24))
        return lbl

    # ---------------- lifecycle ----------------
    def start_level(self, level, use_carry):
        app = App.get_running_app()
        self.level = level
        city = get_city(level)
        diff = get_difficulty(level)
        carry_time = app.progress.carry_time if use_carry else 0
        carry_kills = min(app.progress.carry_kills, 24) if use_carry else 0

        kills_start = carry_kills
        time_start = diff["base_time"] + carry_time
        self.game_area.kills_required = 25
        self.game_area.load_level(level, kills_start, time_start, diff)

        self.city_label.text = f"#{level}  {city['name']} ({city['continent']})"
        self.kills_bar.max = 25
        bonus_bits = []
        if carry_time > 0:
            bonus_bits.append(f"+{carry_time}s carried")
        if carry_kills > 0:
            bonus_bits.append(f"+{carry_kills} kills carried")
        self.bonus_label.text = " . ".join(bonus_bits)
        self.next_btn.opacity = 0
        self.next_btn.disabled = True
        self._close_popup()
        self._refresh_hud()

    def _refresh_hud(self):
        ga = self.game_area
        self.kills_label.text = f"Kills {min(ga.kills, ga.kills_required)}/{ga.kills_required}"
        self.kills_bar.value = min(ga.kills, ga.kills_required)
        self.timer_label.text = str(max(0, math.ceil(ga.time_left)))
        self.timer_label.color = RUST if ga.time_left < 10 else MUSTARD

    def _on_tick(self):
        self._refresh_hud()

    def _on_kill(self):
        self._refresh_hud()

    def _on_cleared(self):
        self._refresh_hud()
        self.next_btn.opacity = 1
        self.next_btn.disabled = False

    def _on_time_out(self):
        self._refresh_hud()
        SoundBank.play("level_fail.wav")
        city = get_city(self.level)
        body = make_popup_body(
            "Time's Up!",
            [f"You caught {min(self.game_area.kills, 25)} of 25 rats in {city['name']}."],
            [
                ("Retry City", lambda *a: self._retry(), MUSTARD),
                ("Back to Map", lambda *a: self._to_menu(), PANEL),
            ],
        )
        self._show_popup(body)

    def _pause(self, *a):
        self.game_area.pause()
        body = make_popup_body("Paused", [], [
            ("Resume", lambda *a: self._resume(), MUSTARD),
            ("Quit to Menu", lambda *a: self._to_menu(), PANEL),
        ])
        self._show_popup(body)

    def _resume(self, *a):
        self._close_popup()
        self.game_area.resume()

    def _retry(self, *a):
        self._close_popup()
        self.start_level(self.level, use_carry=False)

    def _advance(self, *a):
        app = App.get_running_app()
        leftover_time = min(round(self.game_area.time_left), 20)
        bonus_kills = min(max(self.game_area.kills - 25, 0), 10)
        app.progress.save(
            furthest_level=max(app.progress.furthest_level, self.level + 1),
            carry_time=leftover_time,
            carry_kills=bonus_kills,
        )
        SoundBank.play("level_clear.wav")
        if self.level >= 300:
            body = make_popup_body("You beat the world!", ["All 300 cities cleared. Legendary."],
                                    [("Back to Menu", lambda *a: self._to_menu(), MUSTARD)])
            self._show_popup(body)
            return
        self.start_level(self.level + 1, use_carry=True)

    def _to_menu(self, *a):
        self._close_popup()
        self.game_area.pause()
        self.manager.current = "menu"

    def _show_popup(self, body):
        self._close_popup()
        self._popup = Popup(content=body, size_hint=(0.86, None), height=dp(240),
                             auto_dismiss=False, separator_height=0,
                             background_color=(0.04, 0.14, 0.14, 0.97))
        self._popup.open()

    def _close_popup(self):
        if self._popup:
            self._popup.dismiss()
            self._popup = None

    def on_leave(self, *a):
        self.game_area.pause()


# ============================================================================
# APP
# ============================================================================
class RatbusterApp(App):
    title = "Ratbuster: World Tour"

    def build(self):
        Window.clearcolor = BG_DEEP
        self.progress = Progress(os.path.join(self.user_data_dir, "ratbuster_progress.json"))

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(MapScreen(name="map"))
        sm.add_widget(GameScreen(name="game"))
        sm.current = "menu"
        self.sm = sm
        return sm

    def start_game(self, level, use_carry):
        self.sm.current = "game"
        game_screen = self.sm.get_screen("game")
        game_screen.start_level(level, use_carry)


if __name__ == "__main__":
    RatbusterApp().run()
