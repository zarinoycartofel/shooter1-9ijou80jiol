from pygame import *
from random import randint

# --- Инициализация звуков и музыки ---
mixer.init()
mixer.music.load('space.ogg')  # Загрузка фоновой музыки
mixer.music.play()             # Бесконечное воспроизведение музыки
fire_sound = mixer.Sound('fire.ogg')  # Загрузка звука выстрела

# --- Настройка шрифтов и текста ---
font.init()
font = font.SysFont('Arial', 36)  # Создание шрифта Arial, размер 36

# Подготовка надписей для финала игры (текст, сглаживание, цвет)
win = font.render('Ты победил!', 1, 'Green')
lose = font.render('Ты проиграл!', 1, (180, 0, 0))

# --- Пути к изображениям (названия файлов) ---
img_back = "galaxy.jpg"  # Фон игры
img_hero = "rocket.png"  # Корабль игрока
img_enemy = "ufo.png"    # Вражеское НЛО
img_bullet = 'bullet.png' # Пуля
img_ast = 'asteroid.png' # Астероид

# --- Игровые переменные и счетчики ---
score = 0       # Сколько врагов сбил игрок
lost = 0        # Сколько врагов улетело за нижний край
max_lost = 11   # Лимит пропущенных врагов, после которого наступает проигрыш
max_score = 101 # Количество очков, необходимое для победы
lives = 3       # Начальное количество жизней игрока

# ==============================================================================
# ОПИСАНИЕ КЛАССОВ (ООП)
# ==============================================================================

# Базовый класс для всех спрайтов (персонажей) в игре
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        # Загружаем картинку и меняем ее размер под нужные параметры
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed # Скорость перемещения спрайта
        self.rect = self.image.get_rect() # Создаем хитбокс (прямоугольник) объекта
        self.rect.x = player_x # Координата X на экране
        self.rect.y = player_y # Координата Y на экране
        
    def reset(self):
        # Отрисовка спрайта в его текущих координатах
        window.blit(self.image, (self.rect.x, self.rect.y))

# Класс для управляемого игроком корабля
class Player(GameSprite):
    def update(self):
        # Проверяем нажатые клавиши для движения влево/вправо с ограничением по краям
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
            
    def fire(self):
        # Создаем пулю над кораблем (по центру x) и добавляем ее в группу пуль
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, 15)
        bullets.add(bullet)

# Класс для врагов (НЛО)
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed # Движение врага строго вниз
        global lost
        # Если враг улетел за нижнюю границу экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80) # Телепортируем его наверх в случайный X
            self.rect.y = 0
            lost += 1 # Засчитываем пропуск

# Класс для астероидов (падающие препятствия, которые нельзя сбить)
class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed # Движение вниз
        # Если астероид улетел за экран, возвращаем его наверх без штрафа по очкам
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 30)
            self.rect.y = -40

# Класс для летящих вверх пуль
class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed # Движение пули строго вверх
        # Если пуля улетела за верхний край, удаляем ее из памяти программы
        if self.rect.y < 0:
            self.kill()            

# ==============================================================================
# НАСТРОЙКА ОКНА И СОЗДАНИЕ ОБЪЕКТОВ
# ==============================================================================

win_width = 700   # Ширина игрового окна
win_height = 500  # Высота игрового окна
display.set_caption("Shooter") # Название окна
window = display.set_mode((win_width, win_height)) # Создание самого окна
background = transform.scale(image.load(img_back), (win_width, win_height)) # Подгонка фона под размер окна

# Создание игрока (картинка, координаты X и Y, размеры, скорость)
ship = Player(img_hero, win_width/2 - 40, win_height - 100, 80, 100, 10) 

# Создание группы врагов-монстров (5 штук)
monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)

# Создание группы астероидов (2 штуки)
asteroids = sprite.Group()
for i in range(1, 3):
    ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
    asteroids.add(ast)

# Создание пустой группы для будущих пуль
bullets = sprite.Group()

# Переменные управления состояниями игры
finish = False  # Флаг окончания раунда (True, если победили или проиграли)
run = True      # Флаг работы всего приложения (False закроет окно)

# ==============================================================================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
# ==============================================================================
while run:
    # Цикл обработки событий (нажатия клавиш, мыши, закрытие окна)
    for e in event.get():
        if e.type == QUIT: # Если нажали на "крестик" окна
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE: # Если нажали Пробел
                fire_sound.play() # Включаем звук выстрела
                ship.fire()       # Корабль выпускает пулю

    # Если раунд продолжается (игра не на паузе финала)
    if not finish:
        window.blit(background, (0,0)) # Отрисовка фонового изображения

        # Создание и отрисовка текста со счетом и пропусками
        text_score = font.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text_score, (10, 20))
        text_lost = font.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lost, (10, 50))
        
        # Выбор цвета счетчика жизней в зависимости от их количества (Зеленый -> Желтый -> Красный)
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

        # Проверка столкновения пуль с монстрами (True, True удаляет и пулю, и монстра)
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
            # Эффект урона: подсвечиваем весь экран красным оттенком
            window.fill((150, 0, 0), special_flags=BLEND_RGB_ADD)
            display.update()
            time.delay(200) # Короткая пауза, чтобы игрок заметил урон

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
            finish = True # Останавливаем игру
            window.blit(lose, (200, 200)) # Выводим надпись "Ты проиграл!"

        # Проверка условий победы
        if score >= max_score:
            finish = True # Останавливаем игру
            window.blit(win, (200, 200)) # Выводим надпись "Ты победил!"

        display.update() # Обновляем кадр на экране
        
    else:
        # --- Блок перезапуска игры (если finish == True) ---
        finish = False
        score = 0
        lost = 0
        lives = 3 # Сбрасываем счетчик жизней до начального значения
        
        # Очищаем все группы объектов от старых спрайтов
        for b in bullets: b.kill()
        for m in monsters: m.kill()
        for a in asteroids: a.kill()

        time.delay(4000) # Ждем 4 секунды перед началом нового раунда
        
        # Заново заполняем игру монстрами
        for i in range(1, 6):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)
            
        # Заново заполняем игру астероидами
        for i in range(1, 3):
            ast = Asteroid(img_ast, randint(30, win_width - 30), -40, 80, 50, randint(1, 7))
            asteroids.add(ast)

    time.delay(40) # Искусственная задержка (ограничение FPS примерно до 25 кадров в секунду)


