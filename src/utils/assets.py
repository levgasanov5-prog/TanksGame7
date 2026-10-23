import os
import pygame
from src.settings import *

# Автоматически находим корень проекта (папку, где лежит main.py и sounds)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False

def load_sound(name):
    if not SOUND_AVAILABLE: return None
    path = os.path.join(BASE_DIR, "sounds", name)
    if os.path.exists(path):
        try: return pygame.mixer.Sound(path)
        except Exception: return None
    return None

def load_music(name):
    if not SOUND_AVAILABLE: return None
    path = os.path.join(BASE_DIR, "sounds", name)
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