from pygame import *
from random import randint

mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

font.init()
font = font.SysFont('Arial', 36)

win = font.render('Ты победил!', 1, 'Green')
lose = font.render('Ты проиграл!', 1, (180, 0, 0))

img_back = "galaxy.jpg"
img_hero = "rocket.png"
img_enemy = "ufo.png"
img_bullet = 'bullet.png'
img_ast = 'asteroid.png' 

score = 0
lost = 0
max_lost = 11
max_score = 101
lives = 3 # Начальное количество жизней

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = -40

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()            

win_width = 700
win_height = 500
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

ship = Player(img_hero, win_width/2 - 40, win_height - 100, 80, 100, 10) 

monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

asteroids = sprite.Group()
for i in range(1, 3):
    ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
    asteroids.add(ast)

bullets = sprite.Group()

finish = False
run = True 
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                fire_sound.play()
                ship.fire()

    if not finish:
        window.blit(background,(0,0))

        text_score = font.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text_score, (10, 20))
        text_lost = font.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lost, (10, 50))
        
        # Отображение жизней на экране разными цветами в зависимости от остатка
        if lives == 3: life_color = (0, 255, 0)
        elif lives == 2: life_color = (255, 255, 0)
        else: life_color = (255, 0, 0)
        text_lives = font.render("Жизни: " + str(lives), 1, life_color)
        window.blit(text_lives, (win_width - 150, 20))

        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update() 

        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window) 

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        # Проверка столкновения с монстрами
        if sprite.spritecollide(ship, monsters, True):
            lives -= 1
            # Возвращаем одного монстра взамен уничтоженного при столкновении
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
            # Вспышка экрана при уроне
            window.fill((150, 0, 0), special_flags=BLEND_RGB_ADD)
            display.update()
            time.delay(200)

        # Проверка столкновения с астероидами
        if sprite.spritecollide(ship, asteroids, True):
            lives -= 1
            # Возвращаем один астероид взамен уничтоженного
            ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(ast)
            # Вспышка экрана при уроне
            window.fill((150, 0, 0), special_flags=BLEND_RGB_ADD)
            display.update()
            time.delay(200)

        # Проигрыш: закончились жизни ИЛИ много пропущено
        if lives <= 0 or lost >= max_lost:
            finish = True
            window.blit(lose, (200, 200))

        if score >= max_score:
            finish = True
            window.blit(win, (200, 200))

        display.update()
    else:
        finish = False
        score = 0
        lost = 0
        lives = 3 # Сброс жизней при перезапуске
        for b in bullets: b.kill()
        for m in monsters: m.kill()
        for a in asteroids: a.kill()

        time.delay(4000)
        for i in range(1, 6):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
        for i in range(1, 3):
            ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(ast)

    time.delay(40)

