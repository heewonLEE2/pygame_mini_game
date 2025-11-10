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
        self.ammo = 10
        self.max_ammo = 10
        self.last_reload_time = time.time()
        self.shoot_cooldown = 0.2   # 🔫 연속 발사 최소 간격(초)
        self.last_shot_time = 0
        self.shooting = False       # 키 입력 상태 추적

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= player_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += player_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= player_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += player_speed

        # 총알 발사 (단발 모드)
        current_time = time.time()
        if keys[pygame.K_SPACE]:
            if not self.shooting and self.ammo > 0 and current_time - self.last_shot_time >= self.shoot_cooldown:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                bullet_group.add(bullet)
                self.ammo -= 1
                self.last_shot_time = current_time
                self.shooting = True  # 🔸 한 번 눌렀을 때만 발사
        else:
            self.shooting = False  # 키에서 손을 떼면 다시 발사 가능

        # 1초마다 탄약 자동 회복
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

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("./assets/explosion.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))  # 폭발 크기
        self.rect = self.image.get_rect(center=(x, y))
        self.start_time = time.time()
        self.duration = 0.4  # 폭발 지속 시간(초)

    def update(self):
        # 일정 시간 후 자동 제거
        if time.time() - self.start_time > self.duration:
            self.kill()

player = Player()
player_group = pygame.sprite.Group(player)
enemy_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

score = 0
frame_count = 0

running = True
game_over = False

while running:
    screen.fill(WHITE)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # ============ 게임 진행 중 ============
        # 배경 스크롤
        bg_y1 += bg_speed
        bg_y2 += bg_speed
        if bg_y1 >= HEIGHT:
            bg_y1 = -HEIGHT
        if bg_y2 >= HEIGHT:
            bg_y2 = -HEIGHT
        screen.blit(background, (0, bg_y1))
        screen.blit(background, (0, bg_y2))

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
        explosion_group.update()

        # 총알 충돌
        for bullet in bullet_group:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemy_group, False)
            for enemy in hit_enemies:
                enemy.hp -= 1
                bullet.kill()
                if enemy.hp <= 0:
                    # 폭발 효과 생성
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    explosion_group.add(explosion)

                    enemy.kill()
                    score += 50

        # 충돌 감지 → 게임오버로 전환
        if pygame.sprite.spritecollide(player, enemy_group, False):
            game_over = True
            end_time = time.time()
            survival_time = end_time - start_time

        # 코인 충돌
        coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
        score += len(coins_collected) * 10

        # 생존 시간
        survival_time = time.time() - start_time

        # 화면 출력
        player_group.draw(screen)
        enemy_group.draw(screen)
        coin_group.draw(screen)
        bullet_group.draw(screen)
        explosion_group.draw(screen)


        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = font.render(f"Time: {int(survival_time)}s", True, (0, 0, 0))
        ammo_text = font.render(f"Bullet: {player.ammo}/{player.max_ammo}", True, (0, 0, 0))

        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 50))
        screen.blit(ammo_text, (10, 90))

    else:
        # ============ 게임 오버 화면 ============
        font_large = pygame.font.SysFont(None, 72)
        font_small = pygame.font.SysFont(None, 36)

        gameover_text = font_large.render("GAME OVER", True, (255, 0, 0))
        score_text = font_small.render(f"Final Score: {score}", True, (0, 0, 0))
        time_text = font_small.render(f"Survival Time: {int(survival_time)}s", True, (0, 0, 0))
        restart_text = font_small.render("Press R to Restart or Q to Quit", True, (100, 100, 100))

        screen.blit(gameover_text, (WIDTH//2 - 180, HEIGHT//2 - 100))
        screen.blit(score_text, (WIDTH//2 - 100, HEIGHT//2))
        screen.blit(time_text, (WIDTH//2 - 130, HEIGHT//2 + 40))
        screen.blit(restart_text, (WIDTH//2 - 180, HEIGHT//2 + 100))

        # 키 입력 처리
        if keys[pygame.K_r]:
            # 게임 재시작
            score = 0
            frame_count = 0
            start_time = time.time()
            game_over = False
            player.rect.center = (WIDTH//2, HEIGHT-50)
            enemy_group.empty()
            coin_group.empty()
            bullet_group.empty()
        elif keys[pygame.K_q]:
            running = False

    pygame.display.flip()
    clock.tick(60)


