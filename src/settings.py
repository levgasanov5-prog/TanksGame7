WIDTH, HEIGHT = 900, 600
FPS = 60
TANK_SIZE = 40
FULLSCREEN = True

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN = (60, 180, 60)
DARK_GREEN = (40, 130, 40)
RED = (200, 60, 60)
DARK_RED = (150, 40, 40)
YELLOW = (240, 220, 100)
BLUE = (70, 130, 200)
BROWN = (140, 90, 50)
ORANGE = (255, 140, 0)
BRIGHT_ORANGE = (255, 180, 50)
CYAN = (80, 220, 220)
PURPLE = (160, 80, 200)
DARK_PURPLE = (110, 40, 160)
ICE = (150, 220, 255)
CRIMSON = (220, 20, 60)
DARK_CRIMSON = (140, 10, 30)
BUNKER_GRAY = (100, 105, 110)
BUNKER_DARK = (60, 65, 70)
BLOOD_RED = (180, 20, 20)
BLOOD_DARK = (120, 10, 10)
KAMIKAZE_COLOR = (30, 30, 35)
KAMIKAZE_DARK = (10, 10, 12)
SHOCKWAVE_COLOR = (255, 200, 100)
MEGATRON_RED = (200, 20, 20)
MEGATRON_DARK = (20, 10, 10)
MEGA_DRONE_GREEN = (60, 220, 80)
MEGA_DRONE_DARK = (20, 80, 40)
PURPLE_LIGHTNING = (200, 80, 255)
LAVA = (255, 90, 20)
LAVA_BRIGHT = (255, 180, 60)
VOLCANO_DARK = (60, 35, 30)
VOLCANO_ROCK = (90, 60, 50)
ASH = (70, 65, 60)
SMOKE_DARK = (40, 38, 36)
MAPS = {
    "grass": {"bg": (80, 130, 60), "bg2": (60, 100, 45), "wall": (140, 90, 50), "wall2": (160, 100, 60)},
    "desert": {"bg": (200, 180, 120), "bg2": (180, 160, 100), "wall": (170, 130, 80), "wall2": (190, 150, 90)},
    "snow": {"bg": (220, 230, 240), "bg2": (200, 210, 220), "wall": (130, 150, 170), "wall2": (150, 170, 190)},
    "dead_forest": {"bg": (45, 60, 40), "bg2": (30, 45, 28), "wall": (70, 50, 35), "wall2": (90, 65, 45)},
    "arena": {"bg": (70, 65, 60), "bg2": (55, 50, 45), "wall": (120, 110, 100), "wall2": (140, 130, 120)},
    "wasteland": {"bg": (55, 40, 35), "bg2": (40, 28, 24), "wall": (80, 55, 45), "wall2": (100, 70, 55)},
}
WEAPON_NAMES = {"normal": "Обычное", "rocket": "Ракета", "laser": "Лазер", "ice": "Лёд", "mine": "Мина", "homing": "Самонавод", "kamikaze": "Камикадзе"}
WEAPON_COLORS = {"normal": WHITE, "rocket": ORANGE, "laser": CYAN, "ice": ICE, "mine": PURPLE, "homing": RED, "kamikaze": KAMIKAZE_COLOR}
