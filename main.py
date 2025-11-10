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
        self.gun_level = 1          # 🔫 총 레벨 (1~3)
        self.max_gun_level = 3

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= player_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += player_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= player_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += player_speed

        # 총알 발사 (총 레벨에 따라 발사 개수 변경)
        current_time = time.time()
        if keys[pygame.K_SPACE]:
            if not self.shooting and self.ammo > 0 and current_time - self.last_shot_time >= self.shoot_cooldown:
                if self.gun_level == 1:
                    # 1발 (중앙)
                    bullet = Bullet(self.rect.centerx, self.rect.top)
                    bullet_group.add(bullet)
                elif self.gun_level == 2:
                    # 2발 (좌우)
                    bullet_left = Bullet(self.rect.centerx - 15, self.rect.top)
                    bullet_right = Bullet(self.rect.centerx + 15, self.rect.top)
                    bullet_group.add(bullet_left, bullet_right)
                elif self.gun_level == 3:
                    # 3발 (중앙, 좌, 우)
                    bullet_center = Bullet(self.rect.centerx, self.rect.top)
                    bullet_left = Bullet(self.rect.centerx - 20, self.rect.top)
                    bullet_right = Bullet(self.rect.centerx + 20, self.rect.top)
                    bullet_group.add(bullet_center, bullet_left, bullet_right)
                
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
    def __init__(self, x, y, size=60):  # 기본 폭발 크기 60
        super().__init__()
        self.image = pygame.image.load("./assets/explosion.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (size, size))
        self.rect = self.image.get_rect(center=(x, y))
        self.start_time = time.time()
        self.duration = 0.4  # 폭발 지속 시간(초)

    def update(self):
        # 일정 시간 후 자동 제거
        if time.time() - self.start_time > self.duration:
            self.kill()

class Boss(pygame.sprite.Sprite):
    def __init__(self, hp_bonus=0, attack_delay=1.0):
        super().__init__()
        self.image = pygame.image.load("./assets/boss.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 120))  # 보스 크기
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))  # 화면 상단 중앙
        self.hp = 30 + hp_bonus  # 기본 30 + 추가 체력
        self.max_hp = 30 + hp_bonus
        self.last_attack_time = time.time()
        self.attack_delay = attack_delay  # 공격 속도 (초)
        self.alive = True

    def update(self):
        # 체력 0이면 제거
        if self.hp <= 0:
            self.alive = False
            explosion = Explosion(self.rect.centerx, self.rect.centery, size=200)
            explosion_group.add(explosion)
            self.kill()
            global score, last_boss_death_time, boss_spawned, boss_kill_count, first_boss_killed
            score += 300  # 보상 점수
            last_boss_death_time = time.time()  # 사망 시간 기록
            boss_spawned = False  # 다음 보스 생성 가능 상태로 전환
            boss_kill_count += 1  # 보스 처치 카운트 증가
            first_boss_killed = True  # 첫 번째 보스 이후 계속 리스폰


        # 일정 시간마다 공격
        current_time = time.time()
        if current_time - self.last_attack_time > self.attack_delay:
            self.last_attack_time = current_time
            # 화면 가로 범위 내 랜덤 위치에서 총알 발사
            x = random.randint(self.rect.left, self.rect.right)
            boss_bullet = BossBullet(x, self.rect.bottom)
            boss_bullet_group.add(boss_bullet)

    def draw_hp_bar(self, surface):
        # HP 비율 계산
        ratio = self.hp / self.max_hp
        bar_width = 180
        bar_height = 12
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 20

        # 배경(빨강)
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        # 현재 HP(초록)
        pygame.draw.rect(surface, (0, 255, 0), (x, y, int(bar_width * ratio), bar_height))

class MovingBoss(Boss):
    def __init__(self, hp_bonus=0, attack_delay=1.0, is_final=False):
        super().__init__(hp_bonus, attack_delay)
        
        # 최종 보스면 finalBoss 이미지 사용
        if is_final:
            self.image = pygame.image.load("./assets/finalBoss.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (240, 150))  # 최종 보스는 더 크게
        else:
            self.image = pygame.image.load("./assets/MovingBoss.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (220, 130))
        
        self.rect = self.image.get_rect(center=(WIDTH // 2, 100))
        self.speed_x = 3  # 좌우 이동 속도

    def update(self):
        super().update()

        # 좌우로 이동
        self.rect.x += self.speed_x
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.speed_x *= -1  # 방향 반전


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("./assets/bossBullet.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 40))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5  # 아래로 이동

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class BulletItem(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./assets/bulletItem.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (35, 35))  # 아이템 크기
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), 0))
        self.speed = 3  # 떨어지는 속도

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class GunItem(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./assets/gunItem.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))  # 아이템 크기
        self.rect = self.image.get_rect(center=(random.randint(20, WIDTH - 20), 0))
        self.speed = 3  # 떨어지는 속도

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Warning(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./assets/warning.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (300, 300))  # 경고 이미지 크기
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.start_time = time.time()
        self.blink_count = 0
        self.max_blinks = 3  # 3번 깜빡임
        self.blink_duration = 0.3  # 각 깜빡임 지속 시간 (초)
        self.visible = True
        self.last_blink_time = time.time()

    def update(self):
        current_time = time.time()
        elapsed = current_time - self.last_blink_time
        
        # 깜빡임 효과
        if elapsed >= self.blink_duration:
            self.visible = not self.visible
            self.last_blink_time = current_time
            if not self.visible:
                self.blink_count += 1
        
        # 3번 깜빡이면 제거
        if self.blink_count >= self.max_blinks:
            self.kill()

    def draw(self, surface):
        if self.visible:
            surface.blit(self.image, self.rect)


player = Player()
player_group = pygame.sprite.Group(player)
enemy_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
bullet_item_group = pygame.sprite.Group()
gun_item_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
boss_group = pygame.sprite.Group()
boss_bullet_group = pygame.sprite.Group()
warning_group = pygame.sprite.Group()
boss_spawned = False
last_boss_death_time = 0
warning_shown = False  # 경고 표시 여부
warning_start_time = 0  # 경고 시작 시간
boss_kill_count = 0  # 보스 처치 횟수
first_boss_killed = False  # 첫 번째 보스 처치 여부

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

        # 🔹 랜덤하게 총알 아이템 생성 (약 0.3% 확률)
        if random.randint(1, 100) <= 3:
            bullet_item_group.add(BulletItem())

        # 🔫 gun_level이 3 미만일 때만 gunItem 생성
        if player.gun_level < player.max_gun_level and random.randint(1, 1800) <= 2:
            gun_item_group.add(GunItem())

        # 업데이트
        player.update(keys)
        enemy_group.update()
        coin_group.update()
        bullet_group.update()
        explosion_group.update()
        boss_group.update()
        boss_bullet_group.update()
        bullet_item_group.update()
        gun_item_group.update()
        warning_group.update()  # 경고 업데이트 추가

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

        # 보스 총알 충돌
        for bullet in bullet_group:
            hit_boss = pygame.sprite.spritecollide(bullet, boss_group, False)
            for b in hit_boss:
                b.hp -= 1
                bullet.kill()
                score += 10

        # 충돌 감지 → 게임오버로 전환
        if pygame.sprite.spritecollide(player, enemy_group, False):
            game_over = True
            end_time = time.time()
            survival_time = end_time - start_time

        if pygame.sprite.spritecollide(player, boss_bullet_group, True):
            game_over = True
            end_time = time.time()
            survival_time = end_time - start_time

        # 코인 충돌
        coins_collected = pygame.sprite.spritecollide(player, coin_group, True)
        score += len(coins_collected) * 10

        # 🔹 총알 아이템 충돌
        bullet_items_collected = pygame.sprite.spritecollide(player, bullet_item_group, True)
        for _ in bullet_items_collected:
            player.ammo = min(player.max_ammo, player.ammo + 5)  # 최대 탄약 초과 방지

        # 🔫 총 아이템 충돌
        gun_items_collected = pygame.sprite.spritecollide(player, gun_item_group, True)
        for _ in gun_items_collected:
            if player.gun_level < player.max_gun_level:
                player.gun_level += 1
                # print(f"🔫 총 레벨 업 현재 레벨: {player.gun_level}")

        # 생존 시간
        survival_time = time.time() - start_time

        # 첫 번째 보스 경고 및 생성
        if survival_time >= 8 and not warning_shown and not boss_spawned and not first_boss_killed:
            warning = Warning()
            warning_group.add(warning)
            warning_shown = True
            warning_start_time = time.time()
            # print("⚠️ 보스 경고!")
        
        # 경고 후 2초 뒤 첫 번째 보스 생성
        if warning_shown and not boss_spawned and not boss_group and not first_boss_killed and time.time() - warning_start_time >= 2:
            boss = Boss()  # 첫 보스는 기본 스탯
            boss_group.add(boss)
            boss_spawned = True
            warning_shown = False
            first_boss_killed = False
            # print("✅ 첫 번째 보스 등장")

        # 첫 번째 보스 처치 후 계속 리스폰되는 보스 시스템
        if first_boss_killed and not warning_shown and not boss_spawned and not boss_group and last_boss_death_time > 0 and time.time() - last_boss_death_time >= 18:
            warning = Warning()
            warning_group.add(warning)
            warning_shown = True
            warning_start_time = time.time()
            # print("⚠️ 보스 경고!")
        
        # 경고 후 2초 뒤 이동형 보스 생성 (첫 번째 보스 처치 후 총 20초)
        if first_boss_killed and warning_shown and not boss_spawned and not boss_group and last_boss_death_time > 0 and time.time() - warning_start_time >= 2:
            # 2번째 보스부터 체력 20씩 증가
            hp_bonus = (boss_kill_count - 1) * 20
            
            # 공격 속도 증가 (0.2초씩 빨라지고 최소 0.4초까지만)
            attack_delay = max(0.4, 1.0 - (boss_kill_count - 1) * 0.2)
            
            # 최종 보스인지 확인 (공격속도가 max에 도달했는지)
            is_final = (attack_delay <= 0.4)
            
            moving_boss = MovingBoss(hp_bonus, attack_delay, is_final)
            boss_group.add(moving_boss)
            boss_spawned = True
            warning_shown = False
            # print(f"🔥 이동형 보스 등장! HP: {moving_boss.max_hp}, 공격속도: {attack_delay:.1f}초")

        # 화면 출력
        player_group.draw(screen)
        enemy_group.draw(screen)
        coin_group.draw(screen)
        bullet_item_group.draw(screen)
        gun_item_group.draw(screen)
        bullet_group.draw(screen)
        explosion_group.draw(screen)
        boss_group.draw(screen)
        boss_bullet_group.draw(screen)
        
        # 경고 이미지 그리기 (깜빡임 효과 포함)
        for warning in warning_group:
            warning.draw(screen)
        
        for boss in boss_group:
            boss.draw_hp_bar(screen)

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = font.render(f"Time: {int(survival_time)}s", True, (0, 0, 0))
        ammo_text = font.render(f"Ammo: {player.ammo}/{player.max_ammo}", True, (0, 0, 0))
        gun_text = font.render(f"Gun Lv: {player.gun_level}", True, (0, 0, 0))

        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 50))
        screen.blit(ammo_text, (10, 90))
        screen.blit(gun_text, (10, 130))

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

            # 🔹 모든 그룹 초기화
            enemy_group.empty()
            coin_group.empty()
            bullet_group.empty()
            bullet_item_group.empty()
            gun_item_group.empty()
            explosion_group.empty()
            boss_group.empty()
            boss_bullet_group.empty()
            warning_group.empty()

            # 🔹 보스 재등장 조건 초기화
            boss_spawned = False
            last_boss_death_time = 0
            warning_shown = False
            warning_start_time = 0
            boss_kill_count = 0
            first_boss_killed = False
            
            # 🔫 플레이어 총 레벨 초기화
            player.gun_level = 1
            player.ammo = player.max_ammo
        elif keys[pygame.K_q]:
            running = False

    pygame.display.flip()
    clock.tick(60)