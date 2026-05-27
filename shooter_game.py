from pygame import *
from random import randint

# --- Инициализация звуков и музыки ---
mixer.init()
mixer.music.load('space.ogg')  
mixer.music.play()             
fire_sound = mixer.Sound('fire.ogg')  

# --- Настройка шрифтов и текста ---
font.init()
font = font.SysFont('Arial', 36)  

# надписи 
win = font.render('Ты победил!', 1, (255, 255, 0))
lose = font.render('Ты проиграл!', 1, (180, 0, 0))

#Пути к изображениям 
img_back = "galaxy.jpg"  
img_hero = "rocket.png" 
img_enemy = "ufo.png"    
img_bullet = 'bullet.png' 
img_ast = 'asteroid.png' 

# --- Игровые переменные и счетчики ---
score = 0       
lost = 0        
max_lost = 11   
max_score = 101 
lives = 3       


# Базовый класс для всех спрайтов (персонажей) в игре
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        # Загружаем картинку и меняем ее размер под нужные параметры
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed 
        self.rect = self.image.get_rect() 
        self.rect.x = player_x
        self.rect.y = player_y 
        
    def reset(self):
        # Отрисовка спрайта в его текущих координатах
        window.blit(self.image, (self.rect.x, self.rect.y))

# Класс для управляемого игроком корабля
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

# Класс для врагов 
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed 
        global lost
        # Если враг улетел за нижнюю границу экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80) 
            self.rect.y = 0
            lost += 1 # Засчитываем пропуск

# Класс для астероидов (падающие препятствия, которые нельзя сбить)
class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed 
        # Если астероид улетел за экран, возвращаем его наверх без штрафа по очкам
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 30)
            self.rect.y = -40

# Класс для летящих вверх пуль
class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed 
        # Если пуля улетела за верхний край, удаляем ее из памяти программы
        if self.rect.y < 0:
            self.kill()            


win_width = 700   
win_height = 500  
display.set_caption("Shooter") 
window = display.set_mode((win_width, win_height)) 
background = transform.scale(image.load(img_back), (win_width, win_height)) 

# Создание игрока 
ship = Player(img_hero, win_width/2 - 40, win_height - 100, 80, 100, 10) 

# Создание группы монстров 
monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

# Создание группы астероидов 
asteroids = sprite.Group()
for i in range(1, 3):
    ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
    asteroids.add(ast)

# Создание пустой группы для будущих пуль
bullets = sprite.Group()

# Переменные управления состояниями игры
finish = False  
run = True      


while run:
    # Цикл обработки событий 
    for e in event.get():
        if e.type == QUIT: 
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE: 
                fire_sound.play() 
                ship.fire()      

    # Если раунд продолжается 
    if not finish:
        window.blit(background, (0,0)) 

        # Создание и отрисовка текста со счетом и пропусками
        text_score = font.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text_score, (10, 20))
        text_lost = font.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lost, (10, 50))
        
        # Выбор цвета счетчика жизней в зависимости от их количества 
        if lives == 3: life_color = (0, 255, 0)
        elif lives == 2: life_color = (255, 255, 0)
        else: life_color = (255, 0, 0)
        text_lives = font.render("Жизни: " + str(lives), 1, life_color)
        window.blit(text_lives, (win_width - 150, 20))

        # Обновление логики и позиций всех игровых объектов
        ship.update()
        monsters.update()
        bullets.update()
        asteroids.update() 

        # Отрисовка всех объектов на экране
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        asteroids.draw(window) 

        # Проверка столкновения пуль с монстрами 
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1 # Начисляем очко за уничтожение
            # Спавним нового монстра взамен уничтоженного
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        # Проверка столкновения корабля с монстрами
        if sprite.spritecollide(ship, monsters, True):
            lives -= 1 # Отнимаем жизнь
            # Спавним нового монстра взамен уничтоженного при столкновении
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
           

        # Проверка столкновения корабля с астероидами
        if sprite.spritecollide(ship, asteroids, True):
            lives -= 1 # Отнимаем жизнь
            # Спавним новый астероид взамен уничтоженного при столкновении
            ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(ast)
            # Эффект урона: подсвечиваем экран красным
            window.fill((150, 0, 0), special_flags=BLEND_RGB_ADD)
            display.update()
            time.delay(200)

        # Проверка условий проигрыша
        if lives <= 0 or lost >= max_lost:
            finish = True 
            window.blit(lose, (200, 200)) 

        # Проверка условий победы
        if score >= max_score:
            finish = True 
            window.blit(win, (200, 200)) 

        display.update() # Обновляем кадр на экране
        
    else:
        finish = False
        score = 0
        lost = 0
        lives = 3 
        
        # Очищаем все группы объектов от старых спрайтов
        for b in bullets: b.kill()
        for m in monsters: m.kill()
        for a in asteroids: a.kill()

        time.delay(4000) 
        
        # Заново заполняем игру монстрами
        for i in range(1, 6):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
            
        # Заново заполняем игру астероидами
        for i in range(1, 3):
            ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(ast)

    time.delay(40)

