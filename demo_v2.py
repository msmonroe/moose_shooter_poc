import math
import random
import sys
import pygame

from player_sprite import load_player_sprite

WIDTH, HEIGHT = 540, 900
FPS = 60

pygame.init()
pygame.display.set_caption("Moose Shooter - Validation Demo")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 21, bold=True)
SMALL = pygame.font.SysFont("consolas", 15, bold=True)
MID = pygame.font.SysFont("consolas", 33, bold=True)
BIG = pygame.font.SysFont("arialblack", 48)
LOGO = pygame.font.SysFont("arialblack", 36)

WHITE = (244, 247, 252)
RED = (244, 72, 72)
CYAN = (68, 217, 255)
GREEN = (93, 246, 149)
YELLOW = (255, 219, 80)
ORANGE = (255, 133, 48)
PURPLE = (186, 97, 255)
GRAY = (142, 155, 175)

PLAYER_SPEED = 350
BULLET_SPEED = 720
ENEMY_BULLET_SPEED = 300

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def glow(surface, x, y, radius, color, rings=4):
    layer = pygame.Surface((radius * 8, radius * 8), pygame.SRCALPHA)
    cx = cy = radius * 4
    for n in range(rings, 0, -1):
        rr = radius + n * radius
        pygame.draw.circle(layer, (*color, max(8, 35 // n)), (cx, cy), rr)
    pygame.draw.circle(layer, color, (cx, cy), radius)
    surface.blit(layer, (x-cx, y-cy))

def draw_background(t):
    for y in range(HEIGHT):
        k = y / HEIGHT
        c = (int(4 + 6*k), int(9 + 23*k), int(22 + 31*k))
        pygame.draw.line(screen, c, (0, y), (WIDTH, y))
    random.seed(73)
    for i in range(110):
        x = random.randrange(WIDTH)
        y = (random.randrange(HEIGHT) + int(t * (11 + (i % 5) * 6))) % HEIGHT
        b = 120 + (i % 4)*32
        pygame.draw.circle(screen, (b,b,b), (x,y), 1 + (i % 17 == 0))
    pygame.draw.circle(screen, (183, 212, 238), (445, 128), 38)
    pygame.draw.circle(screen, (215, 230, 244), (435, 117), 28)
    far = [(0,690),(65,610),(120,675),(185,575),(260,680),(335,590),(405,670),(470,600),(540,680),(540,900),(0,900)]
    near = [(0,760),(85,665),(145,735),(230,640),(315,742),(390,655),(455,730),(540,650),(540,900),(0,900)]
    pygame.draw.polygon(screen, (7,21,34), far)
    pygame.draw.polygon(screen, (5,16,25), near)
    for x in range(-20, 580, 44):
        base = 810 + (x % 3)*13
        h = 85 + (x*7 % 40)
        pygame.draw.rect(screen, (4,16,20), (x+19, base-h//3, 5, h//2))
        for j in range(3):
            yy = base-h+j*22
            pygame.draw.polygon(screen, (5,27,29), [(x+21,yy),(x-2,yy+42),(x+44,yy+42)])

class Particle:
    def __init__(self, x, y, color, speed=210):
        ang = random.random() * math.tau
        s = random.uniform(speed*.35, speed)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(ang)*s, math.sin(ang)*s
        self.life = random.uniform(.25,.7)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2,5)

    def update(self, dt):
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.vx *= .985
        self.vy *= .985
        self.life -= dt

    def draw(self, offset):
        if self.life <= 0:
            return
        r = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(screen, self.color, (int(self.x+offset[0]), int(self.y+offset[1])), r)

class Bullet:
    def __init__(self, x, y, vy, friendly=True, spread=0):
        self.x, self.y = x, y
        self.vx = spread
        self.vy = vy
        self.friendly = friendly
        self.rect = pygame.Rect(0,0,10,28)

    def update(self, dt):
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, offset):
        x = int(self.x + offset[0])
        y = int(self.y + offset[1])
        color = CYAN if self.friendly else ORANGE
        glow(screen, x, y, 4, color, 3)
        pygame.draw.line(screen, WHITE, (x,y-10), (x,y+9), 2)

class Enemy:
    def __init__(self, x, y, kind, row, col):
        self.base_x = x
        self.x, self.y = x, y
        self.kind = kind
        self.row, self.col = row, col
        self.phase = random.random()*math.tau
        self.bob = random.random()*math.tau
        self.hp = 2 if kind == "cart" else 1
        self.shoot_timer = random.uniform(1.4,4.0)
        self.w, self.h = 54, 48

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt, t, wave):
        self.x = self.base_x + math.sin(t*1.45+self.phase)*(12+wave*3)
        self.y += math.sin(t*2.5+self.bob)*.18
        self.shoot_timer -= dt

    def maybe_shoot(self):
        if self.shoot_timer <= 0:
            self.shoot_timer = random.uniform(1.8,4.3)
            if random.random() < .42:
                return Bullet(self.x, self.y+28, ENEMY_BULLET_SPEED, False)
        return None

    def draw(self, offset):
        r = self.rect.move(offset)
        ox, oy = r.center
        if self.kind == "alien":
            glow(screen, ox, r.bottom+1, 3, PURPLE, 2)
            pygame.draw.ellipse(screen, (78,30,110), r.inflate(8,4))
            pygame.draw.ellipse(screen, PURPLE, r)
            pygame.draw.ellipse(screen, (70,245,128), (r.x+7,r.y+8,r.w-14,r.h-14))
            pygame.draw.circle(screen, WHITE, (ox,oy-3), 10)
            pygame.draw.circle(screen, (14,20,25), (ox,oy-3), 5)
            pygame.draw.circle(screen, CYAN, (ox-2,oy-5), 2)
            pygame.draw.circle(screen, ORANGE, (r.left+11,r.bottom-1), 4)
            pygame.draw.circle(screen, ORANGE, (r.right-11,r.bottom-1), 4)
        elif self.kind == "chicken":
            pygame.draw.ellipse(screen, (240,238,229), r)
            pygame.draw.circle(screen, WHITE, (ox+12,r.y+10), 12)
            pygame.draw.circle(screen, RED, (ox+9,r.y), 6)
            pygame.draw.polygon(screen, YELLOW, [(r.right-1,oy-2),(r.right+13,oy+4),(r.right-1,oy+9)])
            pygame.draw.circle(screen, (20,20,20), (ox+15,r.y+7), 3)
            pygame.draw.arc(screen, (165,165,170), (r.x+4,r.y+15,24,20), 0, math.pi, 3)
            pygame.draw.line(screen, YELLOW, (ox-7,r.bottom-4),(ox-7,r.bottom+8),3)
            pygame.draw.line(screen, YELLOW, (ox+3,r.bottom-4),(ox+3,r.bottom+8),3)
        else:
            body = pygame.Rect(r.x+5,r.y+9,r.w-10,r.h-14)
            pygame.draw.rect(screen, (65,74,86), body, border_radius=5)
            pygame.draw.rect(screen, RED, (body.x+4,body.y+3,body.w-8,6), border_radius=2)
            pygame.draw.line(screen, (200,208,216), (body.left+7,body.top+1),(body.right-4,body.top+1),3)
            pygame.draw.line(screen, (190,200,210), (body.left+9,body.top+8),(body.left+3,r.y),3)
            pygame.draw.circle(screen, (22,24,28), (body.left+9,body.bottom+3),5)
            pygame.draw.circle(screen, (22,24,28), (body.right-9,body.bottom+3),5)
            glow(screen, ox, r.bottom+6, 3, ORANGE, 2)

class Craig:
    def __init__(self):
        self.x, self.y = WIDTH/2, 170
        self.w, self.h = 268, 162
        self.max_hp = self.hp = 90
        self.dir = 1
        self.shoot_timer = .55

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt):
        self.x += 90*self.dir*dt
        if self.x < 150 or self.x > WIDTH-150:
            self.dir *= -1
        self.shoot_timer -= dt

    def maybe_shoot(self):
        if self.shoot_timer > 0:
            return []
        self.shoot_timer = .48
        return [Bullet(self.x+dx,self.y+73,ENEMY_BULLET_SPEED+55,False,dx*.35) for dx in (-70,-35,0,35,70)]

    def draw(self, offset):
        r = self.rect.move(offset)
        pygame.draw.rect(screen, (41,29,23), r.inflate(12,12), border_radius=20)
        pygame.draw.rect(screen, (213,198,162), r, border_radius=15)
        pygame.draw.rect(screen, (120,113,96), (r.x+18,r.y+18,r.w-36,16), border_radius=4)
        pygame.draw.rect(screen, (32,40,47), (r.x+34,r.y+48,r.w-68,50), border_radius=8)
        pygame.draw.polygon(screen, CYAN, [(r.x+66,r.y+63),(r.x+103,r.y+59),(r.x+82,r.y+80)])
        pygame.draw.polygon(screen, CYAN, [(r.right-66,r.y+63),(r.right-103,r.y+59),(r.right-82,r.y+80)])
        pygame.draw.rect(screen, (47,47,48), (r.centerx-75,r.y+104,150,22), border_radius=4)
        pygame.draw.rect(screen, WHITE, (r.centerx-63,r.y+119,126,59))
        for yy in (135,147,159):
            pygame.draw.line(screen,(180,180,180),(r.centerx-48,yy),(r.centerx+45,yy),2)
        for side in (-1,1):
            sx = r.centerx + side*(r.w//2+7)
            pygame.draw.line(screen,(64,67,70),(sx,r.y+55),(sx+side*36,r.y+82),11)
            glow(screen, sx+side*36, r.y+84, 5, ORANGE, 3)

class Player:
    def __init__(self):
        self.x, self.y = WIDTH/2, HEIGHT-116
        self.sprite = load_player_sprite(126)
        self.w, self.h = 82, 100
        self.cooldown = 0
        self.lives = 3
        self.invuln = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def update(self, dt, keys):
        dx = (1 if keys[pygame.K_RIGHT] or keys[pygame.K_d] else 0) - (1 if keys[pygame.K_LEFT] or keys[pygame.K_a] else 0)
        self.x = clamp(self.x + dx*PLAYER_SPEED*dt, 72, WIDTH-72)
        self.cooldown = max(0,self.cooldown-dt)
        self.invuln = max(0,self.invuln-dt)

    def shoot(self):
        if self.cooldown > 0:
            return []
        self.cooldown = .16
        return [Bullet(self.x-22,self.y-66,-BULLET_SPEED,True), Bullet(self.x+22,self.y-66,-BULLET_SPEED,True)]

    def hit(self):
        if self.invuln <= 0:
            self.lives -= 1
            self.invuln = 1.2
            return True
        return False

    def draw(self, offset):
        if self.invuln > 0 and int(self.invuln*12)%2 == 0:
            return
        x = int(self.x + offset[0])
        y = int(self.y + offset[1])
        pygame.draw.ellipse(screen, (0,0,0), (x-46,y+55,92,18))
        glow(screen, x-22, y-65, 4, CYAN, 3)
        glow(screen, x+22, y-65, 4, CYAN, 3)
        rect = self.sprite.get_rect(center=(x,y))
        screen.blit(self.sprite, rect)

def make_wave(kind):
    return [Enemy(70+col*79,160+row*69,kind,row,col) for row in range(3) for col in range(6)]

def add_burst(game,x,y,color=ORANGE,count=18):
    for _ in range(count):
        game["particles"].append(Particle(x,y,color,random.uniform(110,250)))
    game["shake"] = max(game["shake"], .13)

def panel(rect,title,value):
    pygame.draw.rect(screen,(7,12,19),rect,border_radius=10)
    pygame.draw.rect(screen,(70,86,105),rect,2,border_radius=10)
    screen.blit(SMALL.render(title,True,GRAY),(rect.x+10,rect.y+6))
    screen.blit(MID.render(value,True,WHITE),(rect.x+10,rect.y+24))

def centered(text,y,font,color):
    s=font.render(text,True,color)
    screen.blit(s,(WIDTH//2-s.get_width()//2,y))

def reset_game():
    return {"player":Player(),"bullets":[],"particles":[],"enemies":make_wave("alien"),"wave":1,"score":0,"state":"playing","message":2.0,"boss_warning":0.0,"boss":None,"shake":0.0,"time":0.0}

game=reset_game()
running=True
while running:
    dt=clock.tick(FPS)/1000.0
    game["time"] += dt
    t=game["time"]
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running=False
            if event.key == pygame.K_r and game["state"] in ("won","gameover"): game=reset_game()
    keys=pygame.key.get_pressed()
    if game["state"]=="playing":
        p=game["player"]
        p.update(dt,keys)
        if keys[pygame.K_SPACE]: game["bullets"].extend(p.shoot())
        for b in game["bullets"][:]:
            b.update(dt)
            if b.rect.bottom < -50 or b.rect.top > HEIGHT+50: game["bullets"].remove(b)
        if game["boss"] is None and game["boss_warning"] <= 0:
            for e in game["enemies"]:
                e.update(dt,t,game["wave"])
                shot=e.maybe_shoot()
                if shot: game["bullets"].append(shot)
            for b in game["bullets"][:]:
                if not b.friendly: continue
                for e in game["enemies"][:]:
                    if b.rect.colliderect(e.rect):
                        e.hp -= 1
                        add_burst(game,e.x,e.y,CYAN,7)
                        if e.hp <= 0:
                            game["score"] += 100
                            add_burst(game,e.x,e.y,YELLOW,20)
                            game["enemies"].remove(e)
                        if b in game["bullets"]: game["bullets"].remove(b)
                        break
            if not game["enemies"]:
                game["wave"] += 1
                game["message"]=1.7
                if game["wave"]==2: game["enemies"]=make_wave("chicken")
                elif game["wave"]==3: game["enemies"]=make_wave("cart")
                else: game["boss_warning"]=2.5
        elif game["boss_warning"] > 0:
            game["boss_warning"] -= dt
            game["shake"]=max(game["shake"],.05)
            if game["boss_warning"] <= 0: game["boss"]=Craig()
        if game["boss"]:
            boss=game["boss"]
            boss.update(dt)
            game["bullets"].extend(boss.maybe_shoot())
            for b in game["bullets"][:]:
                if b.friendly and b.rect.colliderect(boss.rect):
                    boss.hp -= 1
                    game["score"] += 20
                    add_burst(game,b.x,b.y,CYAN,6)
                    if b in game["bullets"]: game["bullets"].remove(b)
                    if boss.hp <= 0:
                        game["score"] += 500
                        add_burst(game,boss.x,boss.y,YELLOW,95)
                        game["state"]="won"
                        break
        for b in game["bullets"][:]:
            if not b.friendly and b.rect.colliderect(game["player"].rect):
                if game["player"].hit(): add_burst(game,game["player"].x,game["player"].y,RED,28)
                if b in game["bullets"]: game["bullets"].remove(b)
        if game["player"].lives <= 0: game["state"]="gameover"
        game["message"]=max(0,game["message"]-dt)
    for p in game["particles"][:]:
        p.update(dt)
        if p.life <= 0: game["particles"].remove(p)
    game["shake"]=max(0,game["shake"]-dt)
    mag=7 if game["shake"]>0 else 0
    offset=(random.randint(-mag,mag),random.randint(-mag,mag)) if mag else (0,0)
    draw_background(t)
    logo=LOGO.render("MOOSE SHOOTER",True,YELLOW)
    screen.blit(logo,(WIDTH//2-logo.get_width()//2,18))
    screen.blit(SMALL.render("TOTALLY NORMAL FOREST DEFENSE",True,CYAN),(WIDTH//2-112,58))
    for e in game["enemies"]: e.draw(offset)
    if game["boss"]: game["boss"].draw(offset)
    for b in game["bullets"]: b.draw(offset)
    for p in game["particles"]: p.draw(offset)
    game["player"].draw(offset)
    panel(pygame.Rect(14,86,154,62),"SCORE",f"{game['score']:,}")
    panel(pygame.Rect(WIDTH-168,86,154,62),"WAVE",str(min(game["wave"],4)))
    screen.blit(MID.render("♥"*max(0,game["player"].lives),True,RED),(18,157))
    if game["message"]>0 and game["wave"]<=3:
        centered({1:"ALIEN INVADERS",2:"CHICKEN ATTACK",3:"SHOPPING CARTS?!"}[game["wave"]],HEIGHT//2-52,MID,WHITE)
    if game["boss_warning"]>0:
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((130,0,0,int(42+32*(.5+.5*math.sin(t*11)))))
        screen.blit(ov,(0,0))
        centered("BOSS INCOMING",HEIGHT//2-92,BIG,RED)
        centered("WHY IS IT A PRINTER?",HEIGHT//2-22,FONT,WHITE)
    if game["boss"]:
        centered("CRAIG THE PRINTER",153,MID,WHITE)
        bar=pygame.Rect(62,195,WIDTH-124,21)
        pygame.draw.rect(screen,(36,36,42),bar,border_radius=7)
        fill=int(bar.w*max(0,game["boss"].hp)/game["boss"].max_hp)
        pygame.draw.rect(screen,RED,(bar.x,bar.y,fill,bar.h),border_radius=7)
        pygame.draw.rect(screen,WHITE,bar,2,border_radius=7)
    if game["state"]=="won":
        centered("PAPER JAM!",HEIGHT//2-110,BIG,YELLOW)
        centered("+500",HEIGHT//2-48,BIG,GREEN)
        centered("CRAIG HAS BEEN DEFEATED",HEIGHT//2+28,FONT,WHITE)
        centered("PRESS R TO RESTART",HEIGHT//2+64,SMALL,GRAY)
    if game["state"]=="gameover":
        centered("MOOSE DOWN",HEIGHT//2-75,BIG,RED)
        centered("PRESS R TO RESTART",HEIGHT//2+2,FONT,WHITE)
    if game["state"]=="playing":
        hint=SMALL.render("A/D or arrows MOVE   SPACE FIRE   ESC QUIT",True,GRAY)
        screen.blit(hint,(WIDTH//2-hint.get_width()//2,HEIGHT-26))
    pygame.display.flip()
pygame.quit()
sys.exit()
