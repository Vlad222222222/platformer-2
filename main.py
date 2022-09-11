import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1550
screen_height = 800

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Мой платформер')

# создаем фон
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

# создаем переменные
tile_size = 50
game_over = 0
main_menu = True
level = 3
max_levels = 15
score = 0

# создаем цвета
white = (255, 255, 255)
blue = (0, 0, 255)

# загружаем артинки
sun_img = pygame.image.load('sun (1).png')
bg_img = pygame.image.load('bg.png')
restart_img = pygame.image.load('restart.png')
start_img = pygame.image.load('start.png')
exit_img = pygame.image.load('exit.png')

# загружаем музыку
pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
coin_fx = pygame.mixer.Sound('coin.wav ')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('game_over.wav')
game_over_fx.set_volume(0.5)
game_win_fx = pygame.mixer.Sound('game_win.wav')
game_win_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# функция рестарта левла
def reset_level(level):
    player.reset(100, screen_height - 130)
    snail_group.empty()
    platform_group.empty()
    spring_group.empty()
    coin_group.empty()
    lava_group.empty()
    exit_group.empty()
    cactus_group.empty()
    bird_group.empty()
    snail_spring_group.empty()
    dont_snail_spring_group.empty()
    ice_group.empty()
    honey_group.empty()


    # загружаем уровни и создаем мир
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)
    # создаем монеты койны и счет монет
    score_coin = Coin(tile_size // 2, tile_size // 2)
    coin_group.add(score_coin)
    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        # получаем позиции мыши
        pos = pygame.mouse.get_pos()

        # проверка условия перехода и нажатия
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # рисуем кнопки
        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5
        col_thresh = 20

        if game_over == 0:
            # получаем нажатия клавиатуры
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = - 15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 1
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # анимация
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # создаем гравитацию
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # проверяем коллизию
            self.in_air = True
            for tile in world.tile_list:
                # проверяем нет ли столкновения по координате x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # проверяем нет ли столкновения по координате y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверка прыгает ли персонаж
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    # проверка падает ли персонаж
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # проверка на столкновение с врагами
            if pygame.sprite.spritecollide(self, snail_group, False):
                game_over = -1
                game_over_fx.play()

            # проверка на столкновение с кактусом
            if pygame.sprite.spritecollide(self, cactus_group, False):
                game_over = -1
                game_over_fx.play()

            # проверка на столкновение с лавой
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1
                game_over_fx.play()

            # проверка на столкновение с выходом
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1

            # проверка на столкновение с птицей
            if pygame.sprite.spritecollide(self, bird_group, False):
                game_over = -1
                game_over_fx.play()

            # проверка на столкновение с не улиткой пружинкой
            if pygame.sprite.spritecollide(self, dont_snail_spring_group, False):
                game_over = -1
                game_over_fx.play()

            # проверка на столкновение с платформой
            for platform in platform_group:
                # столкновения по координате x
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # столкновения по координате y
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверить, если ниже платформы
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # проверьте, есть ли над платформой
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # двигаться боком с платформой
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # проверка на столкновение с пружиной
            for spring in spring_group:
                # столкновения по координате x
                if spring.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # столкновения по координате y
                if spring.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if below platform
                    if abs((self.rect.top + dy) - spring.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = spring.rect.bottom - self.rect.top
                    # проверьте, есть ли над платформой
                    elif abs((self.rect.bottom + dy) - spring.rect.top) < col_thresh:
                        self.rect.bottom = spring.rect.top - 1
                        self.vel_y = -20

            # проверка на столкновение с  улиткой пружиной
            for snail_spring in snail_spring_group:
                # столкновения по координате x
                if snail_spring.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # столкновения по координате y
                if snail_spring.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверить, если ниже платформы
                    if abs((self.rect.top + dy) - snail_spring.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = snail_spring.rect.bottom - self.rect.top
                    # проверьте, есть ли над платформой
                    elif abs((self.rect.bottom + dy) - snail_spring.rect.top) < col_thresh:
                        self.rect.bottom = snail_spring.rect.top - 1
                        self.vel_y = -15

            # проверка на столкновение с  льдом
            for ice in ice_group:
                # столкновения по координате x
                if ice.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # collision in the x direction
                if ice.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверить, если ниже платформы
                    if abs((self.rect.top + dy) - ice.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = ice.rect.bottom - self.rect.top
                    # проверьте, есть ли над платформой
                    elif abs((self.rect.bottom + dy) - ice.rect.top) < col_thresh:
                        self.rect.bottom = ice.rect.top - 1
                        dx = +10
                        self.in_air = False

            # проверка на столкновение с  медом
            for honey in honey_group:
                # столкновения по координате x
                if honey.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # столкновения по координате y
                if honey.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # проверить, если ниже платформы
                    if abs((self.rect.top + dy) - honey.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = honey.rect.bottom - self.rect.top
                    # проверьте, есть ли над платформой
                    elif abs((self.rect.bottom + dy) - honey.rect.top) < col_thresh:
                        self.rect.bottom = honey.rect.top - 1
                        self.vel_y = 0



                    # move sideways with the platform

            # обновляем координаты игрока
            self.rect.x += dx
            self.rect.y += dy


        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
            if self.rect.y > 200:
                self.rect.y -= 5

        # вывод игрока на экран
        screen.blit(self.image, self.rect)

        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 1
        self.counter = 0
        for num in range(1, 5):
            img_right = pygame.image.load(f'guy{num}.png')
            img_right = pygame.transform.scale(img_right, (40, 80))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('dead.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True


class World():
    def __init__(self, data):
        self.tile_list = []

        # загрузка изоюбражений
        dirt_img = pygame.image.load('dirt.png')
        grass_img = pygame.image.load('grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    snail = Enemy(col_count * tile_size, row_count * tile_size + 25)
                    snail_group.add(snail)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 9:
                    cactus = Cactus(col_count * tile_size, row_count * tile_size + 1)
                    cactus_group.add(cactus)
                if tile == 10:
                    spring = Spring(col_count * tile_size, row_count * tile_size + 1)
                    spring_group.add(spring)
                if tile == 11:
                    bird = Bird(col_count * tile_size, row_count * tile_size + 1)
                    bird_group.add(bird)
                if tile == 12:
                    snail_spring = Snail_spring(col_count * tile_size, row_count * tile_size + 1)
                    snail_spring_group.add(snail_spring)
                if tile == 13:
                    dont_snail_spring = Dont_snail_spring(col_count * tile_size, row_count * tile_size + 1)
                    dont_snail_spring_group.add(dont_snail_spring)
                if tile == 14:
                    honey = Honey(col_count * tile_size, row_count * tile_size + 1)
                    honey_group.add(honey)
                if tile == 15:
                    ice = Ice(col_count * tile_size, row_count * tile_size + 1)
                    ice_group.add(ice)


                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('snail.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_direction_y = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 100:
            self.move_direction *= -1
            self.move_counter *= -1



class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('platform.x.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('coin.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('выход.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Cactus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('cactus.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size + 25))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Spring(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('spring.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('bird.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 4
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 30:
            self.move_direction *= -1
            self.move_counter *= -1

class Snail_spring(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('snail_spring.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 3
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= -1

class Dont_snail_spring(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('dont_snail_spring.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_direction_y = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 100:
            self.move_direction *= -1
            self.move_counter *= -1

class Ice(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('ice.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Honey(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('honey.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




player = Player(100, screen_height - 130)

dont_snail_spring_group = pygame.sprite.Group()
snail_spring_group = pygame.sprite.Group()
spring_group = pygame.sprite.Group()
cactus_group = pygame.sprite.Group()
snail_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
ice_group = pygame.sprite.Group()
honey_group = pygame.sprite.Group()

# отображение отчета создание монеты
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# загрузка уровня и создание мира
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# создание кнопок
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)

run = True
while run:

    clock.tick(fps)

    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    if  main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            snail_group.update()
            platform_group.update()
            spring_group.update()
            cactus_group.update()
            bird_group.update()
            snail_spring_group.update()
            dont_snail_spring_group.update()
            ice_group.update()
            honey_group.update()


        if pygame.sprite.spritecollide(player, coin_group, True):
            score += 1
            coin_fx.play()
        draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)


        cactus_group.draw(screen)
        snail_group.draw(screen)
        platform_group.draw(screen)
        spring_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)
        bird_group.draw(screen)
        snail_spring_group.draw(screen)
        dont_snail_spring_group.draw(screen)
        ice_group.draw(screen)
        honey_group.draw(screen)

        game_over = player.update(game_over)

        # смерть игрока
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # игрок выйграл
        if game_over == 1:
            # рестарт левла или следущий уровень
            level += 1
            if level <= max_levels:
                # рестарт уровня
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('Ты выйграл!', font, blue, (screen_width // 2) - 140, screen_height // 2)
                game_win_fx.play()
                if restart_button.draw():
                    level = 1
                    # рестарт левла
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
