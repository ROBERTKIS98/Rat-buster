"""Difficulty scaling curve, shared by the game screen."""


def get_difficulty(level):
    t = min(level, 300)
    holes = min(3 + t // 20, 9)
    max_rats = min(2 + t // 12, 9)
    speed = 90 + t * 0.9          # pixels/sec the rat travels toward its hole
    spawn_gap = max(1.1 - t * 0.003, 0.26)   # seconds between spawns
    base_time = max(45 - t // 8, 22)          # seconds for this city
    return {
        "holes": holes,
        "max_rats": max_rats,
        "speed": speed,
        "spawn_gap": spawn_gap,
        "base_time": base_time,
    }
