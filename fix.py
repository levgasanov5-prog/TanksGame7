import os

# Создаем папки
os.makedirs('src/utils', exist_ok=True)

# Создаем пустые файлы __init__.py
open('src/__init__.py', 'w').close()
open('src/utils/__init__.py', 'w').close()

# Создаем settings.py
with open('src/settings.py', 'w', encoding='utf-8') as f:
    f.write('''WIDTH, HEIGHT = 900, 600
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
''')

# Создаем assets.py
with open('src/utils/assets.py', 'w', encoding='utf-8') as f:
    f.write('''import os
import pygame
from src.settings import *

try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False

def load_sound(name):
    if not SOUND_AVAILABLE: return None
    path = os.path.join("sounds", name)
    if os.path.exists(path):
        try: return pygame.mixer.Sound(path)
        except Exception: return None
    return None

def load_music(name):
    if not SOUND_AVAILABLE: return None
    path = os.path.join("sounds", name)
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            return path
        except Exception: return None
    return None

sound_shoot = load_sound("shoot.wav")
sound_hit = load_sound("hit.wav")
sound_explosion = load_sound("explosion.wav")
sound_bonus = load_sound("bonus.wav")
sound_freeze = load_sound("freeze.wav")
sound_switch = load_sound("switch.wav")
sound_thunder = load_sound("thunder.wav")
sound_bomb = load_sound("bomb.wav")

MENU_MUSIC = None
BATTLE_MUSIC = None
BOSS_MUSIC = None

def load_all_music():
    global MENU_MUSIC, BATTLE_MUSIC, BOSS_MUSIC
    MENU_MUSIC = load_music("menu.mp3") or load_music("menu.ogg")
    BATTLE_MUSIC = MENU_MUSIC
    BOSS_MUSIC = MENU_MUSIC

def play_music(path, volume=0.4):
    if path:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception: pass

def stop_music():
    if SOUND_AVAILABLE:
        try: pygame.mixer.music.stop()
        except Exception: pass

def play(s):
    if s:
        try: s.play()
        except Exception: pass
''')

print("ВСЁ ГОТОВО! Файлы созданы принудительно!")