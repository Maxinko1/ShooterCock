from pygame import *
from random import randint


Lost = False

class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, size_x, size_y, speed, cooldown_time, bullets_counter, cooldown_shots):
        super().__init__()
       
        self.image = transform.scale(image.load(img), (size_x, size_y))
        self.speed = speed
       
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.cooldown_time = cooldown_time
        self.last_shot_time = cooldown_time

        self.bullets_counter = bullets_counter

        self.cooldown_shots = cooldown_shots
       
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < win_width:
            self.rect.x += self.speed
        if keys[K_SPACE]:
            if self.bullets_counter > 0:
                time_ticks = time.get_ticks()
                if time_ticks - self.last_shot_time >= self.cooldown_time:
                    self.fire()
                    self.last_shot_time = time_ticks
                    self.bullets_counter -= 1
            if self.bullets_counter == 0 or self.bullets_counter < 0:
                time_ticks = time.get_ticks()
                if time_ticks - self.last_shot_time >= self.cooldown_shots:
                    self.last_shot_time = time_ticks
                    self.bullets_counter = 5
   
    def fire(self):
        fire_sound.play()
        bullet = Bullet("bullet.png", self.rect.centerx - 7.5, self.rect.top, 17, 25, -15, 0, 0, 0)
        bullets.add(bullet)
       
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.y = -50
            self.rect.x = randint(0, win_width - 80)
            self.speed = randint(1, 5)
           
            global lost
            lost += 1

bullets_counter = 5
bullets = sprite.Group()  # Создание группы для хранения пуль

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < -10:
            self.kill()


# Кол-во пропущенных НЛО
lost = 0
score = 0
lives = 3


# Фоновая музыка
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()


fire_sound = mixer.Sound("fire.ogg")


# Шрифты
font.init()
label_score_font = font.SysFont("Arial", 36)
label_score_font54 = font.SysFont("Arial", 54)




win_width = 700
win_height = 500


window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")


background = transform.scale(
    image.load("galaxy.jpg"), (win_width, win_height)
)


ship = Player("rocket.png", 5, win_height - 100, 80, 100, 10, 150, 5, 600)


monsters = sprite.Group()
asteroids = sprite.Group()

def create_enemy(monsters_group, asteroids_group):
    for m in monsters_group:
        m.kill()
    for a in asteroids_group:
        a.kill()
    for _ in range(4):
        monsters_group.add(
            Enemy("ufo.png",
                randint(0, win_width - 80),
                -50,
                80,
                50,
                randint(1, 5),
                0,
                0,
                0)
        )

    for _ in range(2):
        asteroids_group.add(
            Enemy("asteroid.png",
                randint(0, win_width - 80),
                -100,
                50,
                50,
                randint(1, 4),
                0,
                0,
                0)
        )


finish = False
run = True
create_enemy(monsters, asteroids)


while run:
    time.delay(50)

    for e in event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN and e.key == K_r and finish == True:
            finish = False

            score = 0
            lost = 0
            lives = 3
            bullets_counter = 5
            Lost = False

            label_score_font = font.SysFont("Arial", 36)
            label_score_font54 = font.SysFont("Arial", 54)

            for b in bullets:
                b.kill()
            
            create_enemy(monsters, asteroids)
            ship.rect.x = (win_width // 2) - 25
            ship.rect.y = win_height - 100

    if not finish:
        window.blit(background, (0, 0))

        # Обновление и отображение врагов
        monsters.update()
        monsters.draw(window)

        asteroids.update()
        asteroids.draw(window)

        # Обновление и отображение игрока
        ship.update()
        ship.reset()

        # Обновление и отображение пуль
        bullets.update()
        bullets.draw(window)

        # Проверка столкновения пуль с врагами
        for bullet in bullets:
            hit_list = sprite.spritecollide(bullet, monsters, True)
            for hit in hit_list:
                bullet.kill()
                score += 1

                new_enemy = Enemy("ufo.png", randint(0, win_width - 80), -50, 80, 50, randint(1, 5), 0, 0, 0)
                monsters.add(new_enemy)

        for bullet in bullets:
            hit_list = sprite.spritecollide(bullet, asteroids, True)
            for hit in hit_list:
                bullet.kill()
                score += 1

                new_enemy = Enemy("asteroid.png", randint(0, win_width - 80), -50, 50, 50, randint(1, 4), 0, 0, 0)
                asteroids.add(new_enemy)
                
        for enemy in monsters:
            hit_list = sprite.spritecollide(ship, monsters, True)
            for hit in hit_list:
                lives -= 1

                new_enemy = Enemy("ufo.png", randint(0, win_width - 80), -50, 80, 50, randint(1, 5), 0, 0, 0)
                monsters.add(new_enemy)

        for enemy in asteroids:
            hit_list = sprite.spritecollide(ship, asteroids, True)
            for hit in hit_list:
                lives -= 1

                new_enemy = Enemy("asteroid.png", randint(0, win_width - 80), -50, 50, 50, randint(1, 4), 0, 0, 0)
                asteroids.add(new_enemy)
        
        if lost == 3:
            lives -= 1
            lost = 0

        if ship.bullets_counter == 0 or ship.bullets_counter < 0:
            time_ticks = time.get_ticks()
            if time_ticks - ship.last_shot_time >= ship.cooldown_shots:
                window.blit(
                    label_score_font54.render(
                    f"Перезарядка", True, (255, 255, 255)
                    ), (250, 450)
                )

        # Отображение счета и количества пропущенных врагов
        window.blit(
            label_score_font.render(
                f"Счет: {score}", True, (255, 255, 255)
            ), (10, 20)
        )

        window.blit(
            label_score_font.render(
                f"Пропущено: {lost}", True, (255, 255, 255)
            ), (10, 50)
        )

        window.blit(
            label_score_font.render(
                f"Жизней: {lives}", True, (255, 255, 255)
            ), (10, 80)
        )

        # Проверка условия поражения
        if lost >= 3 or lives < 1:
            finish = True
            label_score_font = font.SysFont("Arial", 100)
            window.blit(
                label_score_font.render(
                    f"YOU LOSE", True, (255, 0, 0)
                ), (175, 200)
            )

        # Проверка условия победы
        if score >= 25 and lives >= 1:
            finish = True
            label_score_font = font.SysFont("Arial", 100)
            window.blit(
                label_score_font.render(
                    f"YOU WIN!", True, (50, 205, 50)
                ), (175, 200)
            )

        display.update()
