
import pygame
import random
import math
import sys

WIDTH, HEIGHT = 540, 900
FPS = 60

pygame.init()
pygame.display.set_caption("Moose Shooter POC")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 24)
BIG = pygame.font.SysFont("consolas", 56, bold=True)
MID = pygame.font.SysFont("consolas", 34, bold=True)

BG = (10, 14, 24)
WHITE = (240, 240, 240)
RED = (230, 70, 70)
GREEN = (80, 220, 120)
YELLOW = (255, 220, 90)
BLUE = (100, 190, 255)
PURPLE = (180, 120, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (65, 65, 70)
BROWN = (130, 90, 45)

PLAYER_SPEED = 340
BULLET_SPEED = 620
ENEMY_BULLET_SPEED = 260

def clamp(v, a, b):
    return max(a, min(b, v))

class Bullet:
    def __init__(self, x, y, vy, friendly=True):
        self.rect = pygame.Rect(x - 4, y - 14, 8, 24)
        self.vy = vy
        self.friendly = friendly

    def update(self, dt):
        self.rect.y += int(self.vy * dt)

    def draw(self):
        color = GREEN if self.friendly else RED
        pygame.draw.rect(screen, color, self.rect, border_radius=4)

class Enemy:
    def __init__(self, x, y, kind, row, col):
        self.x = x
        self.y = y
        self.kind = kind
        self.row = row
        self.col = col
        self.w = 48
        self.h = 42
        self.hp = 1 if kind != "cart" else 2
        self.alive = True
        self.phase = random.random() * math.tau
        self.shoot_timer = random.uniform(1.5, 4.0)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w/2), int(self.y - self.h/2), self.w, self.h)

    def update(self, dt, t, wave):
        sway = math.sin(t * (1.2 + wave * .1) + self.phase) * (18 + 4*wave)
        self.x += sway * dt

        self.shoot_timer -= dt

    def maybe_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = random.uniform(1.8, 4.5)
            if random.random() < 0.42:
                return Bullet(self.x, self.y + 24, ENEMY_BULLET_SPEED, friendly=False)
        return None

    def draw(self):
        r = self.rect
        if self.kind == "alien":
            pygame.draw.ellipse(screen, PURPLE, r)
            pygame.draw.circle(screen, WHITE, (r.centerx, r.centery-4), 10)
            pygame.draw.circle(screen, (30,30,30), (r.centerx, r.centery-4), 5)
            pygame.draw.line(screen, PURPLE, (r.left+6, r.bottom), (r.left-6, r.bottom+12), 5)
            pygame.draw.line(screen, PURPLE, (r.right-6, r.bottom), (r.right+6, r.bottom+12), 5)
        elif self.kind == "chicken":
            pygame.draw.ellipse(screen, WHITE, r)
            pygame.draw.circle(screen, RED, (r.centerx+10, r.top+2), 7)
            pygame.draw.polygon(screen, YELLOW, [(r.right, r.centery), (r.right+12, r.centery+4), (r.right, r.centery+8)])
            pygame.draw.circle(screen, (25,25,25), (r.centerx+12, r.centery-6), 3)
            pygame.draw.line(screen, YELLOW, (r.centerx-8, r.bottom), (r.centerx-8, r.bottom+10), 3)
            pygame.draw.line(screen, YELLOW, (r.centerx+4, r.bottom), (r.centerx+4, r.bottom+10), 3)
        else:
            pygame.draw.rect(screen, DARK_GRAY, r, border_radius=5)
            pygame.draw.rect(screen, RED, (r.x+4, r.y+5, r.w-8, 7))
            pygame.draw.circle(screen, WHITE, (r.x+10, r.bottom+3), 5)
            pygame.draw.circle(screen, WHITE, (r.right-10, r.bottom+3), 5)

class CraigBoss:
    def __init__(self):
        self.x = WIDTH/2
        self.y = 170
        self.w = 250
        self.h = 150
        self.max_hp = 80
        self.hp = self.max_hp
        self.shoot_timer = 0.7
        self.move_dir = 1
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt):
        self.x += 90 * self.move_dir * dt
        if self.x < 150 or self.x > WIDTH-150:
            self.move_dir *= -1
        self.shoot_timer -= dt

    def maybe_shoot(self):
        shots = []
        if self.shoot_timer <= 0:
            self.shoot_timer = 0.55
            for dx in (-70, -35, 0, 35, 70):
                b = Bullet(self.x+dx, self.y+65, ENEMY_BULLET_SPEED+60, friendly=False)
                shots.append(b)
        return shots

    def draw(self):
        r = self.rect
        pygame.draw.rect(screen, (205, 194, 165), r, border_radius=12)
        pygame.draw.rect(screen, (110, 120, 100), (r.x+40, r.y+36, 95, 30), border_radius=4)
        pygame.draw.rect(screen, (80,80,80), (r.x+160, r.y+36, 42, 28), border_radius=3)
        pygame.draw.rect(screen, (35,35,35), (r.x+34, r.y+87, r.w-68, 25), border_radius=4)
        pygame.draw.rect(screen, WHITE, (r.centerx-65, r.bottom-12, 130, 70))
        pygame.draw.line(screen, (30,30,30), (r.x+58, r.y+20), (r.x+82, r.y+34), 6)
        pygame.draw.line(screen, (30,30,30), (r.right-58, r.y+20), (r.right-82, r.y+34), 6)
        label = MID.render("CRAIG", True, WHITE)
        screen.blit(label, (WIDTH/2-label.get_width()/2, 36))
        bar_x, bar_y, bar_w, bar_h = 70, 82, WIDTH-140, 22
        pygame.draw.rect(screen, (50,50,50), (bar_x, bar_y, bar_w, bar_h))
        fill = int(bar_w * max(0, self.hp)/self.max_hp)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, fill, bar_h))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)

class Player:
    def __init__(self):
        self.x = WIDTH/2
        self.y = HEIGHT-100
        self.w = 66
        self.h = 58
        self.cooldown = 0
        self.lives = 3
        self.invuln = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt, keys):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        self.x += dx * PLAYER_SPEED * dt
        self.x = clamp(self.x, 45, WIDTH-45)
        self.cooldown = max(0, self.cooldown-dt)
        self.invuln = max(0, self.invuln-dt)

    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = 0.18
            return Bullet(self.x, self.y-35, -BULLET_SPEED, friendly=True)
        return None

    def hit(self):
        if self.invuln <= 0:
            self.lives -= 1
            self.invuln = 1.2

    def draw(self):
        r = self.rect
        if self.invuln > 0 and int(self.invuln*10) % 2 == 0:
            return
        pygame.draw.ellipse(screen, BROWN, (r.x+12, r.y+10, r.w-24, r.h-8))
        pygame.draw.ellipse(screen, BROWN, (r.centerx-14, r.y-5, 28, 30))
        # antlers
        pygame.draw.line(screen, (205,175,120), (r.centerx-8, r.y+4), (r.centerx-28, r.y-18), 5)
        pygame.draw.line(screen, (205,175,120), (r.centerx+8, r.y+4), (r.centerx+28, r.y-18), 5)
        pygame.draw.line(screen, (205,175,120), (r.centerx-28, r.y-18), (r.centerx-38, r.y-28), 4)
        pygame.draw.line(screen, (205,175,120), (r.centerx+28, r.y-18), (r.centerx+38, r.y-28), 4)
        # cannon
        pygame.draw.rect(screen, (80,90,100), (r.centerx-8, r.y-20, 16, 34), border_radius=4)

def make_wave(kind, wave_num):
    enemies = []
    rows = 3
    cols = 6
    sx = 70
    sy = 140
    gapx = 72
    gapy = 68
    for row in range(rows):
        for col in range(cols):
            enemies.append(Enemy(sx + col*gapx, sy + row*gapy, kind, row, col))
    return enemies

def draw_stars(t):
    random.seed(42)
    for i in range(75):
        x = random.randrange(WIDTH)
        y = (random.randrange(HEIGHT) + int(t*18*(1+(i%4)*.25))) % HEIGHT
        c = 120 + (i % 3)*40
        pygame.draw.circle(screen, (c,c,c), (x,y), 1 + (i%7==0))

def centered(text, y, font=BIG, color=WHITE):
    surf = font.render(text, True, color)
    screen.blit(surf, (WIDTH/2-surf.get_width()/2, y))

def reset_game():
    return {
        "player": Player(),
        "bullets": [],
        "enemies": make_wave("alien", 1),
        "wave": 1,
        "score": 0,
        "state": "playing",
        "message_timer": 2.0,
        "boss_warning": 0,
        "boss": None,
        "paper_jam_timer": 0,
        "time": 0.0
    }

game = reset_game()

running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    game["time"] += dt
    t = game["time"]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game["state"] in ("gameover", "won"):
                game = reset_game()

    keys = pygame.key.get_pressed()

    if game["state"] == "playing":
        p = game["player"]
        p.update(dt, keys)

        if keys[pygame.K_SPACE]:
            b = p.shoot()
            if b:
                game["bullets"].append(b)

        for b in game["bullets"][:]:
            b.update(dt)
            if b.rect.bottom < -40 or b.rect.top > HEIGHT+40:
                game["bullets"].remove(b)

        # Normal enemy waves
        if game["boss"] is None and game["boss_warning"] <= 0:
            for e in game["enemies"]:
                e.update(dt, t, game["wave"])
                shot = e.maybe_shoot()
                if shot:
                    game["bullets"].append(shot)

            # player bullet vs enemies
            for b in game["bullets"][:]:
                if not b.friendly:
                    continue
                for e in game["enemies"]:
                    if e.alive and b.rect.colliderect(e.rect):
                        e.hp -= 1
                        if e.hp <= 0:
                            e.alive = False
                            game["score"] += 100
                        if b in game["bullets"]:
                            game["bullets"].remove(b)
                        break

            game["enemies"] = [e for e in game["enemies"] if e.alive]

            if not game["enemies"]:
                game["wave"] += 1
                game["message_timer"] = 1.6
                if game["wave"] == 2:
                    game["enemies"] = make_wave("chicken", 2)
                elif game["wave"] == 3:
                    game["enemies"] = make_wave("cart", 3)
                elif game["wave"] == 4:
                    game["boss_warning"] = 2.3

        elif game["boss_warning"] > 0:
            game["boss_warning"] -= dt
            if game["boss_warning"] <= 0:
                game["boss"] = CraigBoss()

        # Boss logic
        if game["boss"] is not None:
            boss = game["boss"]
            boss.update(dt)
            game["bullets"].extend(boss.maybe_shoot())

            for b in game["bullets"][:]:
                if b.friendly and b.rect.colliderect(boss.rect):
                    boss.hp -= 1
                    game["score"] += 20
                    if b in game["bullets"]:
                        game["bullets"].remove(b)
                    if boss.hp <= 0:
                        game["score"] += 500
                        game["paper_jam_timer"] = 3.0
                        game["state"] = "won"
                        break

        # enemy bullets vs player
        for b in game["bullets"][:]:
            if not b.friendly and b.rect.colliderect(game["player"].rect):
                game["player"].hit()
                if b in game["bullets"]:
                    game["bullets"].remove(b)

        if game["player"].lives <= 0:
            game["state"] = "gameover"

        game["message_timer"] = max(0, game["message_timer"]-dt)

    elif game["state"] == "won":
        game["paper_jam_timer"] = max(0, game["paper_jam_timer"]-dt)

    # DRAW
    screen.fill(BG)
    draw_stars(t)

    # world
    for e in game["enemies"]:
        e.draw()
    if game["boss"]:
        game["boss"].draw()

    for b in game["bullets"]:
        b.draw()
    game["player"].draw()

    # HUD
    score_s = FONT.render(f"SCORE {game['score']:,}", True, WHITE)
    screen.blit(score_s, (18, 18))
    lives_s = FONT.render("MOOSE " + "♥"*max(0, game["player"].lives), True, YELLOW)
    screen.blit(lives_s, (18, 48))

    if game["message_timer"] > 0 and game["wave"] <= 3:
        title = {1:"ALIEN INVADERS", 2:"CHICKEN ATTACK", 3:"SHOPPING CARTS?!"}.get(game["wave"], "")
        centered(title, HEIGHT//2-40, MID, WHITE)

    if game["boss_warning"] > 0:
        centered("⚠ BOSS INCOMING ⚠", HEIGHT//2-80, MID, RED)
        centered("WHY?", HEIGHT//2-30, FONT, WHITE)

    if game["state"] == "won":
        centered("PAPER JAM", HEIGHT//2-80, BIG, GREEN)
        centered("+500", HEIGHT//2-10, BIG, YELLOW)
        centered("CRAIG HAS BEEN DEFEATED", HEIGHT//2+70, FONT, WHITE)
        centered("PRESS R TO RESTART", HEIGHT//2+110, FONT, GRAY)

    if game["state"] == "gameover":
        centered("MOOSE DOWN", HEIGHT//2-80, BIG, RED)
        centered("PRESS R TO RESTART", HEIGHT//2, FONT, WHITE)

    if game["state"] == "playing":
        hint = FONT.render("A/D or ←/→  MOVE    SPACE  FIRE", True, GRAY)
        screen.blit(hint, (WIDTH/2-hint.get_width()/2, HEIGHT-34))

    pygame.display.flip()

pygame.quit()
sys.exit()
