
import pygame
import random
import math
import sys

WIDTH, HEIGHT = 540, 900
FPS = 60

pygame.init()
pygame.display.set_caption("Moose Shooter - Fake Demo")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 22)
SMALL = pygame.font.SysFont("consolas", 16, bold=True)
MID = pygame.font.SysFont("consolas", 34, bold=True)
BIG = pygame.font.SysFont("consolas", 54, bold=True)
TITLE = pygame.font.SysFont("arialblack", 44)

BG_TOP = (5, 11, 25)
BG_BOTTOM = (8, 28, 46)
WHITE = (242, 245, 250)
RED = (238, 74, 74)
GREEN = (84, 242, 158)
CYAN = (77, 213, 255)
YELLOW = (255, 220, 91)
ORANGE = (255, 137, 57)
PURPLE = (175, 104, 255)
GRAY = (145, 155, 170)
DARK = (22, 28, 38)
BROWN = (139, 88, 43)
TAN = (221, 177, 104)

PLAYER_SPEED = 340
BULLET_SPEED = 690
ENEMY_BULLET_SPEED = 290

def clamp(v, a, b):
    return max(a, min(b, v))

def lerp(a, b, t):
    return int(a + (b-a)*t)

def draw_gradient(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = tuple(lerp(BG_TOP[i], BG_BOTTOM[i], t) for i in range(3))
        pygame.draw.line(surface, c, (0, y), (WIDTH, y))

def glow_circle(surface, pos, radius, color, strength=5):
    overlay = pygame.Surface((radius*4, radius*4), pygame.SRCALPHA)
    center = (radius*2, radius*2)
    for i in range(strength, 0, -1):
        rr = int(radius * (1 + i*0.45))
        alpha = max(10, int(48 / i))
        pygame.draw.circle(overlay, (*color, alpha), center, rr)
    pygame.draw.circle(overlay, color, center, radius)
    surface.blit(overlay, (pos[0]-center[0], pos[1]-center[1]))

class Particle:
    def __init__(self, x, y, color, speed=180):
        a = random.random() * math.tau
        s = random.uniform(speed*0.35, speed)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(a)*s, math.sin(a)*s
        self.life = random.uniform(.25, .65)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.vx *= .985
        self.vy *= .985
        self.life -= dt

    def draw(self, offset=(0,0)):
        if self.life <= 0:
            return
        alpha = self.life / self.max_life
        r = max(1, int(self.size*alpha))
        pygame.draw.circle(screen, self.color, (int(self.x+offset[0]), int(self.y+offset[1])), r)

class Bullet:
    def __init__(self, x, y, vy, friendly=True):
        self.x, self.y = x, y
        self.vy = vy
        self.friendly = friendly
        self.rect = pygame.Rect(x-5, y-15, 10, 30)

    def update(self, dt):
        self.y += self.vy*dt
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, offset=(0,0)):
        color = CYAN if self.friendly else ORANGE
        x, y = int(self.x+offset[0]), int(self.y+offset[1])
        glow_circle(screen, (x,y), 4, color, 4)
        pygame.draw.line(screen, WHITE, (x, y-9), (x, y+9), 2)

class Enemy:
    def __init__(self, x, y, kind, row, col):
        self.base_x = x
        self.x, self.y = x, y
        self.kind = kind
        self.row, self.col = row, col
        self.w, self.h = 52, 46
        self.hp = 1 if kind != "cart" else 2
        self.alive = True
        self.phase = random.random()*math.tau
        self.shoot_timer = random.uniform(1.4, 3.6)
        self.bob = random.random()*math.tau

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt, t, wave):
        self.x = self.base_x + math.sin(t*1.5 + self.phase) * (12+wave*3)
        self.y += math.sin(t*2.2+self.bob)*0.15
        self.shoot_timer -= dt

    def maybe_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = random.uniform(1.8, 4.1)
            if random.random() < .38:
                return Bullet(self.x, self.y+26, ENEMY_BULLET_SPEED, False)
        return None

    def draw(self, offset=(0,0)):
        r = self.rect.move(offset)
        ox, oy = r.centerx, r.centery
        if self.kind == "alien":
            pygame.draw.ellipse(screen, (55, 24, 84), r.inflate(8, 6))
            pygame.draw.ellipse(screen, PURPLE, r)
            pygame.draw.ellipse(screen, (74, 255, 133), (r.x+6, r.y+8, r.w-12, r.h-12))
            pygame.draw.circle(screen, WHITE, (ox, oy-3), 10)
            pygame.draw.circle(screen, (15,20,25), (ox, oy-3), 5)
            pygame.draw.circle(screen, CYAN, (ox-2, oy-5), 2)
            pygame.draw.circle(screen, ORANGE, (r.left+10, r.bottom-2), 4)
            pygame.draw.circle(screen, ORANGE, (r.right-10, r.bottom-2), 4)
        elif self.kind == "chicken":
            pygame.draw.ellipse(screen, (235,235,230), r)
            pygame.draw.circle(screen, WHITE, (ox+11, r.y+10), 12)
            pygame.draw.circle(screen, RED, (ox+9, r.y+1), 6)
            pygame.draw.polygon(screen, YELLOW, [(r.right-2, oy-1), (r.right+13, oy+4), (r.right-2, oy+9)])
            pygame.draw.circle(screen, (20,20,20), (ox+14, r.y+7), 3)
            pygame.draw.arc(screen, GRAY, (r.x+4,r.y+15,22,20), 0, math.pi, 3)
            pygame.draw.line(screen, YELLOW, (ox-7, r.bottom-4), (ox-7, r.bottom+8), 3)
            pygame.draw.line(screen, YELLOW, (ox+3, r.bottom-4), (ox+3, r.bottom+8), 3)
        else:
            body = pygame.Rect(r.x+5, r.y+9, r.w-10, r.h-14)
            pygame.draw.rect(screen, (64,72,82), body, border_radius=5)
            pygame.draw.line(screen, (190,200,210), (body.left+4,body.top+2), (body.right-3,body.top+2), 3)
            pygame.draw.rect(screen, RED, (body.x+3, body.y+3, body.w-6, 6), border_radius=2)
            pygame.draw.line(screen, (190,200,210), (body.left+8, body.top+8), (body.left+3, r.y), 3)
            pygame.draw.circle(screen, (30,30,30), (body.left+8, body.bottom+3), 5)
            pygame.draw.circle(screen, (30,30,30), (body.right-8, body.bottom+3), 5)
            glow_circle(screen, (ox, r.bottom+5), 3, ORANGE, 3)

class CraigBoss:
    def __init__(self):
        self.x, self.y = WIDTH/2, 165
        self.w, self.h = 260, 156
        self.max_hp, self.hp = 90, 90
        self.shoot_timer = .6
        self.move_dir = 1

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt):
        self.x += 88*self.move_dir*dt
        if self.x < 150 or self.x > WIDTH-150:
            self.move_dir *= -1
        self.shoot_timer -= dt

    def maybe_shoot(self):
        shots=[]
        if self.shoot_timer <= 0:
            self.shoot_timer = .5
            for dx in (-72,-36,0,36,72):
                shots.append(Bullet(self.x+dx, self.y+68, ENEMY_BULLET_SPEED+55, False))
        return shots

    def draw(self, offset=(0,0)):
        r = self.rect.move(offset)
        pygame.draw.rect(screen, (40,31,25), r.inflate(10,10), border_radius=18)
        pygame.draw.rect(screen, (211,196,158), r, border_radius=14)
        pygame.draw.rect(screen, (123,118,100), (r.x+18,r.y+18,r.w-36,16), border_radius=4)
        pygame.draw.rect(screen, (37,44,49), (r.x+36,r.y+49,r.w-72,46), border_radius=8)
        pygame.draw.polygon(screen, CYAN, [(r.x+65,r.y+64),(r.x+98,r.y+60),(r.x+82,r.y+76)])
        pygame.draw.polygon(screen, CYAN, [(r.right-65,r.y+64),(r.right-98,r.y+60),(r.right-82,r.y+76)])
        pygame.draw.rect(screen, (50,50,50), (r.centerx-73,r.y+101,146,20), border_radius=4)
        pygame.draw.rect(screen, WHITE, (r.centerx-62,r.y+116,124,55))
        pygame.draw.line(screen, (180,180,180), (r.centerx-48,r.y+132), (r.centerx+48,r.y+132), 2)
        pygame.draw.line(screen, (180,180,180), (r.centerx-48,r.y+143), (r.centerx+32,r.y+143), 2)

class Player:
    def __init__(self):
        self.x, self.y = WIDTH/2, HEIGHT-110
        self.w, self.h = 86, 84
        self.cooldown = 0
        self.lives = 3
        self.invuln = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt, keys):
        dx = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0) - (1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        self.x = clamp(self.x + dx*PLAYER_SPEED*dt, 55, WIDTH-55)
        self.cooldown = max(0, self.cooldown-dt)
        self.invuln = max(0, self.invuln-dt)

    def shoot(self):
        if self.cooldown <= 0:
            self.cooldown = .16
            return Bullet(self.x, self.y-48, -BULLET_SPEED, True)

    def hit(self):
        if self.invuln <= 0:
            self.lives -= 1
            self.invuln = 1.15

    def draw(self, offset=(0,0)):
        if self.invuln > 0 and int(self.invuln*12)%2 == 0:
            return
        x, y = int(self.x+offset[0]), int(self.y+offset[1])
        pygame.draw.ellipse(screen, (0,0,0), (x-34,y+29,68,18))
        pygame.draw.ellipse(screen, (121,62,34), (x-26,y-3,52,62))
        pygame.draw.rect(screen, (143,32,32), (x-25,y+12,50,27), border_radius=8)
        for xx in (x-13,x+4):
            pygame.draw.line(screen, (36,30,30), (xx,y+13), (xx,y+39), 3)
        pygame.draw.line(screen, (36,30,30), (x-24,y+25), (x+24,y+25), 3)
        pygame.draw.ellipse(screen, BROWN, (x-20,y-28,40,44))
        pygame.draw.ellipse(screen, (170,105,55), (x-16,y-2,32,18))
        pygame.draw.ellipse(screen, BROWN, (x-34,y-19,18,10))
        pygame.draw.ellipse(screen, BROWN, (x+16,y-19,18,10))
        for side in (-1,1):
            base=(x+side*13,y-20)
            pts=[base,(x+side*29,y-40),(x+side*41,y-53)]
            pygame.draw.lines(screen,TAN,False,pts,6)
            pygame.draw.line(screen,TAN,(x+side*29,y-40),(x+side*22,y-54),5)
            pygame.draw.line(screen,TAN,(x+side*37,y-49),(x+side*34,y-63),5)
        pygame.draw.rect(screen,(61,73,85),(x-18,y+18,36,28),border_radius=6)
        pygame.draw.rect(screen,(112,132,146),(x-14,y+21,8,22),border_radius=3)
        pygame.draw.rect(screen,(112,132,146),(x+6,y+21,8,22),border_radius=3)
        glow_circle(screen,(x-10,y+43),3,ORANGE,2)
        glow_circle(screen,(x+10,y+43),3,ORANGE,2)
        pygame.draw.rect(screen,(55,72,84),(x+25,y-12,13,38),border_radius=5)
        pygame.draw.rect(screen,(97,117,129),(x+22,y-19,19,18),border_radius=5)
        glow_circle(screen,(x+31,y-13),3,CYAN,2)

def make_wave(kind):
    enemies=[]
    sx, sy, gapx, gapy = 70, 155, 78, 68
    for row in range(3):
        for col in range(6):
            enemies.append(Enemy(sx+col*gapx, sy+row*gapy, kind, row, col))
    return enemies

def add_explosion(game, x, y, color=ORANGE, count=18):
    for _ in range(count):
        game["particles"].append(Particle(x,y,color,random.uniform(110,240)))
    game["shake"] = max(game["shake"], .14)

def draw_stars(t):
    random.seed(42)
    for i in range(90):
        x = random.randrange(WIDTH)
        y = (random.randrange(HEIGHT) + int(t*(16+(i%5)*5))) % HEIGHT
        c = 120+(i%3)*45
        pygame.draw.circle(screen,(c,c,c),(x,y),1+(i%11==0))
    pts=[(0,720),(65,630),(118,690),(185,610),(245,690),(330,600),(410,684),(475,620),(540,700),(540,900),(0,900)]
    pygame.draw.polygon(screen,(7,20,31),pts)

def panel(rect, title, value=None):
    pygame.draw.rect(screen,(9,13,20),rect,border_radius=10)
    pygame.draw.rect(screen,(70,82,98),rect,2,border_radius=10)
    if title:
        screen.blit(SMALL.render(title,True,GRAY),(rect.x+10,rect.y+7))
    if value is not None:
        screen.blit(MID.render(value,True,WHITE),(rect.x+10,rect.y+25))

def centered(text,y,font=BIG,color=WHITE):
    s=font.render(text,True,color)
    screen.blit(s,(WIDTH//2-s.get_width()//2,y))

def reset_game():
    return {
        "player":Player(),
        "bullets":[],
        "enemies":make_wave("alien"),
        "wave":1,
        "score":0,
        "state":"playing",
        "message_timer":2.0,
        "boss_warning":0.0,
        "boss":None,
        "time":0.0,
        "particles":[],
        "shake":0.0,
    }

game=reset_game()
running=True

while running:
    dt=clock.tick(FPS)/1000.0
    game["time"]+=dt
    t=game["time"]

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:
                running=False
            if event.key==pygame.K_r and game["state"] in ("gameover","won"):
                game=reset_game()

    keys=pygame.key.get_pressed()

    if game["state"]=="playing":
        p=game["player"]
        p.update(dt,keys)
        if keys[pygame.K_SPACE]:
            b=p.shoot()
            if b: game["bullets"].append(b)

        for b in game["bullets"][:]:
            b.update(dt)
            if b.rect.bottom<-40 or b.rect.top>HEIGHT+40:
                game["bullets"].remove(b)

        if game["boss"] is None and game["boss_warning"]<=0:
            for e in game["enemies"]:
                e.update(dt,t,game["wave"])
                shot=e.maybe_shoot()
                if shot: game["bullets"].append(shot)

            for b in game["bullets"][:]:
                if not b.friendly: continue
                for e in game["enemies"]:
                    if e.alive and b.rect.colliderect(e.rect):
                        e.hp-=1
                        add_explosion(game,e.x,e.y,ORANGE,8)
                        if e.hp<=0:
                            e.alive=False
                            game["score"]+=100
                            add_explosion(game,e.x,e.y,YELLOW,18)
                        if b in game["bullets"]: game["bullets"].remove(b)
                        break

            game["enemies"]=[e for e in game["enemies"] if e.alive]
            if not game["enemies"]:
                game["wave"]+=1
                game["message_timer"]=1.75
                if game["wave"]==2:
                    game["enemies"]=make_wave("chicken")
                elif game["wave"]==3:
                    game["enemies"]=make_wave("cart")
                elif game["wave"]==4:
                    game["boss_warning"]=2.35

        elif game["boss_warning"]>0:
            game["boss_warning"]-=dt
            game["shake"]=max(game["shake"],.05)
            if game["boss_warning"]<=0:
                game["boss"]=CraigBoss()

        if game["boss"]:
            boss=game["boss"]
            boss.update(dt)
            game["bullets"].extend(boss.maybe_shoot())
            for b in game["bullets"][:]:
                if b.friendly and b.rect.colliderect(boss.rect):
                    boss.hp-=1
                    game["score"]+=20
                    add_explosion(game,b.x,b.y,CYAN,7)
                    if b in game["bullets"]: game["bullets"].remove(b)
                    if boss.hp<=0:
                        game["score"]+=500
                        add_explosion(game,boss.x,boss.y,YELLOW,80)
                        game["state"]="won"
                        break

        for b in game["bullets"][:]:
            if not b.friendly and b.rect.colliderect(game["player"].rect):
                game["player"].hit()
                add_explosion(game,game["player"].x,game["player"].y,RED,24)
                if b in game["bullets"]: game["bullets"].remove(b)

        if game["player"].lives<=0:
            game["state"]="gameover"

        game["message_timer"]=max(0,game["message_timer"]-dt)

    for p in game["particles"][:]:
        p.update(dt)
        if p.life<=0: game["particles"].remove(p)

    game["shake"]=max(0,game["shake"]-dt)
    shake_mag=6 if game["shake"]>0 else 0
    offset=(random.randint(-shake_mag,shake_mag),random.randint(-shake_mag,shake_mag)) if shake_mag else (0,0)

    draw_gradient(screen)
    draw_stars(t)

    for e in game["enemies"]:
        e.draw(offset)
    if game["boss"]:
        game["boss"].draw(offset)
    for b in game["bullets"]:
        b.draw(offset)
    for p in game["particles"]:
        p.draw(offset)
    game["player"].draw(offset)

    panel(pygame.Rect(14,14,170,66),"SCORE",f"{game['score']:,}")
    panel(pygame.Rect(WIDTH-184,14,170,66),"WAVE",str(min(game["wave"],4)))
    heart_text="♥"*max(0,game["player"].lives)
    hs=MID.render(heart_text,True,RED)
    screen.blit(hs,(18,88))

    if game["message_timer"]>0 and game["wave"]<=3:
        title={1:"ALIEN INVADERS",2:"CHICKEN ATTACK",3:"SHOPPING CARTS?!"}[game["wave"]]
        centered(title,HEIGHT//2-50,MID,WHITE)

    if game["boss_warning"]>0:
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        pulse=int(45+35*(.5+.5*math.sin(t*10)))
        overlay.fill((120,0,0,pulse))
        screen.blit(overlay,(0,0))
        centered("BOSS INCOMING",HEIGHT//2-90,BIG,RED)
        centered("THIS SEEMS UNNECESSARY",HEIGHT//2-25,SMALL,WHITE)

    if game["boss"]:
        centered("CRAIG",95,MID,WHITE)
        bar=pygame.Rect(65,132,WIDTH-130,20)
        pygame.draw.rect(screen,(37,37,42),bar,border_radius=7)
        fill=int(bar.w*max(0,game["boss"].hp)/game["boss"].max_hp)
        pygame.draw.rect(screen,RED,(bar.x,bar.y,fill,bar.h),border_radius=7)
        pygame.draw.rect(screen,WHITE,bar,2,border_radius=7)

    if game["state"]=="won":
        centered("PAPER JAM!",HEIGHT//2-105,BIG,YELLOW)
        centered("+500",HEIGHT//2-40,BIG,GREEN)
        centered("CRAIG HAS BEEN DEFEATED",HEIGHT//2+35,SMALL,WHITE)
        centered("PRESS R TO RESTART",HEIGHT//2+70,SMALL,GRAY)

    if game["state"]=="gameover":
        centered("MOOSE DOWN",HEIGHT//2-70,BIG,RED)
        centered("PRESS R TO RESTART",HEIGHT//2+5,SMALL,WHITE)

    if game["state"]=="playing":
        hint=SMALL.render("A/D or ←/→ MOVE   SPACE FIRE   ESC QUIT",True,GRAY)
        screen.blit(hint,(WIDTH//2-hint.get_width()//2,HEIGHT-27))

    pygame.display.flip()

pygame.quit()
sys.exit()
