import pygame
import sys
import random
import math

# Импортируем наши новые модули
from src.settings import *
from src.utils.assets import *

# --- Инициализация окна ---
pygame.init()

if FULLSCREEN:
    info = pygame.display.Info()
    SCREEN_W, SCREEN_H = info.current_w, info.current_h
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
    SCALE = min(SCREEN_W / WIDTH, SCREEN_H / HEIGHT)
    SCALED_W = int(WIDTH * SCALE)
    SCALED_H = int(HEIGHT * SCALE)
    OFFSET_X = (SCREEN_W - SCALED_W) // 2
    OFFSET_Y = (SCREEN_H - SCALED_H) // 2
    game_surface = pygame.Surface((WIDTH, HEIGHT))
else:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game_surface = screen
    SCALE = 1.0
    SCALED_W = WIDTH
    SCALED_H = HEIGHT
    OFFSET_X = 0
    OFFSET_Y = 0

pygame.display.set_caption("Танки — Битва с боссами")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22, bold=True)
small_font = pygame.font.SysFont("Arial", 16, bold=True)
mid_font = pygame.font.SysFont("Arial", 32, bold=True)
big_font = pygame.font.SysFont("Arial", 64, bold=True)

shake_amount = 0
scorch_marks = []
vignette_surface = None
wasteland_volcanoes = []


# --- Вспомогательные функции отрисовки (остались тут, т.к. завязаны на глобальные переменные) ---

def create_vignette():
    global vignette_surface
    vignette_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(60):
        alpha = int(180 * (i / 60))
        pygame.draw.rect(vignette_surface, (0, 0, 0, alpha),
                         (i, i, WIDTH - i * 2, HEIGHT - i * 2),
                         max(1, 3))
    for radius in range(0, 500, 5):
        alpha = max(0, int(150 * (radius / 500)))
        pygame.draw.circle(vignette_surface, (0, 0, 0, alpha),
                           (WIDTH // 2, HEIGHT // 2), 500 - radius, 5)


def shake_screen(amount):
    global shake_amount
    shake_amount = max(shake_amount, amount)


def add_scorch(x, y, radius=40):
    scorch_marks.append([x, y, radius, 600])


def present():
    if FULLSCREEN:
        scaled = pygame.transform.scale(game_surface, (SCALED_W, SCALED_H))
        screen.fill(BLACK)
        screen.blit(scaled, (OFFSET_X, OFFSET_Y))
    pygame.display.flip()


# --- Классы игровых объектов ---

class Particle:
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5) * speed_mult
        self.vy = random.uniform(-5, 5) * speed_mult
        self.life = random.randint(20, 50)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha // 4),
                               (self.size * 3 // 2, self.size * 3 // 2), self.size * 3 // 2)
            pygame.draw.circle(surf, (*self.color, alpha),
                               (self.size * 3 // 2, self.size * 3 // 2), self.size)
            surface.blit(surf, (self.x - self.size * 3 // 2, self.y - self.size * 3 // 2))


class Shockwave:
    def __init__(self, x, y, max_radius=200, color=None):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = max_radius
        self.life = 25
        self.initial_life = 25
        self.color = color if color else SHOCKWAVE_COLOR

    def update(self):
        self.radius += (self.max_radius - self.radius) * 0.15
        self.life -= 1

    def alive(self):
        return self.life > 0

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.initial_life))
        width = max(1, int(8 * (self.life / self.initial_life)))
        surf = pygame.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha),
                           (self.radius + 10, self.radius + 10),
                           int(self.radius), width)
        surface.blit(surf, (self.x - self.radius - 10, self.y - self.radius - 10))


class BloodSplat:
    def __init__(self, x, y, color=BLOOD_RED):
        self.x = x
        self.y = y
        self.color = color
        self.life = 40
        self.particles = []
        for _ in range(15):
            p = Particle(x, y, color, speed_mult=1.5)
            p.size = random.randint(3, 6)
            self.particles.append(p)

    def update(self):
        for p in self.particles:
            p.update()
        self.life -= 1

    def alive(self):
        return self.life > 0

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)


class SmokeEmitter:
    def __init__(self, x, y, color=(40, 40, 40)):
        self.x = x
        self.y = y
        self.life = 30
        self.vy = -1.5
        self.vx = random.uniform(-0.5, 0.5)
        self.size = random.randint(6, 12)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size += 0.3

    def alive(self):
        return self.life > 0

    def draw(self, surface):
        if self.life > 0:
            alpha = int(180 * (self.life / 30))
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (self.size, self.size), int(self.size))
            surface.blit(surf, (self.x - self.size, self.y - self.size))


class Explosion:
    def __init__(self, x, y, colors=None, count=30, speed_mult=1.0, shake=True):
        if colors is None:
            colors = [ORANGE, YELLOW, RED]
        self.particles = [Particle(x, y, random.choice(colors), speed_mult) for _ in range(count)]
        self.life = 40
        if shake:
            shake_screen(6)
            add_scorch(x, y, radius=40)

    def update(self):
        for p in self.particles:
            p.update()
        self.life -= 1

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def alive(self):
        return self.life > 0


class Thunder:
    def __init__(self, target_x, target_y, owner, damage=1):
        self.target_x = target_x
        self.target_y = target_y
        self.owner = owner
        self.damage = damage
        self.life = 30
        self.initial_life = 30
        self.bolt_points = []
        self._damaged = False
        self.generate_bolt()

    def generate_bolt(self):
        x = self.target_x
        y = 0
        points = [(x, y)]
        while y < self.target_y:
            y += random.randint(15, 30)
            x += random.randint(-20, 20)
            points.append((x, y))
        points.append((self.target_x, self.target_y))
        self.bolt_points = points

    def update(self):
        self.life -= 1

    def alive(self):
        return self.life > 0

    def _draw_thick_line(self, surface, color, width):
        if len(self.bolt_points) < 2:
            return
        min_x = min(p[0] for p in self.bolt_points) - width
        max_x = max(p[0] for p in self.bolt_points) + width
        min_y = min(p[1] for p in self.bolt_points) - width
        max_y = max(p[1] for p in self.bolt_points) + width
        min_x = max(0, int(min_x))
        min_y = max(0, int(min_y))
        max_x = min(WIDTH, int(max_x))
        max_y = min(HEIGHT, int(max_y))
        w = max_x - min_x
        h = max_y - min_y
        if w <= 0 or h <= 0:
            return
        temp = pygame.Surface((w, h), pygame.SRCALPHA)
        offset_points = [(p[0] - min_x, p[1] - min_y) for p in self.bolt_points]
        for i in range(len(offset_points) - 1):
            pygame.draw.line(temp, color, offset_points[i], offset_points[i + 1], width)
        surface.blit(temp, (min_x, min_y))

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.initial_life))
        if len(self.bolt_points) > 1:
            mid_color = (PURPLE[0], PURPLE[1], PURPLE[2], alpha // 2)
            self._draw_thick_line(surface, mid_color, 6)
            core_color = (255, 255, 255, alpha)
            self._draw_thick_line(surface, core_color, 3)
        if self.life > 20:
            r = (self.initial_life - self.life) * 3
            if r > 0:
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (PURPLE[0], PURPLE[1], PURPLE[2], alpha // 2), (r, r), r)
                surface.blit(s, (self.target_x - r, self.target_y - r))


class PurpleLightning:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 40
        self.initial_life = 40
        self.bolt_points = []
        self._damaged = False
        self.generate_bolts()

    def generate_bolts(self):
        for _ in range(5):
            angle = random.uniform(0, math.pi * 2)
            points = [(self.x, self.y)]
            px, py = self.x, self.y
            for _ in range(random.randint(3, 6)):
                px += math.cos(angle) * random.randint(20, 40) + random.randint(-15, 15)
                py += math.sin(angle) * random.randint(20, 40) + random.randint(-15, 15)
                points.append((px, py))
            self.bolt_points.append(points)

    def update(self):
        self.life -= 1

    def alive(self):
        return self.life > 0

    def rect(self):
        r = 60
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.initial_life))
        for points in self.bolt_points:
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(glow_surf,
                                 (PURPLE_LIGHTNING[0], PURPLE_LIGHTNING[1], PURPLE_LIGHTNING[2], alpha // 3),
                                 p1, p2, 8)
                surface.blit(glow_surf, (0, 0))
                pygame.draw.line(surface, PURPLE_LIGHTNING, p1, p2, 3)
                pygame.draw.line(surface, WHITE, p1, p2, 1)
        if self.life > 30:
            r = (40 - self.life) * 4
            if r > 0:
                s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(s,
                                   (PURPLE_LIGHTNING[0], PURPLE_LIGHTNING[1], PURPLE_LIGHTNING[2], alpha // 2),
                                   (r, r), r)
                surface.blit(s, (self.x - r, self.y - r))


class Bomb:
    def __init__(self, x, y, owner, radius=90, fuse=60, damage=2):
        self.x = x
        self.y = y
        self.owner = owner
        self.radius = radius
        self.damage = damage
        self.life = fuse
        self.exploded = False
        self.explosion_life = 30
        self._damaged = False
        self.drop_offset = -50

    def update(self):
        if not self.exploded:
            self.life -= 1
            self.drop_offset += 1
            if self.life <= 0:
                self.exploded = True
                shake_screen(5)
                add_scorch(self.x, self.y, radius=self.radius - 20)
        else:
            self.explosion_life -= 1

    def alive(self):
        if not self.exploded:
            return self.life > 0
        return self.explosion_life > 0

    def rect(self):
        r = self.radius if self.exploded else 20
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

    def draw(self, surface):
        if not self.exploded:
            draw_x = self.x
            draw_y = self.y + self.drop_offset
            shadow = pygame.Surface((30, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, 30, 12))
            surface.blit(shadow, (self.x - 15, self.y - 6))
            pygame.draw.circle(surface, BLACK, (draw_x, draw_y), 14)
            pygame.draw.circle(surface, DARK_GRAY, (draw_x, draw_y), 14, 2)
            if (self.life // 5) % 2 == 0:
                pygame.draw.circle(surface, CRIMSON, (draw_x, draw_y - 12), 4)
            else:
                pygame.draw.circle(surface, RED, (draw_x, draw_y - 12), 4)
        else:
            t = self.explosion_life / 30
            r = int(self.radius * (1 - t * 0.3))
            aura_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            alpha = int(200 * t)
            pygame.draw.circle(aura_surf, (255, 140, 0, alpha // 3), (r, r), r)
            pygame.draw.circle(aura_surf, (255, 180, 50, alpha // 2), (r, r), int(r * 0.7))
            pygame.draw.circle(aura_surf, (255, 220, 100, alpha), (r, r), int(r * 0.4))
            surface.blit(aura_surf, (self.x - r, self.y - r))


class Kamikaze:
    def __init__(self, x, y, owner, target):
        self.x = x
        self.y = y
        self.owner = owner
        self.target = target
        self.damage = 10
        self.radius = 18
        self.alive = True
        self.angle = 0
        self.trail = []
        self.speed = 6
        self.life = 300
        self.is_red_laser = False

    def update(self, walls):
        if self.target and self.target.hp > 0:
            tx = self.target.x + self.target.size // 2
            ty = self.target.y + self.target.size // 2
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.angle = math.atan2(dy, dx)
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        else:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:
            self.trail.pop(0)
        self.life -= 1
        if self.life <= 0:
            self.alive = False
        if self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
            self.alive = False

    def rect(self):
        return pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(150 * (i / max(1, len(self.trail))))
            r = max(2, self.radius - 8)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (60, 60, 60, alpha), (r, r), r)
            surface.blit(surf, (int(tx) - r, int(ty) - r))
        cx, cy = int(self.x), int(self.y)
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        nose = (cx + cos_a * 20, cy + sin_a * 20)
        tail_left = (cx - cos_a * 15 - sin_a * 12, cy - sin_a * 15 + cos_a * 12)
        tail_right = (cx - cos_a * 15 + sin_a * 12, cy - sin_a * 15 - cos_a * 12)
        pygame.draw.polygon(surface, KAMIKAZE_COLOR, [nose, tail_left, tail_right])
        pygame.draw.polygon(surface, KAMIKAZE_DARK, [nose, tail_left, tail_right], 2)
        wing_left = (cx - sin_a * 18, cy + cos_a * 18)
        wing_right = (cx + sin_a * 18, cy - cos_a * 18)
        pygame.draw.line(surface, KAMIKAZE_COLOR, (cx, cy), wing_left, 8)
        pygame.draw.line(surface, KAMIKAZE_COLOR, (cx, cy), wing_right, 8)
        pygame.draw.circle(surface, CRIMSON, (cx, cy), 4)
        pygame.draw.circle(surface, ORANGE, (int(cx - cos_a * 12), int(cy - sin_a * 12)), 3)


class Axe:
    def __init__(self, x, y, target_x, target_y, owner):
        self.owner = owner
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.flight_time = 70
        self.t = 0.0
        self.rot = 0.0
        self.radius = 22
        self.alive = True
        self.landed = False
        self.land_effect_life = 30
        self.mini_bombs_spawned = False
        self.mini_bombs = []
        self.damage = 3
        self.area = 110
        self._damaged_targets = set()

    def update(self, player=None, drones=None, walls=None):
        if not self.landed:
            self.t += 1.0 / self.flight_time
            if self.t >= 1.0:
                self.t = 1.0
                self.landed = True
                shake_screen(18)
                add_scorch(self.target_x, self.target_y, radius=self.area)
                play(sound_explosion)
            self.x = self.start_x + (self.target_x - self.start_x) * self.t
            base_y = self.start_y + (self.target_y - self.start_y) * self.t
            arc = math.sin(self.t * math.pi) * 220
            self.y = base_y - arc
            self.rot += 0.35
        else:
            self.land_effect_life -= 1
            if self.land_effect_life <= 0:
                self.alive = False

    def rect(self):
        return pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius,
                           self.radius * 2, self.radius * 2)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        if not self.landed:
            shadow_t = min(1.0, self.t)
            sx = self.start_x + (self.target_x - self.start_x) * shadow_t
            sy = self.start_y + (self.target_y - self.start_y) * shadow_t
            sh = pygame.Surface((40, 16), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0, 0, 0, 110), (0, 0, 40, 16))
            surface.blit(sh, (sx - 20, sy - 8))
            axe_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.line(axe_surf, (90, 60, 40), (40, 60), (40, 15), 7)
            pygame.draw.line(axe_surf, (50, 30, 20), (40, 60), (40, 15), 3)
            blade = [(40, 15), (62, 22), (62, 40), (40, 34)]
            pygame.draw.polygon(axe_surf, (200, 200, 210), blade)
            pygame.draw.polygon(axe_surf, (120, 120, 130), blade, 2)
            blade2 = [(40, 15), (18, 22), (18, 40), (40, 34)]
            pygame.draw.polygon(axe_surf, (200, 200, 210), blade2)
            pygame.draw.polygon(axe_surf, (120, 120, 130), blade2, 2)
            pygame.draw.circle(axe_surf, MEGATRON_RED, (40, 15), 5)
            rotated = pygame.transform.rotate(axe_surf, math.degrees(self.rot) % 360)
            rect = rotated.get_rect(center=(cx, cy))
            surface.blit(rotated, rect)
        else:
            t = max(0.0, self.land_effect_life / 30.0)
            r = int(self.area * (0.4 + (1 - t) * 0.6))
            aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            alpha = int(220 * t)
            pygame.draw.circle(aura, (180, 20, 20, alpha // 4), (r, r), r)
            pygame.draw.circle(aura, (230, 30, 30, alpha // 2), (r, r), int(r * 0.7))
            pygame.draw.circle(aura, (255, 90, 60, alpha), (r, r), int(r * 0.4))
            pygame.draw.circle(aura, (255, 200, 180, alpha), (r, r), int(r * 0.18))
            surface.blit(aura, (self.target_x - r, self.target_y - r))
            axe_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.line(axe_surf, (90, 60, 40), (30, 50), (30, 12), 6)
            pygame.draw.polygon(axe_surf, (200, 200, 210), [(30, 12), (48, 18), (48, 34), (30, 30)])
            pygame.draw.polygon(axe_surf, (120, 120, 130), [(30, 12), (48, 18), (48, 34), (30, 30)], 2)
            rect = axe_surf.get_rect(center=(self.target_x, self.target_y))
            surface.blit(axe_surf, rect)


class MiniBomb:
    def __init__(self, x, y, vx, vy, owner, delay=45):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.owner = owner
        self.delay = delay
        self.alive = True
        self.exploded = False
        self.radius = 10
        self.blast_radius = 55
        self.damage = 1
        self._damaged_targets = set()
        self.explosion_life = 0
        self.angle = random.uniform(0, math.pi * 2)

    def update(self, walls):
        if not self.exploded:
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.94
            self.vy *= 0.94
            self.vy += 0.06
            self.angle += 0.25
            self.delay -= 1
            if self.delay <= 0:
                self.exploded = True
                self.explosion_life = 25
                play(sound_explosion)
                shake_screen(4)
                add_scorch(self.x, self.y, radius=self.blast_radius - 10)
            if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
                self.alive = False
        else:
            self.explosion_life -= 1
            if self.explosion_life <= 0:
                self.alive = False

    def rect(self):
        r = self.blast_radius if self.exploded else self.radius
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def draw(self, surface):
        if not self.exploded:
            glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 140, 0, 70), (self.radius * 2, self.radius * 2), self.radius * 2)
            surface.blit(glow, (int(self.x) - self.radius * 2, int(self.y) - self.radius * 2))
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.radius, 2)
            if (self.delay // 4) % 2 == 0:
                pygame.draw.circle(surface, BRIGHT_ORANGE, (int(self.x), int(self.y - self.radius - 3)), 3)
        else:
            t = max(0.0, self.explosion_life / 25.0)
            r = int(self.blast_radius * (1.1 - t * 0.3))
            aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            alpha = int(230 * t)
            pygame.draw.circle(aura, (255, 100, 0, alpha // 3), (r, r), r)
            pygame.draw.circle(aura, (255, 160, 30, alpha // 2), (r, r), int(r * 0.7))
            pygame.draw.circle(aura, (255, 220, 120, alpha), (r, r), int(r * 0.4))
            surface.blit(aura, (int(self.x) - r, int(self.y) - r))


class Bullet:
    def __init__(self, x, y, vx, vy, kind, owner, damage_override=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.kind = kind
        self.owner = owner
        self.alive = True
        self.trail = []
        self.spawn_ignore = 5
        self.is_red_laser = False

        if kind == "rocket":
            self.radius = 8
            self.damage = 2
            self.color = ORANGE
        elif kind == "big_rocket":
            self.radius = 14
            self.damage = 3
            self.color = PURPLE
        elif kind == "laser":
            self.radius = 4
            self.damage = 1
            self.color = CYAN
        elif kind == "ice":
            self.radius = 6
            self.damage = 1
            self.color = ICE
            self.freeze = 120
        elif kind == "homing":
            self.radius = 6
            self.damage = 2
            self.color = RED
        else:
            self.radius = 5
            self.damage = 1
            self.color = WHITE

        if damage_override:
            self.damage = damage_override

    def update(self, walls, enemies):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 12:
            self.trail.pop(0)
        if self.kind == "homing":
            closest = None
            closest_dist = 9999
            for e in enemies:
                if e != self.owner and e.hp > 0:
                    d = math.hypot(e.x - self.x, e.y - self.y)
                    if d < closest_dist:
                        closest_dist = d
                        closest = e
            if closest:
                dx = closest.x + closest.size // 2 - self.x
                dy = closest.y + closest.size // 2 - self.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    speed = math.hypot(self.vx, self.vy)
                    turn = 0.15
                    self.vx += (dx / dist) * speed * turn
                    self.vy += (dy / dist) * speed * turn
                    current = math.hypot(self.vx, self.vy)
                    if current > 0:
                        self.vx = self.vx / current * speed
                        self.vy = self.vy / current * speed
        self.x += self.vx
        self.y += self.vy
        if self.spawn_ignore > 0:
            self.spawn_ignore -= 1
            return
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False
            return
        rect = pygame.Rect(int(self.x) - 3, int(self.y) - 3, 6, 6)
        if any(rect.colliderect(w) for w in walls):
            self.alive = False
            for _ in range(5):
                Particle(self.x, self.y, YELLOW, speed_mult=0.6)

    def rect(self):
        r = max(5, self.radius)
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(200 * (i / max(1, len(self.trail))))
            r = max(1, self.radius - 3)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (r, r), r)
            surface.blit(surf, (int(tx) - r, int(ty) - r))
        glow_r = self.radius + 4
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 60), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (int(self.x) - glow_r, int(self.y) - glow_r))
        if self.kind == "rocket":
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius - 3)
        elif self.kind == "big_rocket":
            pygame.draw.circle(surface, DARK_PURPLE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, PURPLE, (int(self.x), int(self.y)), self.radius - 4)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 8)
        elif self.kind == "laser":
            pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 2)
        elif self.kind == "ice":
            pygame.draw.circle(surface, ICE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 2)
            for angle in range(0, 360, 60):
                ex = self.x + math.cos(math.radians(angle)) * self.radius
                ey = self.y + math.sin(math.radians(angle)) * self.radius
                pygame.draw.line(surface, WHITE, (int(self.x), int(self.y)), (int(ex), int(ey)), 1)
        elif self.kind == "homing":
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius - 2)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 2)


class Mine:
    def __init__(self, x, y, owner):
        self.x = x
        self.y = y
        self.owner = owner
        self.size = 20
        self.alive = True
        self.arm_time = 60
        self.life = 600
        self.pulse = 0
        self.is_red_laser = False

    def rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    def update(self):
        if self.arm_time > 0:
            self.arm_time -= 1
        self.life -= 1
        self.pulse += 0.2
        if self.life <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        color = PURPLE if self.arm_time == 0 else GRAY
        offset = math.sin(self.pulse) * 2
        pygame.draw.circle(surface, color, (int(self.x), int(self.y + offset)), self.size // 2)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y + offset)), self.size // 2, 2)
        for angle in range(0, 360, 45):
            ex = self.x + math.cos(math.radians(angle)) * (self.size // 2 + 3)
            ey = self.y + offset + math.sin(math.radians(angle)) * (self.size // 2 + 3)
            pygame.draw.line(surface, BLACK, (int(self.x), int(self.y + offset)), (int(ex), int(ey)), 2)


class Bonus:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.size = 24
        self.life = 600
        self.pulse = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self):
        self.life -= 1
        self.pulse += 0.15

    def draw(self, surface):
        if self.life <= 0:
            return
        offset = math.sin(self.pulse) * 3
        cx = self.x + self.size // 2
        cy = self.y + self.size // 2 + offset
        colors = {"health": (220, 60, 60), "speed": (60, 130, 220), "double": (240, 140, 0), "rapid": (240, 220, 100)}
        icons = {"health": "+", "speed": ">>", "double": "x2", "rapid": "~"}
        color = colors[self.kind]
        glow_r = self.size // 2 + 8
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 60), (glow_r, glow_r), glow_r)
        surface.blit(glow_surf, (int(cx) - glow_r, int(cy) - glow_r))
        pygame.draw.circle(surface, color, (int(cx), int(cy)), self.size // 2 + 3)
        pygame.draw.circle(surface, WHITE, (int(cx), int(cy)), self.size // 2 + 3, 2)
        text = font.render(icons[self.kind], True, WHITE)
        surface.blit(text, (cx - text.get_width() // 2, cy - text.get_height() // 2))


class Bunker:
    def __init__(self, x, y, w=140, h=110):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def inner_rect(self):
        return pygame.Rect(self.x + 18, self.y + 18, self.w - 36, self.h - 36)

    def is_player_inside(self, player):
        return self.inner_rect().contains(player.rect())

    def get_walls(self):
        return [
            pygame.Rect(self.x, self.y, self.w, 15),
            pygame.Rect(self.x, self.y, 15, self.h),
            pygame.Rect(self.x + self.w - 15, self.y, 15, self.h),
            pygame.Rect(self.x, self.y + self.h - 15, self.w // 2 - 30, 15),
            pygame.Rect(self.x + self.w // 2 + 30, self.y + self.h - 15, self.w // 2 - 30, 15),
        ]

    def blocks_bullet(self, bullet_rect):
        return any(bullet_rect.colliderect(w) for w in self.get_walls())

    def draw(self, surface):
        shadow = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), (0, 0, self.w, self.h), border_radius=8)
        surface.blit(shadow, (self.x + 5, self.y + 5))
        pygame.draw.rect(surface, BUNKER_DARK, self.inner_rect(), border_radius=4)
        for wall in self.get_walls():
            pygame.draw.rect(surface, BUNKER_GRAY, wall, border_radius=6)
            pygame.draw.rect(surface, BLACK, wall, 2, border_radius=6)
        cx = self.x + self.w // 2
        cy = self.y + 38
        shield = [(cx, cy - 14), (cx + 14, cy - 5), (cx + 14, cy + 8), (cx, cy + 16), (cx - 14, cy + 8), (cx - 14, cy - 5)]
        pygame.draw.polygon(surface, (60, 200, 100), shield)
        pygame.draw.polygon(surface, WHITE, shield, 2)
        small = pygame.font.SysFont("Arial", 12, bold=True)
        text = small.render("УКРЫТИЕ", True, WHITE)
        surface.blit(text, (cx - text.get_width() // 2, self.y + self.h - 35))


class Tank:
    def __init__(self, x, y, color, dark_color, controls, name):
        self.x = x
        self.y = y
        self.color = color
        self.dark_color = dark_color
        self.controls = controls
        self.name = name
        self.direction = "up"
        self.speed = 3
        self.cooldown = 0
        self.hp = 10
        self.max_hp = 10
        self.size = TANK_SIZE
        self.speed_boost = 0
        self.double_shot = 0
        self.rapid_fire = 0
        self.freeze = 0
        self.weapon = "normal"
        self.hits = 0
        self.shots = 0
        self.recoil = 0
        self.smoke_timer = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def move(self, keys, walls, tanks):
        if self.freeze > 0:
            return
        dx, dy = 0, 0
        speed = self.speed + (2 if self.speed_boost > 0 else 0)
        if keys[self.controls["up"]]:
            dy = -speed
            self.direction = "up"
        elif keys[self.controls["down"]]:
            dy = speed
            self.direction = "down"
        elif keys[self.controls["left"]]:
            dx = -speed
            self.direction = "left"
        elif keys[self.controls["right"]]:
            dx = speed
            self.direction = "right"
        new_rect = self.rect().move(dx, 0)
        if (not any(new_rect.colliderect(w) for w in walls)
                and not any(new_rect.colliderect(t.rect()) for t in tanks if t != self)
                and 0 <= new_rect.x <= WIDTH - self.size):
            self.x += dx
        new_rect = self.rect().move(0, dy)
        if (not any(new_rect.colliderect(w) for w in walls)
                and not any(new_rect.colliderect(t.rect()) for t in tanks if t != self)
                and 0 <= new_rect.y <= HEIGHT - self.size):
            self.y += dy

    def shoot(self, target=None):
        if self.cooldown > 0 or self.freeze > 0:
            return []
        cooldown_map = {"normal": 25, "rocket": 60, "laser": 12, "ice": 35, "mine": 40, "homing": 50, "kamikaze": 180}
        base_cd = cooldown_map.get(self.weapon, 25)
        if self.rapid_fire > 0:
            self.cooldown = max(2, base_cd // 5)
        else:
            self.cooldown = base_cd
        self.shots += 1
        self.recoil = 6
        cx = self.x + self.size // 2
        cy = self.y + self.size // 2
        if self.weapon == "kamikaze":
            play(sound_switch)
            return [Kamikaze(cx, cy, self, target)]
        offset = self.size // 2 + 10
        speed_map = {"normal": 9, "rocket": 5, "laser": 14, "ice": 7, "mine": 0, "homing": 6}
        speed = speed_map.get(self.weapon, 9)
        if self.weapon == "mine":
            play(sound_switch)
            return [Mine(cx, cy, self)]
        bullets = []
        if self.direction == "up":
            bullets.append(Bullet(cx, cy - offset, 0, -speed, self.weapon, self))
        elif self.direction == "down":
            bullets.append(Bullet(cx, cy + offset, 0, speed, self.weapon, self))
        elif self.direction == "left":
            bullets.append(Bullet(cx - offset, cy, -speed, 0, self.weapon, self))
        elif self.direction == "right":
            bullets.append(Bullet(cx + offset, cy, speed, 0, self.weapon, self))
        if self.double_shot > 0 and bullets:
            b = bullets[0]
            if b.vx != 0:
                bullets.append(Bullet(cx - offset, cy + 12, b.vx, 0, self.weapon, self))
                bullets.append(Bullet(cx - offset, cy - 12, b.vx, 0, self.weapon, self))
            else:
                bullets.append(Bullet(cx + 12, cy - offset, 0, b.vy, self.weapon, self))
                bullets.append(Bullet(cx - 12, cy - offset, 0, b.vy, self.weapon, self))
        play(sound_shoot)
        return bullets

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.speed_boost > 0:
            self.speed_boost -= 1
        if self.double_shot > 0:
            self.double_shot -= 1
        if self.rapid_fire > 0:
            self.rapid_fire -= 1
        if self.freeze > 0:
            self.freeze -= 1
        if self.recoil > 0:
            self.recoil -= 1
        self.smoke_timer += 1

    def draw(self, surface):
        ox, oy = 0, 0
        if self.recoil > 0:
            if self.direction == "up": oy = self.recoil
            elif self.direction == "down": oy = -self.recoil
            elif self.direction == "left": ox = self.recoil
            elif self.direction == "right": ox = -self.recoil
        shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80), (0, 0, self.size, self.size), border_radius=6)
        surface.blit(shadow, (self.x + 4 + ox, self.y + 4 + oy))
        pygame.draw.rect(surface, DARK_GRAY, (self.x - 3 + ox, self.y + oy, 6, self.size), border_radius=2)
        pygame.draw.rect(surface, DARK_GRAY, (self.x + self.size - 3 + ox, self.y + oy, 6, self.size), border_radius=2)
        for i in range(0, self.size, 8):
            pygame.draw.line(surface, BLACK, (self.x - 3 + ox, self.y + i + oy), (self.x + 3 + ox, self.y + i + oy), 1)
            pygame.draw.line(surface, BLACK, (self.x + self.size - 3 + ox, self.y + i + oy),
                             (self.x + self.size + 3 + ox, self.y + i + oy), 1)
        body = pygame.Rect(self.x + ox, self.y + oy, self.size, self.size)
        pygame.draw.rect(surface, self.color, body, border_radius=6)
        pygame.draw.rect(surface, self.dark_color, body, 3, border_radius=6)
        for cx_off, cy_off in [(4, 4), (self.size - 4, 4), (4, self.size - 4), (self.size - 4, self.size - 4)]:
            pygame.draw.circle(surface, self.dark_color, (self.x + cx_off + ox, self.y + cy_off + oy), 2)
        if self.freeze > 0:
            pygame.draw.rect(surface, ICE, body.inflate(6, 6), 3, border_radius=8)
        cx, cy = self.x + self.size // 2 + ox, self.y + self.size // 2 + oy
        if self.direction == "up":
            pygame.draw.rect(surface, self.dark_color, (cx - 4, self.y - 14 + oy, 8, 22), border_radius=2)
        elif self.direction == "down":
            pygame.draw.rect(surface, self.dark_color, (cx - 4, self.y + self.size - 8 + oy, 8, 22), border_radius=2)
        elif self.direction == "left":
            pygame.draw.rect(surface, self.dark_color, (self.x - 14 + ox, cy - 4, 22, 8), border_radius=2)
        elif self.direction == "right":
            pygame.draw.rect(surface, self.dark_color, (self.x + self.size - 8 + ox, cy - 4, 22, 8), border_radius=2)
        pygame.draw.circle(surface, WHITE, (cx, cy), 11)
        pygame.draw.circle(surface, self.dark_color, (cx, cy), 11, 2)
        pygame.draw.circle(surface, self.color, (cx, cy), 6)
        if self.cooldown > 0 and self.cooldown > 20:
            flash_alpha = min(255, (self.cooldown - 20) * 50)
            if self.direction == "up":
                fx, fy = cx, self.y + oy - 8
            elif self.direction == "down":
                fx, fy = cx, self.y + self.size + oy + 8
            elif self.direction == "left":
                fx, fy = self.x + ox - 8, cy
            else:
                fx, fy = self.x + self.size + ox + 8, cy
            flash_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 220, 100, flash_alpha), (15, 15), 12)
            surface.blit(flash_surf, (fx - 15, fy - 15))
        if self.double_shot > 0:
            pygame.draw.circle(surface, ORANGE, (self.x + self.size - 5 + ox, self.y + 5 + oy), 5)
        if self.speed_boost > 0:
            pygame.draw.circle(surface, BLUE, (self.x + 5 + ox, self.y + 5 + oy), 5)
        if self.rapid_fire > 0:
            pygame.draw.circle(surface, YELLOW, (self.x + self.size // 2 + ox, self.y + self.size - 5 + oy), 5)
        wcolor = WEAPON_COLORS.get(self.weapon, WHITE)
        pygame.draw.circle(surface, wcolor, (self.x + self.size // 2 + ox, self.y - 5 + oy), 4)
        if self.cooldown > 0:
            total = {"normal": 25, "rocket": 60, "laser": 12, "ice": 35, "mine": 40, "homing": 50, "kamikaze": 180}.get(self.weapon, 25)
            ratio = 1 - (self.cooldown / total)
            pygame.draw.rect(surface, (60, 60, 60), (self.x + ox, self.y + self.size + 4 + oy, self.size, 4))
            pygame.draw.rect(surface, YELLOW, (self.x + ox, self.y + self.size + 4 + oy, int(self.size * ratio), 4))


class BerserkBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 90
        self.hp = 25
        self.max_hp = 25
        self.speed = 2.2
        self.direction = "down"
        self.cooldown_rockets = 0
        self.cooldown_thunder = 0
        self.cooldown_melee = 0
        self.aura_phase = 0
        self.hits = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def center(self):
        return (self.x + self.size // 2, self.y + self.size // 2)

    def move(self, target, walls):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            mx = (dx / dist) * self.speed
            my = (dy / dist) * self.speed
            nr = self.rect().move(mx, 0)
            if not any(nr.colliderect(w) for w in walls) and 0 <= nr.x <= WIDTH - self.size:
                self.x += mx
            nr = self.rect().move(0, my)
            if not any(nr.colliderect(w) for w in walls) and 0 <= nr.y <= HEIGHT - self.size:
                self.y += my
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

    def think(self, player, walls, bullets):
        result = {"bullets": [], "thunders": []}
        if self.cooldown_rockets > 0: self.cooldown_rockets -= 1
        if self.cooldown_thunder > 0: self.cooldown_thunder -= 1
        if self.cooldown_melee > 0: self.cooldown_melee -= 1
        if self.cooldown_rockets == 0:
            cx, cy = self.center()
            dir_map = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
            dx, dy = dir_map[self.direction]
            speed = 5
            offset = self.size // 2 + 10
            base_angle = math.atan2(dy, dx)
            for a in [-15, 0, 15]:
                ang = base_angle + math.radians(a)
                vx = math.cos(ang) * speed
                vy = math.sin(ang) * speed
                result["bullets"].append(Bullet(cx + dx * offset, cy + dy * offset, vx, vy, "big_rocket", self, damage_override=1))
            self.cooldown_rockets = 90
            play(sound_shoot)
        if self.cooldown_thunder == 0:
            tx = player.x + player.size // 2 + random.randint(-60, 60)
            ty = player.y + player.size // 2 + random.randint(-60, 60)
            tx = max(20, min(WIDTH - 20, tx))
            ty = max(20, min(HEIGHT - 20, ty))
            result["thunders"].append(Thunder(tx, ty, self, damage=1))
            self.cooldown_thunder = 180
            play(sound_thunder)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < 100 and self.cooldown_melee == 0:
            player.hp -= 1
            self.cooldown_melee = 60
        return result

    def draw(self, surface):
        cx, cy = self.center()
        self.aura_phase += 0.05
        aura_r = self.size // 2 + 20 + int(math.sin(self.aura_phase) * 8)
        aura_surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (160, 80, 200, 60), (aura_r, aura_r), aura_r)
        pygame.draw.circle(aura_surf, (200, 120, 240, 80), (aura_r, aura_r), aura_r - 10)
        surface.blit(aura_surf, (cx - aura_r, cy - aura_r))
        shadow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 120), (0, 0, self.size, self.size), border_radius=12)
        surface.blit(shadow, (self.x + 6, self.y + 6))
        pygame.draw.rect(surface, (20, 10, 30), (self.x - 6, self.y, 12, self.size), border_radius=4)
        pygame.draw.rect(surface, (20, 10, 30), (self.x + self.size - 6, self.y, 12, self.size), border_radius=4)
        for i in range(0, self.size, 12):
            pygame.draw.line(surface, BLACK, (self.x - 6, self.y + i), (self.x + 6, self.y + i), 2)
            pygame.draw.line(surface, BLACK, (self.x + self.size - 6, self.y + i), (self.x + self.size + 6, self.y + i), 2)
        body = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(surface, DARK_PURPLE, body, border_radius=12)
        pygame.draw.rect(surface, (60, 20, 90), body, 4, border_radius=12)
        inner = body.inflate(-20, -20)
        pygame.draw.rect(surface, (80, 30, 120), inner, border_radius=8)
        pygame.draw.rect(surface, BLACK, inner, 2, border_radius=8)
        if self.direction == "up":
            pygame.draw.rect(surface, (60, 20, 90), (cx - 8, self.y - 25, 16, 35), border_radius=3)
        elif self.direction == "down":
            pygame.draw.rect(surface, (60, 20, 90), (cx - 8, self.y + self.size - 10, 16, 35), border_radius=3)
        elif self.direction == "left":
            pygame.draw.rect(surface, (60, 20, 90), (self.x - 25, cy - 8, 35, 16), border_radius=3)
        elif self.direction == "right":
            pygame.draw.rect(surface, (60, 20, 90), (self.x + self.size - 10, cy - 8, 35, 16), border_radius=3)
        pygame.draw.circle(surface, WHITE, (cx, cy), 22)
        pygame.draw.circle(surface, (60, 20, 90), (cx, cy), 22, 3)
        pygame.draw.circle(surface, PURPLE, (cx, cy), 14)
        pygame.draw.circle(surface, WHITE, (cx - 5, cy - 2), 3)
        pygame.draw.circle(surface, WHITE, (cx + 5, cy - 2), 3)
        pygame.draw.circle(surface, BLACK, (cx - 5, cy - 2), 1)
        pygame.draw.circle(surface, BLACK, (cx + 5, cy - 2), 1)
        pygame.draw.line(surface, BLACK, (cx - 6, cy + 6), (cx + 6, cy + 6), 2)
        bar_w = self.size
        bar_y = self.y - 18
        pygame.draw.rect(surface, (0, 0, 0), (self.x - 2, bar_y - 2, bar_w + 4, 12), border_radius=4)
        pygame.draw.rect(surface, (60, 60, 60), (self.x, bar_y, bar_w, 8), border_radius=3)
        fill = int(bar_w * (max(0, self.hp) / self.max_hp))
        pygame.draw.rect(surface, PURPLE, (self.x, bar_y, fill, 8), border_radius=3)


class DroneBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 80
        self.hp = 25
        self.max_hp = 25
        self.speed = 3.5
        self.hover_phase = 0
        self.aura_phase = 0
        self.cooldown_bombs = 120
        self.cooldown_eye = 60
        self.angle = 0
        self.hits = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def center(self):
        return (self.x + self.size // 2, self.y + self.size // 2)

    def move(self, target, walls):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 250:
            mx = (dx / dist) * self.speed
            my = (dy / dist) * self.speed
        elif dist < 150:
            mx = -(dx / dist) * self.speed
            my = -(dy / dist) * self.speed
        else:
            mx = (-dy / dist) * self.speed
            my = (dx / dist) * self.speed
        self.x += mx
        self.y += my
        self.x = max(10, min(WIDTH - self.size - 10, self.x))
        self.y = max(10, min(HEIGHT - self.size - 10, self.y))

    def think(self, player, walls, bullets):
        result = {"bullets": [], "bombs": []}
        if self.cooldown_bombs > 0: self.cooldown_bombs -= 1
        if self.cooldown_eye > 0: self.cooldown_eye -= 1
        if self.cooldown_bombs == 0:
            for _ in range(5):
                bx = player.x + player.size // 2 + random.randint(-200, 200)
                by = player.y + player.size // 2 + random.randint(-150, 150)
                bx = max(40, min(WIDTH - 40, bx))
                by = max(40, min(HEIGHT - 40, by))
                result["bombs"].append(Bomb(bx, by, self, radius=90))
            self.cooldown_bombs = 240
            play(sound_bomb if sound_bomb else sound_explosion)
        if self.cooldown_eye == 0:
            cx, cy = self.center()
            px = player.x + player.size // 2
            py = player.y + player.size // 2
            dx = px - cx
            dy = py - cy
            dist = math.hypot(dx, dy)
            if dist > 0:
                vx = (dx / dist) * 10
                vy = (dy / dist) * 10
                b = Bullet(cx, cy, vx, vy, "laser", self, damage_override=1)
                b.color = CRIMSON
                result["bullets"].append(b)
            self.cooldown_eye = 90
            play(sound_shoot)
        return result

    def draw(self, surface):
        cx, cy = self.center()
        self.hover_phase += 0.1
        self.aura_phase += 0.08
        self.angle += 0.03
        aura_r = self.size // 2 + 30 + int(math.sin(self.aura_phase) * 10)
        aura_surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (220, 20, 60, 50), (aura_r, aura_r), aura_r)
        pygame.draw.circle(aura_surf, (220, 20, 60, 80), (aura_r, aura_r), aura_r - 12)
        pygame.draw.circle(aura_surf, (255, 100, 100, 100), (aura_r, aura_r), aura_r - 24)
        surface.blit(aura_surf, (cx - aura_r, cy - aura_r))
        shadow = pygame.Surface((60, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, 60, 20))
        surface.blit(shadow, (cx - 30, cy + 30))
        hover = math.sin(self.hover_phase) * 5
        cy_h = cy + hover
        arm_len = 38
        for angle_deg in [45, 135, 225, 315]:
            a = math.radians(angle_deg + self.angle * 20)
            ex = cx + math.cos(a) * arm_len
            ey = cy_h + math.sin(a) * arm_len
            pygame.draw.line(surface, BLACK, (cx, cy_h), (ex, ey), 6)
            pygame.draw.line(surface, DARK_GRAY, (cx, cy_h), (ex, ey), 3)
            prop_w = 24
            prop_h = 8
            prop_surf = pygame.Surface((prop_w * 2, prop_h * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(prop_surf, (40, 40, 40, 200), (0, prop_h, prop_w * 2, prop_h))
            prop_surf = pygame.transform.rotate(prop_surf, math.degrees(math.atan2(ey - cy_h, ex - cx)))
            rect = prop_surf.get_rect(center=(int(ex), int(ey)))
            surface.blit(prop_surf, rect)
            pygame.draw.circle(surface, DARK_GRAY, (int(ex), int(ey)), 5)
            pygame.draw.circle(surface, BLACK, (int(ex), int(ey)), 5, 2)
        pygame.draw.circle(surface, BLACK, (int(cx), int(cy_h)), 22)
        pygame.draw.circle(surface, DARK_GRAY, (int(cx), int(cy_h)), 22, 3)
        pygame.draw.circle(surface, (30, 30, 30), (int(cx), int(cy_h)), 16)
        pygame.draw.circle(surface, BLACK, (int(cx), int(cy_h)), 16, 2)
        pygame.draw.circle(surface, CRIMSON, (int(cx) - 7, int(cy_h) - 3), 6)
        pygame.draw.circle(surface, CRIMSON, (int(cx) + 7, int(cy_h) - 3), 6)
        pygame.draw.circle(surface, (255, 100, 100), (int(cx) - 7, int(cy_h) - 3), 3)
        pygame.draw.circle(surface, (255, 100, 100), (int(cx) + 7, int(cy_h) - 3), 3)
        eye_glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(eye_glow, (220, 20, 60, 80), (20, 20), 18)
        surface.blit(eye_glow, (int(cx) - 20, int(cy_h) - 20))
        bar_y = self.y - 18
        pygame.draw.rect(surface, (0, 0, 0), (self.x - 2, bar_y - 2, self.size + 4, 12), border_radius=4)
        pygame.draw.rect(surface, (60, 60, 60), (self.x, bar_y, self.size, 8), border_radius=3)
        fill = int(self.size * (max(0, self.hp) / self.max_hp))
        pygame.draw.rect(surface, CRIMSON, (self.x, bar_y, fill, 8), border_radius=3)


class MegaDroneBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 60
        self.hp = 15
        self.max_hp = 15
        self.speed = 2.8
        self.hover_phase = 0
        self.aura_phase = 0
        self.cooldown = 40
        self.angle = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def center(self):
        return (self.x + self.size // 2, self.y + self.size // 2)

    def move(self, target, walls):
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 200:
            mx = (dx / dist) * self.speed
            my = (dy / dist) * self.speed
        else:
            mx = (dx / dist) * self.speed * 0.5
            my = (dy / dist) * self.speed * 0.5
        self.x += mx
        self.y += my
        self.x = max(10, min(WIDTH - self.size - 10, self.x))
        self.y = max(10, min(HEIGHT - self.size - 10, self.y))

    def think(self, player, walls, bullets):
        result = {"bullets": []}
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.cooldown == 0:
            cx, cy = self.center()
            px = player.x + player.size // 2
            py = player.y + player.size // 2
            dx = px - cx
            dy = py - cy
            dist = math.hypot(dx, dy)
            if dist > 0:
                vx = (dx / dist) * 8
                vy = (dy / dist) * 8
                b = Bullet(cx, cy, vx, vy, "normal", self, damage_override=1)
                b.color = MEGA_DRONE_GREEN
                result["bullets"].append(b)
            self.cooldown = 40
            play(sound_shoot)
        return result

    def draw(self, surface):
        cx, cy = self.center()
        self.hover_phase += 0.1
        self.aura_phase += 0.08
        self.angle += 0.05
        aura_r = self.size // 2 + 22 + int(math.sin(self.aura_phase) * 6)
        aura_surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (60, 220, 80, 40), (aura_r, aura_r), aura_r)
        pygame.draw.circle(aura_surf, (60, 220, 80, 70), (aura_r, aura_r), aura_r - 10)
        surface.blit(aura_surf, (cx - aura_r, cy - aura_r))
        for i in range(6):
            angle = self.aura_phase * 2 + i * math.pi / 3
            ex = cx + math.cos(angle) * aura_r
            ey = cy + math.sin(angle) * aura_r
            mx = cx + math.cos(angle) * (aura_r - 12) + random.randint(-5, 5)
            my = cy + math.sin(angle) * (aura_r - 12) + random.randint(-5, 5)
            pygame.draw.line(surface, MEGA_DRONE_GREEN, (cx, cy), (int(mx), int(my)), 2)
            pygame.draw.line(surface, MEGA_DRONE_GREEN, (int(mx), int(my)), (int(ex), int(ey)), 2)
        shadow = pygame.Surface((50, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, 50, 16))
        surface.blit(shadow, (cx - 25, cy + 25))
        hover = math.sin(self.hover_phase) * 4
        cy_h = cy + hover
        arm_len = 28
        for angle_deg in [45, 135, 225, 315]:
            a = math.radians(angle_deg + self.angle * 20)
            ex = cx + math.cos(a) * arm_len
            ey = cy_h + math.sin(a) * arm_len
            pygame.draw.line(surface, BLACK, (cx, cy_h), (ex, ey), 5)
            pygame.draw.line(surface, DARK_GRAY, (cx, cy_h), (ex, ey), 2)
            pygame.draw.circle(surface, DARK_GRAY, (int(ex), int(ey)), 6)
            pygame.draw.circle(surface, BLACK, (int(ex), int(ey)), 6, 2)
        pygame.draw.circle(surface, BLACK, (int(cx), int(cy_h)), 18)
        pygame.draw.circle(surface, DARK_GRAY, (int(cx), int(cy_h)), 18, 3)
        pygame.draw.circle(surface, (20, 30, 20), (int(cx), int(cy_h)), 13)
        pygame.draw.circle(surface, BLACK, (int(cx), int(cy_h)), 13, 2)
        pygame.draw.circle(surface, MEGA_DRONE_GREEN, (int(cx) - 6, int(cy_h) - 2), 5)
        pygame.draw.circle(surface, MEGA_DRONE_GREEN, (int(cx) + 6, int(cy_h) - 2), 5)
        pygame.draw.circle(surface, (200, 255, 200), (int(cx) - 6, int(cy_h) - 2), 2)
        pygame.draw.circle(surface, (200, 255, 200), (int(cx) + 6, int(cy_h) - 2), 2)
        bar_y = self.y - 12
        pygame.draw.rect(surface, (0, 0, 0), (self.x - 2, bar_y - 2, self.size + 4, 10), border_radius=4)
        pygame.draw.rect(surface, (60, 60, 60), (self.x, bar_y, self.size, 6), border_radius=3)
        fill = int(self.size * (max(0, self.hp) / self.max_hp))
        pygame.draw.rect(surface, MEGA_DRONE_GREEN, (self.x, bar_y, fill, 6), border_radius=3)


class MegaTronBoss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 140
        self.hp = 40
        self.max_hp = 40
        self.speed = 1.3
        self.aura_phase = 0
        self.cooldown_axe = 180
        self.cooldown_drone = 240
        self.angle = 0
        self.drones_spawned = False
        self.face_dir = 1

    def rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def center(self):
        return (self.x + self.size // 2, self.y + self.size // 2)

    def move(self, target, walls):
        cx, cy = self.center()
        tx = target.x + target.size // 2
        ty = target.y + target.size // 2
        dx = tx - cx
        dy = ty - cy
        dist = math.hypot(dx, dy)
        if dist > 260:
            mx = (dx / dist) * self.speed
            my = (dy / dist) * self.speed
        elif dist < 140:
            mx = -(dx / dist) * self.speed * 0.8
            my = -(dy / dist) * self.speed * 0.8
        else:
            mx = 0
            my = 0
        if mx > 0.01:
            self.face_dir = 1
        elif mx < -0.01:
            self.face_dir = -1
        nr = self.rect().move(mx, 0)
        if not any(nr.colliderect(w) for w in walls) and 0 <= nr.x <= WIDTH - self.size:
            self.x += mx
        nr = self.rect().move(0, my)
        if not any(nr.colliderect(w) for w in walls) and 0 <= nr.y <= HEIGHT - self.size:
            self.y += my

    def think(self, player, walls, bullets, drones_alive):
        result = {"bullets": [], "axes": [], "drones_to_spawn": 0}
        if self.cooldown_axe > 0:
            self.cooldown_axe -= 1
        if self.cooldown_drone > 0:
            self.cooldown_drone -= 1
        if self.cooldown_axe == 0:
            cx, cy = self.center()
            tx = player.x + player.size // 2 + random.randint(-70, 70)
            ty = player.y + player.size // 2 + random.randint(-70, 70)
            tx = max(60, min(WIDTH - 60, tx))
            ty = max(60, min(HEIGHT - 60, ty))
            result["axes"].append(Axe(cx, cy - 40, tx, ty, self))
            self.cooldown_axe = 220
            play(sound_bomb if sound_bomb else sound_explosion)
        if not self.drones_spawned and self.cooldown_drone == 0:
            result["drones_to_spawn"] = 2
            self.drones_spawned = True
        return result

    def draw(self, surface, invulnerable=True):
        cx, cy = self.center()
        self.aura_phase += 0.05
        self.angle += 0.02
        aura_r = self.size // 2 + 30 + int(math.sin(self.aura_phase) * 10)
        aura_surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surf, (200, 20, 20, 40), (aura_r, aura_r), aura_r)
        pygame.draw.circle(aura_surf, (30, 10, 10, 100), (aura_r, aura_r), aura_r - 15)
        pygame.draw.circle(aura_surf, (200, 20, 20, 60), (aura_r, aura_r), aura_r - 30)
        surface.blit(aura_surf, (cx - aura_r, cy - aura_r))
        for i in range(8):
            a = self.aura_phase * 3 + i * math.pi / 4
            ex = cx + math.cos(a) * aura_r
            ey = cy + math.sin(a) * aura_r
            mx = cx + math.cos(a) * (aura_r - 20) + random.randint(-10, 10)
            my = cy + math.sin(a) * (aura_r - 20) + random.randint(-10, 10)
            pygame.draw.line(surface, MEGATRON_RED, (int(mx), int(my)), (int(ex), int(ey)), 3)
        shadow = pygame.Surface((self.size, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 150), (0, 0, self.size, 25))
        surface.blit(shadow, (self.x, self.y + self.size - 10))
        body = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(surface, MEGATRON_DARK, body, border_radius=16)
        pygame.draw.rect(surface, (60, 20, 20), body, 5, border_radius=16)
        shoulder_w = 26
        pygame.draw.rect(surface, (40, 15, 15),
                         (self.x - 12, self.y + 25, shoulder_w, self.size - 55), border_radius=8)
        pygame.draw.rect(surface, MEGATRON_RED,
                         (self.x - 12, self.y + 25, shoulder_w, self.size - 55), 3, border_radius=8)
        pygame.draw.rect(surface, (40, 15, 15),
                         (self.x + self.size - 14, self.y + 25, shoulder_w, self.size - 55), border_radius=8)
        pygame.draw.rect(surface, MEGATRON_RED,
                         (self.x + self.size - 14, self.y + 25, shoulder_w, self.size - 55), 3, border_radius=8)
        inner = body.inflate(-30, -30)
        pygame.draw.rect(surface, (60, 10, 10), inner, border_radius=12)
        pygame.draw.rect(surface, MEGATRON_RED, inner, 3, border_radius=12)
        for i in range(3):
            yy = inner.y + 10 + i * 14
            pygame.draw.line(surface, (30, 5, 5), (inner.x + 10, yy), (inner.right - 10, yy), 2)
        head_cx = cx
        head_cy = self.y + 34
        pygame.draw.rect(surface, (40, 15, 15), (cx - 14, self.y + 10, 28, 20), border_radius=4)
        helmet = pygame.Rect(cx - 38, head_cy - 30, 76, 58)
        pygame.draw.rect(surface, (50, 18, 18), helmet, border_radius=10)
        pygame.draw.rect(surface, MEGATRON_RED, helmet, 4, border_radius=10)
        horn_l = [(cx - 38, head_cy - 20), (cx - 58, head_cy - 40), (cx - 50, head_cy - 5)]
        horn_r = [(cx + 38, head_cy - 20), (cx + 58, head_cy - 40), (cx + 50, head_cy - 5)]
        pygame.draw.polygon(surface, (70, 25, 25), horn_l)
        pygame.draw.polygon(surface, MEGATRON_RED, horn_l, 2)
        pygame.draw.polygon(surface, (70, 25, 25), horn_r)
        pygame.draw.polygon(surface, MEGATRON_RED, horn_r, 2)
        face = pygame.Rect(cx - 26, head_cy - 16, 52, 38)
        pygame.draw.rect(surface, (30, 10, 10), face, border_radius=6)
        pygame.draw.rect(surface, (90, 30, 30), face, 2, border_radius=6)
        eye_y = head_cy - 2
        pygame.draw.ellipse(surface, (255, 40, 40), (cx - 20, eye_y - 7, 14, 8))
        pygame.draw.ellipse(surface, (255, 40, 40), (cx + 6, eye_y - 7, 14, 8))
        pygame.draw.ellipse(surface, (255, 200, 200), (cx - 18, eye_y - 6, 6, 4))
        pygame.draw.ellipse(surface, (255, 200, 200), (cx + 10, eye_y - 6, 6, 4))
        eye_glow = pygame.Surface((100, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(eye_glow, (255, 0, 0, 70), (10, 18, 30, 16))
        pygame.draw.ellipse(eye_glow, (255, 0, 0, 70), (60, 18, 30, 16))
        surface.blit(eye_glow, (cx - 50, head_cy - 30))
        pygame.draw.rect(surface, (20, 5, 5), (cx - 18, head_cy + 8, 36, 10), border_radius=3)
        for i in range(4):
            pygame.draw.line(surface, (120, 40, 40),
                             (cx - 16 + i * 10, head_cy + 8),
                             (cx - 16 + i * 10, head_cy + 18), 2)
        core_r = 10 + int(math.sin(self.aura_phase * 3) * 3)
        pygame.draw.circle(surface, (255, 80, 80), (cx, cy + 5), core_r)
        pygame.draw.circle(surface, (255, 200, 200), (cx, cy + 5), max(2, core_r - 4))
        bar_w = self.size
        bar_y = self.y - 25
        pygame.draw.rect(surface, (0, 0, 0), (self.x - 3, bar_y - 3, bar_w + 6, 18), border_radius=5)
        pygame.draw.rect(surface, (60, 60, 60), (self.x, bar_y, bar_w, 12), border_radius=4)
        if invulnerable:
            if (pygame.time.get_ticks() // 200) % 2 == 0:
                pygame.draw.rect(surface, PURPLE_LIGHTNING, (self.x, bar_y, bar_w, 12), border_radius=4)
        else:
            fill = int(bar_w * (max(0, self.hp) / self.max_hp))
            pygame.draw.rect(surface, MEGATRON_RED, (self.x, bar_y, fill, 12), border_radius=4)
        if invulnerable:
            inv_text = font.render("НЕУЯЗВИМ", True, PURPLE_LIGHTNING)
            surface.blit(inv_text, (cx - inv_text.get_width() // 2, self.y - 55))


# --- Генерация карт и фона ---

def create_walls(map_name):
    walls = [
        pygame.Rect(0, 0, WIDTH, 10),
        pygame.Rect(0, HEIGHT - 10, WIDTH, 10),
        pygame.Rect(0, 0, 10, HEIGHT),
        pygame.Rect(WIDTH - 10, 0, 10, HEIGHT),
    ]
    if map_name == "grass":
        walls.append(pygame.Rect(200, 150, 100, 30))
        walls.append(pygame.Rect(600, 150, 100, 30))
        walls.append(pygame.Rect(200, 420, 100, 30))
        walls.append(pygame.Rect(600, 420, 100, 30))
        walls.append(pygame.Rect(420, 250, 30, 100))
    elif map_name == "desert":
        walls.append(pygame.Rect(WIDTH // 2 - 15, 100, 30, 150))
        walls.append(pygame.Rect(WIDTH // 2 - 15, HEIGHT - 250, 30, 150))
        walls.append(pygame.Rect(150, HEIGHT // 2 - 15, 200, 30))
        walls.append(pygame.Rect(WIDTH - 350, HEIGHT // 2 - 15, 200, 30))
    elif map_name == "snow":
        for i in range(4):
            walls.append(pygame.Rect(100 + i * 180, 200, 30, 120))
        walls.append(pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40))
    elif map_name == "dead_forest":
        for i in range(5):
            walls.append(pygame.Rect(120 + i * 160, 120, 25, 80))
            walls.append(pygame.Rect(160 + i * 140, 380, 25, 80))
        walls.append(pygame.Rect(WIDTH // 2 - 20, HEIGHT // 2 - 20, 40, 40))
    elif map_name == "arena":
        walls.append(pygame.Rect(150, 150, 60, 60))
        walls.append(pygame.Rect(WIDTH - 210, 150, 60, 60))
        walls.append(pygame.Rect(150, HEIGHT - 210, 60, 60))
        walls.append(pygame.Rect(WIDTH - 210, HEIGHT - 210, 60, 60))
        walls.append(pygame.Rect(WIDTH // 2 - 40, HEIGHT // 2 - 40, 80, 80))
    elif map_name == "wasteland":
        walls.append(pygame.Rect(160, 120, 70, 50))
        walls.append(pygame.Rect(WIDTH - 230, 120, 70, 50))
        walls.append(pygame.Rect(160, HEIGHT - 170, 70, 50))
        walls.append(pygame.Rect(WIDTH - 230, HEIGHT - 170, 70, 50))
        walls.append(pygame.Rect(WIDTH // 2 - 45, HEIGHT // 2 - 35, 90, 70))
        walls.append(pygame.Rect(90, HEIGHT // 2 - 20, 60, 40))
        walls.append(pygame.Rect(WIDTH - 150, HEIGHT // 2 - 20, 60, 40))
    return walls


def create_wasteland_volcanoes():
    volcanoes = []
    data = [
        (120, 210, 180, 90),
        (WIDTH - 300, 170, 200, 100),
        (WIDTH // 2 - 60, 120, 160, 80),
        (80, HEIGHT - 140, 220, 100),
        (WIDTH - 280, HEIGHT - 150, 200, 95),
        (WIDTH // 2 + 120, HEIGHT - 120, 140, 70),
    ]
    for (x, y, w, h) in data:
        volcanoes.append({"x": x, "y": y, "w": w, "h": h, "phase": random.uniform(0, 6.28)})
    return volcanoes


def draw_background(surface, map_name):
    data = MAPS[map_name]
    surface.fill(data["bg"])
    if map_name == "wasteland":
        for i in range(0, WIDTH, 40):
            for j in range(0, HEIGHT, 40):
                if (i + j) % 80 == 0:
                    pygame.draw.circle(surface, data["bg2"], (i, j), 2)
        for _ in range(14):
            x = random.randint(20, WIDTH - 20)
            y = random.randint(20, HEIGHT - 20)
            points = [(x, y)]
            for _ in range(random.randint(3, 6)):
                x += random.randint(-40, 40)
                y += random.randint(-40, 40)
                points.append((x, y))
            for i in range(len(points) - 1):
                pygame.draw.line(surface, (120, 40, 10), points[i], points[i + 1], 4)
                pygame.draw.line(surface, LAVA, points[i], points[i + 1], 2)
        for v in wasteland_volcanoes:
            x, y, w, h = v["x"], v["y"], v["w"], v["h"]
            pygame.draw.polygon(surface, VOLCANO_DARK,
                                [(x, y), (x + w // 2, y - h), (x + w, y)])
            pygame.draw.polygon(surface, VOLCANO_ROCK,
                                [(x + 8, y), (x + w // 2, y - h + 6), (x + w - 8, y)], 3)
            pygame.draw.ellipse(surface, (30, 15, 10), (x + w // 2 - 22, y - h - 6, 44, 14))
            t = pygame.time.get_ticks() * 0.003 + v["phase"]
            lava_alpha = 150 + int(80 * (math.sin(t) + 1) / 2)
            lava_surf = pygame.Surface((36, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(lava_surf, (255, 120, 20, lava_alpha), (0, 0, 36, 10))
            surface.blit(lava_surf, (x + w // 2 - 18, y - h - 3))
            for k in range(3):
                lx = x + w // 2 - 10 + k * 10
                ly = y - h + 8
                pygame.draw.line(surface, LAVA, (lx, ly), (lx + random.randint(-8, 8), y - 5), 3)
        haze = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        haze.fill((40, 25, 20, 40))
        surface.blit(haze, (0, 0))
    else:
        for i in range(0, WIDTH, 40):
            for j in range(0, HEIGHT, 40):
                if (i + j) % 80 == 0:
                    pygame.draw.circle(surface, data["bg2"], (i, j), 2)


def draw_scorch_marks(surface):
    global scorch_marks
    for s in scorch_marks:
        x, y, r, life = s
        alpha = int(150 * (life / 600))
        if alpha > 0:
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (20, 10, 5, alpha), (r, r), r)
            pygame.draw.circle(surf, (10, 5, 0, alpha), (r, r), int(r * 0.6))
            surface.blit(surf, (x - r, y - r))
    scorch_marks = [[x, y, r, l - 1] for x, y, r, l in scorch_marks if l > 0]


def draw_walls(surface, walls, map_name):
    data = MAPS.get(map_name, MAPS["grass"])
    for w in walls:
        shadow = pygame.Surface((w.width, w.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), (0, 0, w.width, w.height), border_radius=5)
        surface.blit(shadow, (w.x + 3, w.y + 3))
        pygame.draw.rect(surface, data["wall"], w, border_radius=5)
        pygame.draw.rect(surface, BLACK, w, 2, border_radius=5)
        if map_name == "wasteland":
            pygame.draw.line(surface, (120, 40, 10), (w.x + 8, w.y + w.height // 2),
                             (w.x + w.width - 8, w.y + w.height // 2), 2)


def draw_vignette(surface):
    if vignette_surface is not None:
        surface.blit(vignette_surface, (0, 0))


def draw_low_hp_effect(surface, hp, max_hp):
    if hp > max_hp * 0.4:
        return
    intensity = 1.0 - (hp / (max_hp * 0.4))
    intensity = max(0, min(1, intensity))
    pulse = (math.sin(pygame.time.get_ticks() * 0.008) + 1) * 0.5
    alpha = int(120 * intensity * (0.4 + pulse * 0.6))
    if alpha <= 0:
        return
    red_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(40):
        a = int(alpha * (1 - i / 40))
        pygame.draw.rect(red_surf, (180, 0, 0, a), (i, i, WIDTH - i * 2, HEIGHT - i * 2), 3)
    surface.blit(red_surf, (0, 0))


def draw_menu(surface, selected):
    surface.fill((30, 30, 40))
    title = big_font.render("ТАНКИ", True, YELLOW)
    shadow = big_font.render("ТАНКИ", True, BLACK)
    surface.blit(shadow, (WIDTH // 2 - title.get_width() // 2 + 4, 84))
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
    subtitle = mid_font.render("Битва с боссами", True, WHITE)
    surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 180))
    options = ["Играть", "Управление", "Выход"]
    for i, opt in enumerate(options):
        color = YELLOW if i == selected else WHITE
        text = mid_font.render(opt, True, color)
        rect = text.get_rect(center=(WIDTH // 2, 300 + i * 70))
        if i == selected:
            pygame.draw.rect(surface, (0, 0, 0), rect.inflate(40, 20), border_radius=10)
            pygame.draw.rect(surface, YELLOW, rect.inflate(40, 20), 2, border_radius=10)
        surface.blit(text, rect)
    hint = font.render("Стрелки вверх/вниз — выбор, Enter — подтвердить", True, GRAY)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 40))


def draw_controls(surface):
    surface.fill((30, 30, 40))
    title = mid_font.render("УПРАВЛЕНИЕ", True, YELLOW)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
    lines = [
        "Зелёный танк:",
        "   W A S D — движение, Пробел — выстрел",
        "   1 2 3 4 5 6 — оружие",
        "   Q — КАМИКАДЗЕ (чёрный самолёт, 10 урона)",
        "",
        "Босс 1: ТАНК-БЕРСЕРК",
        "Босс 2: ДРОН-УБИЙЦА",
        "Босс 3: ТАНК-МЕГАТРОН (пустошь с вулканами)",
        "   — двигается и метает топор",
        "     (красный взрыв + мини-бомбы)",
        "",
        "Бонусы:",
        "   + аптечка, >> ускорение, x2 двойной выстрел, ~ спам",
        "",
        "Esc — пауза",
        "Нажми любую клавишу — назад",
    ]
    y = 70
    for line in lines:
        color = WHITE
        if line.startswith("Зелёный"): color = GREEN
        elif line.startswith("Босс 1"): color = PURPLE
        elif line.startswith("Босс 2"): color = CRIMSON
        elif line.startswith("Босс 3"): color = MEGATRON_RED
        text = small_font.render(line, True, color)
        surface.blit(text, (60, y))
        y += 26


def draw_pause(surface):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    text = big_font.render("ПАУЗА", True, YELLOW)
    surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
    hint = mid_font.render("Esc — продолжить", True, WHITE)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))


def draw_boss_victory(surface, level):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))
    surface.blit(overlay, (0, 0))
    names = {1: "ТАНК-БЕРСЕРК", 2: "ДРОН-УБИЙЦА", 3: "ТАНК-МЕГАТРОН"}
    colors = {1: PURPLE, 2: CRIMSON, 3: MEGATRON_RED}
    text = big_font.render(f"БОСС {level} ПОБЕЖДЁН!", True, colors.get(level, PURPLE))
    surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 150))
    name = mid_font.render(names.get(level, ""), True, WHITE)
    surface.blit(name, (WIDTH // 2 - name.get_width() // 2, 230))
    if level < 3:
        sub = mid_font.render("Следующий босс...", True, YELLOW)
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 300))
        hint = font.render("Enter — продолжить, Esc — в меню", True, YELLOW)
    else:
        sub = big_font.render("ТЫ ЧЕМПИОН!", True, YELLOW)
        surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 280))
        sub2 = mid_font.render("Все три босса повержены!", True, WHITE)
        surface.blit(sub2, (WIDTH // 2 - sub2.get_width() // 2, 360))
        hint = font.render("Esc — в меню", True, YELLOW)
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))


def draw_boss_hud(surface, player_hp, player_max_hp, boss, level, in_bunker=False):
    bar_w, bar_h = 250, 26
    x, y = 20, HEIGHT - 40
    pygame.draw.rect(surface, (0, 0, 0), (x - 2, y - 2, bar_w + 4, bar_h + 4), border_radius=6)
    pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_w, bar_h), border_radius=4)
    fill = int(bar_w * (max(0, player_hp) / player_max_hp))
    pygame.draw.rect(surface, GREEN, (x, y, fill, bar_h), border_radius=4)
    text = font.render(f"ТЫ: {max(0, player_hp)}/{player_max_hp}", True, WHITE)
    surface.blit(text, (x + 10, y + 2))
    if in_bunker:
        shield_text = font.render("В УКРЫТИИ", True, (60, 200, 100))
        pygame.draw.rect(surface, (0, 0, 0), (20, HEIGHT - 80, 160, 32), border_radius=6)
        pygame.draw.rect(surface, (60, 200, 100), (20, HEIGHT - 80, 160, 32), 2, border_radius=6)
        surface.blit(shield_text, (30, HEIGHT - 75))
    bar_w2 = 400
    x2 = WIDTH // 2 - bar_w2 // 2
    y2 = 20
    pygame.draw.rect(surface, (0, 0, 0), (x2 - 3, y2 - 3, bar_w2 + 6, 34), border_radius=8)
    pygame.draw.rect(surface, (40, 10, 50), (x2, y2, bar_w2, 28), border_radius=6)
    fill2 = int(bar_w2 * (max(0, boss.hp) / boss.max_hp))
    boss_color = {1: PURPLE, 2: CRIMSON}.get(level, PURPLE)
    pygame.draw.rect(surface, boss_color, (x2, y2, fill2, 28), border_radius=6)
    names = {1: "ТАНК-БЕРСЕРК", 2: "ДРОН-УБИЙЦА"}
    title = font.render(f"УРОВЕНЬ {level} — {names.get(level, '')}", True, WHITE)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, y2 + 35))


# --- Основная логика боев ---

def boss_fight(level=1):
    global shake_amount
    if MENU_MUSIC:
        play_music(MENU_MUSIC, volume=0.4)

    if level == 1:
        map_name = "arena"
    else:
        map_name = "dead_forest"

    walls = create_walls(map_name)
    player = Tank(50, HEIGHT - 90, GREEN, DARK_GREEN, {
        "up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d,
        "shoot": pygame.K_SPACE}, "Игрок")
    player.hp = 10
    player.max_hp = 10
    if level == 1:
        boss = BerserkBoss(WIDTH // 2 - 45, 100)
    else:
        boss = DroneBoss(WIDTH // 2 - 40, 100)
    bunkers = []
    if level == 2:
        bunkers = [
            Bunker(70, HEIGHT - 240, 150, 120),
            Bunker(WIDTH // 2 - 75, 60, 150, 120),
            Bunker(WIDTH - 220, HEIGHT - 240, 150, 120),
        ]
    bullets = []
    kamikazes = []
    mines = []
    thunders = []
    bombs = []
    bonuses = []
    explosions = []
    shockwaves = []
    blood_splats = []
    smokes = []
    paused = False
    round_over = False
    won = False
    bonus_timer = 0
    slowmo_timer = 0
    p1_weapons = {
        pygame.K_1: "normal", pygame.K_2: "rocket", pygame.K_3: "laser",
        pygame.K_4: "ice", pygame.K_5: "mine", pygame.K_6: "homing",
        pygame.K_q: "kamikaze",
    }
    while True:
        if slowmo_timer > 0:
            clock.tick(20)
            slowmo_timer -= 1
        else:
            clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_music()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if round_over:
                        stop_music()
                        return "menu"
                    paused = not paused
                if round_over and event.key == pygame.K_RETURN:
                    if won and level < 2:
                        stop_music()
                        return boss_fight(level + 1)
                    elif won and level == 2:
                        stop_music()
                        return megatron_battle()
                    else:
                        stop_music()
                        return boss_fight(level)
                if not paused and not round_over:
                    if event.key in p1_weapons:
                        player.weapon = p1_weapons[event.key]
                        play(sound_switch)
        if paused:
            draw_background(game_surface, map_name)
            draw_walls(game_surface, walls, map_name)
            for bunker in bunkers:
                bunker.draw(game_surface)
            player.draw(game_surface)
            boss.draw(game_surface)
            for k in kamikazes: k.draw(game_surface)
            for t in thunders: t.draw(game_surface)
            for b in bombs: b.draw(game_surface)
            for b in bullets: b.draw(game_surface)
            draw_pause(game_surface)
            present()
            continue
        if not round_over:
            all_walls = list(walls)
            for bunker in bunkers:
                all_walls.extend(bunker.get_walls())
            player.move(keys, all_walls, [])
            player.update()
            if keys[player.controls["shoot"]]:
                new = player.shoot(target=boss)
                for b in new:
                    if isinstance(b, Kamikaze):
                        kamikazes.append(b)
                    elif isinstance(b, Mine):
                        mines.append(b)
                    else:
                        bullets.append(b)
            player_in_bunker = any(b.is_player_inside(player) for b in bunkers)
            if player_in_bunker:
                boss_actions = {"bullets": [], "thunders": [], "bombs": []}
            else:
                boss_actions = boss.think(player, walls, bullets)
            for b in boss_actions.get("bullets", []):
                bullets.append(b)
            for t in boss_actions.get("thunders", []):
                thunders.append(t)
            for bm in boss_actions.get("bombs", []):
                bombs.append(bm)
            boss.move(player, walls)
            for k in kamikazes:
                k.update(all_walls)
                if k.alive and k.rect().colliderect(boss.rect()):
                    k.alive = False
                    boss.hp -= 10
                    play(sound_explosion)
                    for _ in range(12):
                        ex = k.x + random.randint(-80, 80)
                        ey = k.y + random.randint(-80, 80)
                        explosions.append(Explosion(ex, ey,
                            [ORANGE, BRIGHT_ORANGE, YELLOW, RED],
                            count=50, speed_mult=2.2))
                        add_scorch(ex, ey, radius=90)
                    shockwaves.append(Shockwave(k.x, k.y, max_radius=180))
                    shake_screen(20)
                    if boss.hp <= 0:
                        boss.hp = 0
                        round_over = True
                        won = True
                        slowmo_timer = 60
                        explosions.append(Explosion(boss.x + boss.size // 2, boss.y + boss.size // 2,
                                                    [PURPLE, YELLOW, RED, WHITE], count=60))
                        shockwaves.append(Shockwave(boss.x + boss.size // 2, boss.y + boss.size // 2, max_radius=250))
            kamikazes = [k for k in kamikazes if k.alive]
            for m in mines:
                m.update()
            mines = [m for m in mines if m.alive]
            for m in mines[:]:
                if m.arm_time > 0: continue
                if m.owner != boss and m.rect().colliderect(boss.rect()):
                    boss.hp -= 2
                    explosions.append(Explosion(m.x, m.y, [PURPLE, YELLOW]))
                    play(sound_explosion)
                    mines.remove(m)
                    if boss.hp <= 0:
                        boss.hp = 0
                        round_over = True
                        won = True
                        slowmo_timer = 60
                elif m.owner != player and m.rect().colliderect(player.rect()):
                    player.hp -= 2
                    explosions.append(Explosion(m.x, m.y, [PURPLE, RED]))
                    blood_splats.append(BloodSplat(player.x + player.size // 2, player.y + player.size // 2, RED))
                    play(sound_explosion)
                    mines.remove(m)
                    if player.hp <= 0:
                        player.hp = 0
                        round_over = True
                        won = False
            for t in thunders:
                t.update()
                t_rect = pygame.Rect(t.target_x - 30, t.target_y - 30, 60, 60)
                if t.life > 20 and t_rect.colliderect(player.rect()):
                    if not t._damaged:
                        player.hp -= t.damage
                        t._damaged = True
                        explosions.append(Explosion(t.target_x, t.target_y, [PURPLE, WHITE, DARK_PURPLE]))
                        if player.hp <= 0:
                            player.hp = 0
                            round_over = True
                            won = False
            thunders = [t for t in thunders if t.alive()]
            for bm in bombs:
                bm.update()
                if bm.exploded and not bm._damaged:
                    if bm.rect().colliderect(player.rect()):
                        player.hp -= 2
                        bm._damaged = True
                        explosions.append(Explosion(bm.x, bm.y, [ORANGE, YELLOW, BRIGHT_ORANGE], count=40))
                        if player.hp <= 0:
                            player.hp = 0
                            round_over = True
                            won = False
            bombs = [bm for bm in bombs if bm.alive()]
            for b in bullets:
                if isinstance(b, Mine):
                    b.update()
                else:
                    b.update(all_walls, [player, boss])
                if b.alive and b.owner == boss:
                    for bunker in bunkers:
                        if bunker.blocks_bullet(b.rect()):
                            b.alive = False
                            break
                if b.alive and b.owner == player and b.rect().colliderect(boss.rect()):
                    b.alive = False
                    boss.hp -= b.damage
                    boss.hits += 1
                    explosions.append(Explosion(b.x, b.y, [PURPLE, WHITE]))
                    play(sound_hit)
                    if boss.hp <= 0:
                        boss.hp = 0
                        round_over = True
                        won = True
                        slowmo_timer = 60
                        explosions.append(Explosion(boss.x + boss.size // 2, boss.y + boss.size // 2,
                                                    [PURPLE, YELLOW, RED, WHITE], count=60))
                        shockwaves.append(Shockwave(boss.x + boss.size // 2, boss.y + boss.size // 2, max_radius=250))
                        play(sound_explosion)
                if b.alive and b.owner == boss and b.rect().colliderect(player.rect()):
                    b.alive = False
                    player.hp -= b.damage
                    explosions.append(Explosion(b.x, b.y, [PURPLE, RED]))
                    blood_splats.append(BloodSplat(b.x, b.y, RED))
                    play(sound_hit)
                    if player.hp <= 0:
                        player.hp = 0
                        round_over = True
                        won = False
            bullets = [b for b in bullets if b.alive]
            if player.hp < player.max_hp * 0.3 and player.smoke_timer % 6 == 0:
                smokes.append(SmokeEmitter(player.x + player.size // 2, player.y))
            bonus_timer += 1
            if bonus_timer > 300 and len(bonuses) < 2:
                bonus_timer = 0
                bx = random.randint(60, WIDTH - 80)
                by = random.randint(60, HEIGHT - 80)
                rect = pygame.Rect(bx, by, 24, 24)
                if not any(rect.colliderect(w) for w in all_walls):
                    bonuses.append(Bonus(bx, by, random.choice(["health", "speed", "double", "rapid"])))
            for bonus in bonuses:
                bonus.update()
            bonuses = [b for b in bonuses if b.life > 0]
            for bonus in bonuses[:]:
                if player.rect().colliderect(bonus.rect()):
                    if bonus.kind == "health":
                        player.hp = min(player.max_hp, player.hp + 1)
                    elif bonus.kind == "speed":
                        player.speed_boost = 300
                    elif bonus.kind == "double":
                        player.double_shot = 300
                    elif bonus.kind == "rapid":
                        player.rapid_fire = 600
                    bonuses.remove(bonus)
                    play(sound_bonus)
            if player.hp <= 0 and not round_over:
                player.hp = 0
                round_over = True
                won = False
        for e in explosions:
            e.update()
        explosions = [e for e in explosions if e.alive()]
        for s in shockwaves:
            s.update()
        shockwaves = [s for s in shockwaves if s.alive()]
        for bs in blood_splats:
            bs.update()
        blood_splats = [bs for bs in blood_splats if bs.alive()]
        for sm in smokes:
            sm.update()
        smokes = [sm for sm in smokes if sm.alive()]
        shake_off_x, shake_off_y = 0, 0
        if shake_amount > 0:
            shake_off_x = random.randint(-shake_amount, shake_amount)
            shake_off_y = random.randint(-shake_amount, shake_amount)
            shake_amount = max(0, shake_amount - 1)
        render_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_background(render_surface, map_name)
        draw_scorch_marks(render_surface)
        draw_walls(render_surface, walls, map_name)
        for bunker in bunkers:
            bunker.draw(render_surface)
        for m in mines: m.draw(render_surface)
        for bm in bombs: bm.draw(render_surface)
        for bonus in bonuses: bonus.draw(render_surface)
        for k in kamikazes: k.draw(render_surface)
        for sm in smokes: sm.draw(render_surface)
        player.draw(render_surface)
        if boss.hp > 0:
            boss.draw(render_surface)
        for t in thunders: t.draw(render_surface)
        for b in bullets: b.draw(render_surface)
        for bs in blood_splats: bs.draw(render_surface)
        for s in shockwaves: s.draw(render_surface)
        for e in explosions: e.draw(render_surface)
        game_surface.fill(BLACK)
        game_surface.blit(render_surface, (shake_off_x, shake_off_y))
        draw_vignette(game_surface)
        draw_low_hp_effect(game_surface, player.hp, player.max_hp)
        player_in_bunker = any(b.is_player_inside(player) for b in bunkers)
        draw_boss_hud(game_surface, player.hp, player.max_hp, boss, level, in_bunker=player_in_bunker)
        wtext = small_font.render(f"Оружие: {WEAPON_NAMES[player.weapon]}", True, WEAPON_COLORS[player.weapon])
        game_surface.blit(wtext, (20, HEIGHT - 70))
        if slowmo_timer > 0:
            sm_text = big_font.render("SLOW-MO", True, YELLOW)
            alpha = int(255 * (slowmo_timer / 60))
            sm_surf = pygame.Surface((sm_text.get_width(), sm_text.get_height()), pygame.SRCALPHA)
            sm_surf.blit(sm_text, (0, 0))
            sm_surf.set_alpha(alpha)
            game_surface.blit(sm_surf, (WIDTH // 2 - sm_text.get_width() // 2, 80))
        if round_over:
            if won:
                draw_boss_victory(game_surface, level)
            else:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 220))
                game_surface.blit(overlay, (0, 0))
                text = big_font.render("ТЫ ПРОИГРАЛ", True, RED)
                game_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))
                sub = mid_font.render("Босс оказался сильнее...", True, WHITE)
                game_surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 300))
                hint = font.render("Enter — рестарт, Esc — в меню", True, YELLOW)
                game_surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))
        present()


def megatron_battle():
    global shake_amount, wasteland_volcanoes
    if MENU_MUSIC:
        play_music(MENU_MUSIC, volume=0.4)

    map_name = "wasteland"
    wasteland_volcanoes = create_wasteland_volcanoes()
    walls = create_walls(map_name)

    bunkers = [
        Bunker(100, HEIGHT - 220, 160, 130),
        Bunker(WIDTH // 2 - 80, HEIGHT - 220, 160, 130),
        Bunker(WIDTH - 260, HEIGHT - 220, 160, 130),
    ]

    player = Tank(WIDTH // 2 - 20, HEIGHT - 90, GREEN, DARK_GREEN, {
        "up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d,
        "shoot": pygame.K_SPACE}, "Игрок")
    player.hp = 15
    player.max_hp = 15

    megan = MegaTronBoss(WIDTH // 2 - 70, 60)

    drones = []
    bullets = []
    mines = []
    lightnings = []
    explosions = []
    shockwaves = []
    blood_splats = []
    smokes = []
    bonuses = []
    axes = []
    mini_bombs = []
    paused = False
    round_over = False
    won = False
    bonus_timer = 0
    slowmo_timer = 0

    p1_weapons = {
        pygame.K_1: "normal", pygame.K_2: "rocket", pygame.K_3: "laser",
        pygame.K_4: "ice", pygame.K_5: "mine", pygame.K_6: "homing",
        pygame.K_q: "kamikaze",
    }

    while True:
        if slowmo_timer > 0:
            clock.tick(20)
            slowmo_timer -= 1
        else:
            clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_music()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if round_over:
                        stop_music()
                        return "menu"
                    paused = not paused
                if round_over and event.key == pygame.K_RETURN:
                    stop_music()
                    return megatron_battle()
                if not paused and not round_over:
                    if event.key in p1_weapons:
                        player.weapon = p1_weapons[event.key]
                        play(sound_switch)

        if paused:
            draw_background(game_surface, map_name)
            draw_walls(game_surface, walls, map_name)
            for b in bunkers:
                b.draw(game_surface)
            player.draw(game_surface)
            megan.draw(game_surface, invulnerable=len(drones) > 0)
            for d in drones:
                d.draw(game_surface)
            for a in axes:
                a.draw(game_surface)
            for mb in mini_bombs:
                mb.draw(game_surface)
            for l in lightnings:
                l.draw(game_surface)
            for b in bullets:
                b.draw(game_surface)
            draw_pause(game_surface)
            present()
            continue

        if not round_over:
            all_walls = list(walls)
            for bunker in bunkers:
                all_walls.extend(bunker.get_walls())

            player.move(keys, all_walls, [])
            player.update()

            if keys[player.controls["shoot"]]:
                target = megan if len(drones) == 0 else (drones[0] if drones else megan)
                new = player.shoot(target=target)
                for b in new:
                    if isinstance(b, Mine):
                        mines.append(b)
                    elif isinstance(b, Kamikaze):
                        bullets.append(b)
                    else:
                        bullets.append(b)

            player_in_bunker = any(b.is_player_inside(player) for b in bunkers)
            if player_in_bunker:
                megan_actions = {"bullets": [], "axes": [], "drones_to_spawn": 0}
            else:
                megan_actions = megan.think(player, walls, bullets, len(drones))

            if megan_actions.get("drones_to_spawn", 0) > 0:
                for i in range(2):
                    dx = WIDTH // 2 + (i - 0.5) * 200
                    dy = 250
                    drones.append(MegaDroneBoss(dx, dy))
                play(sound_bomb if sound_bomb else sound_explosion)

            for b in megan_actions.get("bullets", []):
                bullets.append(b)
            for a in megan_actions.get("axes", []):
                axes.append(a)

            megan.move(player, walls)

            for a in axes[:]:
                a.update(player, drones, walls)
                if a.landed and not a.mini_bombs_spawned:
                    a.mini_bombs_spawned = True
                    if math.hypot(player.x + player.size // 2 - a.target_x,
                                  player.y + player.size // 2 - a.target_y) <= a.area:
                        player.hp -= a.damage
                        blood_splats.append(BloodSplat(player.x + player.size // 2,
                                                       player.y + player.size // 2, RED))
                        explosions.append(Explosion(player.x + player.size // 2,
                                                    player.y + player.size // 2,
                                                    [RED, CRIMSON, DARK_CRIMSON], count=40))
                        if player.hp <= 0:
                            player.hp = 0
                            round_over = True
                            won = False
                    for d in drones[:]:
                        if math.hypot(d.x + d.size // 2 - a.target_x,
                                      d.y + d.size // 2 - a.target_y) <= a.area:
                            d.hp -= a.damage
                            if d.hp <= 0:
                                explosions.append(Explosion(d.x + d.size // 2, d.y + d.size // 2,
                                                            [MEGA_DRONE_GREEN, WHITE, YELLOW], count=40))
                                drones.remove(d)
                    explosions.append(Explosion(a.target_x, a.target_y,
                                                [RED, CRIMSON, DARK_CRIMSON, WHITE],
                                                count=70, speed_mult=1.8))
                    shockwaves.append(Shockwave(a.target_x, a.target_y,
                                                max_radius=a.area + 40, color=(255, 60, 60)))
                    for _ in range(10):
                        ang = random.uniform(0, math.pi * 2)
                        spd = random.uniform(3.5, 8.0)
                        mini_bombs.append(MiniBomb(
                            a.target_x, a.target_y,
                            math.cos(ang) * spd, math.sin(ang) * spd,
                            megan, delay=random.randint(30, 55)))
                if not a.alive:
                    axes.remove(a)

            for mb in mini_bombs[:]:
                mb.update(all_walls)
                if mb.exploded and not hasattr(mb, '_applied'):
                    mb._applied = True
                    if math.hypot(player.x + player.size // 2 - mb.x,
                                  player.y + player.size // 2 - mb.y) <= mb.blast_radius:
                        player.hp -= mb.damage
                        blood_splats.append(BloodSplat(player.x + player.size // 2,
                                                       player.y + player.size // 2, RED))
                        if player.hp <= 0:
                            player.hp = 0
                            round_over = True
                            won = False
                    for d in drones[:]:
                        if math.hypot(d.x + d.size // 2 - mb.x,
                                      d.y + d.size // 2 - mb.y) <= mb.blast_radius:
                            d.hp -= mb.damage
                            if d.hp <= 0:
                                explosions.append(Explosion(d.x + d.size // 2, d.y + d.size // 2,
                                                            [MEGA_DRONE_GREEN, WHITE, YELLOW], count=30))
                                drones.remove(d)
                if not mb.alive:
                    mini_bombs.remove(mb)

            for d in drones:
                actions = d.think(player, walls, bullets)
                for b in actions.get("bullets", []):
                    bullets.append(b)
                d.move(player, walls)

            for d in drones:
                if d.rect().colliderect(player.rect()):
                    player.hp -= 1
                    blood_splats.append(BloodSplat(player.x + player.size // 2, player.y + player.size // 2, RED))
                    shake_screen(3)
                    explosions.append(Explosion(d.x + d.size // 2, d.y + d.size // 2, [MEGA_DRONE_GREEN, RED]))

            for m in mines:
                m.update()
            mines = [m for m in mines if m.alive]

            for b in bullets:
                if isinstance(b, Mine):
                    b.update()
                elif isinstance(b, Kamikaze):
                    b.update(all_walls)
                    if b.alive:
                        hit_megan = b.rect().colliderect(megan.rect())
                        hit_drone = None
                        for d in drones:
                            if b.rect().colliderect(d.rect()):
                                hit_drone = d
                                break

                        if hit_megan or hit_drone:
                            b.alive = False
                            play(sound_explosion)
                            blast_radius = 120
                            bx, by = b.x, b.y

                            for d in drones[:]:
                                dcx = d.x + d.size // 2
                                dcy = d.y + d.size // 2
                                if math.hypot(dcx - bx, dcy - by) <= blast_radius:
                                    d.hp -= 10
                                    explosions.append(Explosion(dcx, dcy,
                                                                [MEGA_DRONE_GREEN, WHITE, YELLOW], count=40))
                                    shockwaves.append(Shockwave(dcx, dcy, max_radius=140))
                                    play(sound_hit)
                                    if d.hp <= 0:
                                        explosions.append(Explosion(dcx, dcy,
                                                                    [MEGA_DRONE_GREEN, WHITE, YELLOW], count=50))
                                        shockwaves.append(Shockwave(dcx, dcy, max_radius=180))
                                        drones.remove(d)
                                        play(sound_explosion)
                                        shake_screen(8)

                            if len(drones) == 0:
                                mcx = megan.x + megan.size // 2
                                mcy = megan.y + megan.size // 2
                                if math.hypot(mcx - bx, mcy - by) <= blast_radius + megan.size // 2:
                                    megan.hp -= 10

                            for _ in range(12):
                                ex = bx + random.randint(-90, 90)
                                ey = by + random.randint(-90, 90)
                                explosions.append(Explosion(ex, ey,
                                    [ORANGE, BRIGHT_ORANGE, YELLOW, RED],
                                    count=50, speed_mult=2.2))
                                add_scorch(ex, ey, radius=90)
                            shockwaves.append(Shockwave(bx, by, max_radius=220))
                            shake_screen(20)

                            if megan.hp <= 0 and len(drones) == 0:
                                megan.hp = 0
                                round_over = True
                                won = True
                                slowmo_timer = 60
                                explosions.append(Explosion(megan.x + megan.size // 2, megan.y + megan.size // 2,
                                                            [MEGATRON_RED, YELLOW, WHITE, ORANGE], count=80))
                                shockwaves.append(Shockwave(megan.x + megan.size // 2, megan.y + megan.size // 2, max_radius=300))
                                shake_screen(25)
                else:
                    enemies_list = [player, megan] + drones
                    b.update(all_walls, enemies_list)

                if b.alive and getattr(b, 'is_red_laser', False):
                    if b.rect().colliderect(player.rect()):
                        b.alive = False
                        player.hp -= 2
                        blood_splats.append(BloodSplat(player.x + player.size // 2, player.y + player.size // 2, RED))
                        for _ in range(3):
                            lx = b.x + random.randint(-40, 40)
                            ly = b.y + random.randint(-40, 40)
                            lightnings.append(PurpleLightning(lx, ly))
                            add_scorch(lx, ly, radius=60)
                        explosions.append(Explosion(b.x, b.y, [PURPLE_LIGHTNING, PURPLE, WHITE], count=30))
                        shake_screen(8)
                        play(sound_explosion)
                        if player.hp <= 0:
                            player.hp = 0
                            round_over = True
                            won = False
                    for bunker in bunkers:
                        if bunker.blocks_bullet(b.rect()):
                            b.alive = False
                            break

                if b.alive and b.owner == player and not isinstance(b, Kamikaze) and not isinstance(b, Mine):
                    for d in drones[:]:
                        if b.rect().colliderect(d.rect()):
                            b.alive = False
                            d.hp -= b.damage
                            explosions.append(Explosion(b.x, b.y, [MEGA_DRONE_GREEN, WHITE]))
                            play(sound_hit)
                            if d.hp <= 0:
                                explosions.append(Explosion(d.x + d.size // 2, d.y + d.size // 2,
                                                            [MEGA_DRONE_GREEN, WHITE, YELLOW], count=40))
                                shockwaves.append(Shockwave(d.x + d.size // 2, d.y + d.size // 2, max_radius=120))
                                drones.remove(d)
                                play(sound_explosion)
                                shake_screen(6)
                            break
                    if b.alive and len(drones) == 0 and b.rect().colliderect(megan.rect()):
                        b.alive = False
                        megan.hp -= b.damage
                        explosions.append(Explosion(b.x, b.y, [MEGATRON_RED, WHITE]))
                        play(sound_hit)
                        if megan.hp <= 0:
                            megan.hp = 0
                            round_over = True
                            won = True
                            slowmo_timer = 60
                            explosions.append(Explosion(megan.x + megan.size // 2, megan.y + megan.size // 2,
                                                        [MEGATRON_RED, YELLOW, WHITE, ORANGE], count=80))
                            shockwaves.append(Shockwave(megan.x + megan.size // 2, megan.y + megan.size // 2, max_radius=300))
                            shake_screen(25)

                if b.alive and b.owner in drones and b.rect().colliderect(player.rect()):
                    b.alive = False
                    player.hp -= b.damage
                    blood_splats.append(BloodSplat(b.x, b.y, RED))
                    explosions.append(Explosion(b.x, b.y, [MEGA_DRONE_GREEN, RED]))
                    if player.hp <= 0:
                        player.hp = 0
                        round_over = True
                        won = False

            bullets = [b for b in bullets if b.alive]

            for l in lightnings:
                l.update()
                if l.rect().colliderect(player.rect()) and not l._damaged:
                    player.hp -= 1
                    l._damaged = True
                    blood_splats.append(BloodSplat(player.x + player.size // 2, player.y + player.size // 2, RED))
            lightnings = [l for l in lightnings if l.alive()]

            if player.hp < player.max_hp * 0.3 and player.smoke_timer % 6 == 0:
                smokes.append(SmokeEmitter(player.x + player.size // 2, player.y))

            bonus_timer += 1
            if bonus_timer > 300 and len(bonuses) < 2:
                bonus_timer = 0
                bx = random.randint(60, WIDTH - 80)
                by = random.randint(250, HEIGHT - 80)
                rect = pygame.Rect(bx, by, 24, 24)
                if not any(rect.colliderect(w) for w in all_walls):
                    bonuses.append(Bonus(bx, by, random.choice(["health", "speed", "double", "rapid"])))

            for bonus in bonuses:
                bonus.update()
            bonuses = [b for b in bonuses if b.life > 0]
            for bonus in bonuses[:]:
                if player.rect().colliderect(bonus.rect()):
                    if bonus.kind == "health":
                        player.hp = min(player.max_hp, player.hp + 1)
                    elif bonus.kind == "speed":
                        player.speed_boost = 300
                    elif bonus.kind == "double":
                        player.double_shot = 300
                    elif bonus.kind == "rapid":
                        player.rapid_fire = 600
                    bonuses.remove(bonus)
                    play(sound_bonus)

            if player.hp <= 0 and not round_over:
                player.hp = 0
                round_over = True
                won = False

        for e in explosions:
            e.update()
        explosions = [e for e in explosions if e.alive()]
        for s in shockwaves:
            s.update()
        shockwaves = [s for s in shockwaves if s.alive()]
        for bs in blood_splats:
            bs.update()
        blood_splats = [bs for bs in blood_splats if bs.alive()]
        for sm in smokes:
            sm.update()
        smokes = [sm for sm in smokes if sm.alive()]

        shake_off_x, shake_off_y = 0, 0
        if shake_amount > 0:
            shake_off_x = random.randint(-shake_amount, shake_amount)
            shake_off_y = random.randint(-shake_amount, shake_amount)
            shake_amount = max(0, shake_amount - 1)

        render_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_background(render_surface, map_name)
        draw_scorch_marks(render_surface)
        draw_walls(render_surface, walls, map_name)
        for bunker in bunkers:
            bunker.draw(render_surface)
        for m in mines:
            m.draw(render_surface)
        for mb in mini_bombs:
            mb.draw(render_surface)
        for a in axes:
            a.draw(render_surface)
        for bonus in bonuses:
            bonus.draw(render_surface)
        for sm in smokes:
            sm.draw(render_surface)
        player.draw(render_surface)

        megan.draw(render_surface, invulnerable=len(drones) > 0)

        for d in drones:
            d.draw(render_surface)

        for b in bullets:
            b.draw(render_surface)
        for l in lightnings:
            l.draw(render_surface)
        for bs in blood_splats:
            bs.draw(render_surface)
        for s in shockwaves:
            s.draw(render_surface)
        for e in explosions:
            e.draw(render_surface)

        game_surface.fill(BLACK)
        game_surface.blit(render_surface, (shake_off_x, shake_off_y))
        draw_vignette(game_surface)
        draw_low_hp_effect(game_surface, player.hp, player.max_hp)

        player_in_bunker = any(b.is_player_inside(player) for b in bunkers)
        if player_in_bunker:
            shield_text = font.render("В УКРЫТИИ", True, (60, 200, 100))
            pygame.draw.rect(game_surface, (0, 0, 0), (20, HEIGHT - 80, 160, 32), border_radius=6)
            pygame.draw.rect(game_surface, (60, 200, 100), (20, HEIGHT - 80, 160, 32), 2, border_radius=6)
            game_surface.blit(shield_text, (30, HEIGHT - 75))

        bar_w, bar_h = 250, 26
        x, y = 20, HEIGHT - 40
        pygame.draw.rect(game_surface, (0, 0, 0), (x - 2, y - 2, bar_w + 4, bar_h + 4), border_radius=6)
        pygame.draw.rect(game_surface, (60, 60, 60), (x, y, bar_w, bar_h), border_radius=4)
        fill = int(bar_w * (max(0, player.hp) / player.max_hp))
        pygame.draw.rect(game_surface, GREEN, (x, y, fill, bar_h), border_radius=4)
        text = font.render(f"ТЫ: {max(0, player.hp)}/{player.max_hp}", True, WHITE)
        game_surface.blit(text, (x + 10, y + 2))

        bar_w2 = 400
        x2 = WIDTH // 2 - bar_w2 // 2
        y2 = 20
        pygame.draw.rect(game_surface, (0, 0, 0), (x2 - 3, y2 - 3, bar_w2 + 6, 34), border_radius=8)
        pygame.draw.rect(game_surface, (40, 10, 10), (x2, y2, bar_w2, 28), border_radius=6)
        if len(drones) > 0:
            if (pygame.time.get_ticks() // 300) % 2 == 0:
                pygame.draw.rect(game_surface, PURPLE_LIGHTNING, (x2, y2, bar_w2, 28), border_radius=6)
        else:
            fill2 = int(bar_w2 * (max(0, megan.hp) / megan.max_hp))
            pygame.draw.rect(game_surface, MEGATRON_RED, (x2, y2, fill2, 28), border_radius=6)
        title_text = "УРОВЕНЬ 3 — ТАНК-МЕГАТРОН"
        if len(drones) > 0:
            title_text += " [НЕУЯЗВИМ]"
        title = font.render(title_text, True, WHITE)
        game_surface.blit(title, (WIDTH // 2 - title.get_width() // 2, y2 + 35))

        drone_text = small_font.render(f"Дронов: {len(drones)}/2", True, MEGA_DRONE_GREEN)
        game_surface.blit(drone_text, (WIDTH - 180, 65))

        wtext = small_font.render(f"Оружие: {WEAPON_NAMES[player.weapon]}", True, WEAPON_COLORS[player.weapon])
        game_surface.blit(wtext, (20, HEIGHT - 70))

        if slowmo_timer > 0:
            sm_text = big_font.render("SLOW-MO", True, YELLOW)
            alpha = int(255 * (slowmo_timer / 60))
            sm_surf = pygame.Surface((sm_text.get_width(), sm_text.get_height()), pygame.SRCALPHA)
            sm_surf.blit(sm_text, (0, 0))
            sm_surf.set_alpha(alpha)
            game_surface.blit(sm_surf, (WIDTH // 2 - sm_text.get_width() // 2, 80))

        if round_over:
            if won:
                draw_boss_victory(game_surface, 3)
            else:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 220))
                game_surface.blit(overlay, (0, 0))
                text = big_font.render("ТЫ ПРОИГРАЛ", True, RED)
                game_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))
                sub = mid_font.render("Мегатрон оказался сильнее...", True, WHITE)
                game_surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 300))
                hint = font.render("Enter — рестарт, Esc — в меню", True, YELLOW)
                game_surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))
        present()


def main():
    global vignette_surface
    load_all_music()
    create_vignette()
    if MENU_MUSIC:
        play_music(MENU_MUSIC, volume=0.4)
    selected = 0
    options_count = 3
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_music()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % options_count
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % options_count
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        stop_music()
                        r = boss_fight(level=1)
                        if r == "quit":
                            pygame.quit()
                            sys.exit()
                        if MENU_MUSIC:
                            play_music(MENU_MUSIC, volume=0.4)
                    elif selected == 1:
                        show = True
                        while show:
                            clock.tick(FPS)
                            for ev in pygame.event.get():
                                if ev.type == pygame.QUIT:
                                    stop_music()
                                    pygame.quit()
                                    sys.exit()
                                if ev.type == pygame.KEYDOWN:
                                    show = False
                            draw_controls(game_surface)
                            present()
                    elif selected == 2:
                        stop_music()
                        pygame.quit()
                        sys.exit()
        draw_menu(game_surface, selected)
        present()


if __name__ == "__main__":
    main()