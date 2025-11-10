import pygame, random, sys, time


pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 색상
WHITE = (255, 255, 255)

# 배경 이미지 로드 (초기에 한 번만)
background = pygame.image.load("./assets/background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# 스크롤용 변수
bg_y1 = 0
bg_y2 = -HEIGHT
bg_speed = 2  # 배경이 내려오는 속도

# 비행기 속도, 적 생성 주기, 코인 생성 주기 등
player_speed = 5
enemy_speed = 3
coin_speed = 3
spawn_delay = 30  # 프레임 단위

running = True
start_time = time.time()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./assets/player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-50))
        self.ammo = 10  # 현재 탄약
        self.max_ammo = 10  # 최대 탄약
        self.last_reload_time = time.time()  # 마지막 리로드 시각

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= player_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += player_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= player_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += player_speed

        # 총알 발사
        if keys[pygame.K_SPACE]:
            if self.ammo > 0:  # 🔸 탄약이 남아있을 때만 발사
                bullet = Bullet(self.rect.centerx, self.rect.top)
                bullet_group.add(bullet)
                self.ammo -= 1

        # 1초마다 탄약 자동 회복
        current_time = time.time()
        if current_time - self.last_reload_time >= 1:
            self.last_reload_time = current_time
            if self.ammo < self.max_ammo:
                self.ammo += 1

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./assets/enemy.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH-20), 0))
        self.hp = 3  # 🔹 적 체력 (3으로 설정)

    def update(self):
        self.rect.y += enemy_speed
        if self.rect.top > HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./assets/coin.png").convert_alpha()
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH-20), 0))

    def update(self):
        self.rect.y += coin_speed
        if self.rect.top > HEIGHT:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("./assets/bullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (25, 40))  # 총알 크기
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -8  # 위로 이동 (음수)

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()  # 화면 위로 나가면 제거

player = Player()
player_group = pygame.sprite.Group(player)
enemy_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

score = 0
frame_count = 0

while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

    # 배경 스크롤
    # 배경 스크롤 업데이트
    bg_y1 += bg_speed
    bg_y2 += bg_speed

    if bg_y1 >= HEIGHT:
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT

    # 배경 그리기 (두 장을 이어붙임)
    screen.blit(background, (0, bg_y1))
    screen.blit(background, (0, bg_y2))

    # 종료 이벤트
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 스폰 로직
    frame_count += 1
    if frame_count % 40 == 0:
        enemy_group.add(Enemy())
    if frame_count % 80 == 0:
        coin_group.add(Coin())

    # 업데이트
    player.update(keys)
    enemy_group.update()
    coin_group.update()
    bullet_group.update()

    # 총알이 적에 맞았는지 확인
    for bullet in bullet_group:
        hit_enemies = pygame.sprite.spritecollide(bullet, enemy_group, False)
        for enemy in hit_enemies:
            enemy.hp -= 1
            bullet.kill()
            if enemy.hp <= 0:
                enemy.kill()
                score += 50  # 적 처치 시 추가 점수

    # 충돌 감지
    if pygame.sprite.spritecollide(player, enemy_group, False):
        running = False  # 충돌 시 게임 종료

    coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
    score += len(coins_collected) * 10

    # 생존 시간 계산
    survival_time = time.time() - start_time

    # 화면 그리기
    player_group.draw(screen)
    enemy_group.draw(screen)
    coin_group.draw(screen)
    bullet_group.draw(screen)
    

    # 텍스트 표시
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    time_text = font.render(f"Time: {int(survival_time)}s", True, (0, 0, 0))
    ammo_text = font.render(f"총알: {player.ammo}/{player.max_ammo}", True, (0, 0, 0))

    screen.blit(ammo_text, (10, 90))
    screen.blit(score_text, (10, 10))
    screen.blit(time_text, (10, 50))



    pygame.display.flip()
    clock.tick(60)

