import math
import random

import pgzrun
from pgzero.actor import Actor
from pygame import Rect


WIDTH = 1280
HEIGHT = 640

GRAVITY = 0.5
JUMP_POWER = -12
PLAYER_SPEED = 4
ENEMY_SPEED = 1.5
DETECTION_RANGE = 200

background = 'rock_bg'
game_state = 'menu'
score = 0
fade_alpha = 0
fading = False
fade_mode = None
music_on = True


class GameObject:
    def __init__(self, image, pos):
        self.actor = Actor(image, pos)

    def draw(self):
        self.actor.draw()


class FloatingObject(GameObject):
    def __init__(self, image, pos):
        super().__init__(image, pos)
        self.base_y = pos[1]
        self.float_timer = random.randint(0, 60)

    def update(self):
        self.float_timer += 1
        offset = 3 * math.sin(self.float_timer * 0.1)
        self.actor.y = self.base_y + offset


class Coin(FloatingObject):
    pass


class Door(FloatingObject):
    pass


class Player(GameObject):
    def __init__(self, pos):
        super().__init__('mage-right-0', pos)
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.facing = 'right'
        self.anim_timer = 0

    def move(self):
        if keyboard.left:
            self.velocity_x = -PLAYER_SPEED
            self.facing = 'left'
        elif keyboard.right:
            self.velocity_x = PLAYER_SPEED
            self.facing = 'right'
        else:
            self.velocity_x = 0

        if keyboard.space and self.on_ground:
            self.velocity_y = JUMP_POWER

        self.velocity_y += GRAVITY
        self.actor.x += self.velocity_x
        self.handle_horizontal_collision()
        self.actor.y += self.velocity_y
        self.on_ground = False
        self.handle_vertical_collision()
        self.enforce_bounds()
        self.animate()

    def handle_horizontal_collision(self):
        for platform in solid_surfaces():
            if (self.actor.colliderect(platform)
                    and abs(self.actor.bottom - platform.top) > 5):
                if self.velocity_x > 0:
                    self.actor.right = platform.left
                elif self.velocity_x < 0:
                    self.actor.left = platform.right

    def handle_vertical_collision(self):
        for platform in solid_surfaces():
            if self.actor.colliderect(platform):
                if (self.velocity_y > 0
                        and self.actor.bottom <= platform.top + 15):
                    self.actor.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.actor.top = platform.bottom
                    self.velocity_y = 0

    def enforce_bounds(self):
        if self.actor.left < 0:
            self.actor.left = 0
        if self.actor.right > WIDTH:
            self.actor.right = WIDTH

    def animate(self):
        self.anim_timer += 1
        frame = (self.anim_timer // 10) % 4
        self.actor.image = f'mage-{self.facing}-{frame}'


class Enemy(GameObject):
    def __init__(self, pos, platform):
        super().__init__('zombie-right-0', pos)
        self.platform = platform
        self.velocity_x = random.choice([-ENEMY_SPEED, ENEMY_SPEED])
        self.facing = 'right' if self.velocity_x >= 0 else 'left'
        self.timer = 0

    def update(self):
        distance = abs(self.actor.x - player.actor.x)
        if (distance < DETECTION_RANGE
                and abs(self.actor.y - player.actor.y) < 50
                and self.is_same_platform()):
            self.velocity_x = (ENEMY_SPEED
                               if player.actor.x > self.actor.x
                               else -ENEMY_SPEED)
            self.facing = 'right' if self.velocity_x >= 0 else 'left'
        else:
            if self.actor.left <= self.platform.left:
                self.velocity_x = ENEMY_SPEED
                self.facing = 'right'
            if self.actor.right >= self.platform.right:
                self.velocity_x = -ENEMY_SPEED
                self.facing = 'left'

        self.actor.x += self.velocity_x
        self.actor.bottom = self.platform.top
        self.animate()

    def animate(self):
        self.timer += 1
        frame = (self.timer // 10) % 4
        self.actor.image = f'zombie-{self.facing}-{frame}'

    def is_same_platform(self):
        if self.platform.top == HEIGHT - 32:
            return player.actor.y >= HEIGHT - 64
        return (self.platform.left <= player.actor.x <= self.platform.right
                and abs(player.actor.y - self.platform.top) < 50)


floor_tiles = [Rect((x, HEIGHT - 32), (32, 32)) for x in range(0, WIDTH, 32)]
platforms = [
    Rect((200, 500), (160, 32)),
    Rect((500, 420), (160, 32)),
    Rect((700, 340), (160, 32)),
    Rect((350, 320), (64, 32)),
    Rect((500, 260), (160, 32)),
    Rect((650, 180), (160, 32))
]


def solid_surfaces():
    return floor_tiles + platforms


def draw_tiles():
    for tile in floor_tiles:
        screen.blit('floor', (tile.x, tile.y))
    for platform in platforms:
        for x in range(platform.left, platform.right, 32):
            screen.blit('platform', (x, platform.top))


player = Player((32, HEIGHT - 64))
door = Door('door', (platforms[-1].centerx, platforms[-1].top - 32))
coins = []


def spawn_coins():
    global coins
    coins = [Coin('coin', (p.centerx, p.top - 16)) for p in platforms]
    ground_positions = [100, 400, 600, 900, 1150]
    coins += [Coin('coin', (x, HEIGHT - 64 - 16)) for x in ground_positions]


def draw_button(rect, text):
    screen.draw.filled_rect(rect, 'darkgrey')
    screen.draw.rect(rect, 'black')
    screen.draw.text(text, center=rect.center, fontsize=40, color='black')


def menu_label_start():
    return 'Start Game'


def menu_label_sound():
    return 'Music ON' if music_on else 'Music OFF'


def menu_label_quit():
    return 'Quit Game'


buttons = {
    'start': Rect((WIDTH // 2 - 100, 180), (200, 50)),
    'sound': Rect((WIDTH // 2 - 100, 250), (200, 50)),
    'quit': Rect((WIDTH // 2 - 100, 320), (200, 50))
}

menu_labels = {
    'start': menu_label_start,
    'sound': menu_label_sound,
    'quit': menu_label_quit
}


def draw():
    screen.clear()
    screen.blit(background, (0, 0))

    if game_state == 'menu':
        screen.draw.text(
            "ESCAPE FROM THE ZOMBIES",
            center=(WIDTH // 2, 100),
            fontsize=60,
            color="black"
        )
        for key, rect in buttons.items():
            draw_button(rect, menu_labels[key]())

    elif game_state == 'playing':
        draw_tiles()
        door.draw()
        player.draw()
        for coin in coins:
            coin.draw()
        for enemy in enemies:
            enemy.draw()

        screen.draw.text(
            f"Score: {score}",
            topleft=(10, 10),
            fontsize=40,
            color="black"
        )
        screen.draw.text(
            "Move: left or right. Jump: Space",
            topleft=(10, 40),
            fontsize=40,
            color="black"
        )

    elif game_state == 'victory':
        screen.draw.text(
            "YOU ESCAPED FROM THE ZOMBIES",
            center=(WIDTH // 2, HEIGHT // 2),
            fontsize=60,
            color="black"
        )

    if fading or fade_mode:
        fade_surface = screen.surface.copy()
        fade_surface.set_alpha(fade_alpha)
        fade_surface.fill((0, 0, 0))
        screen.surface.blit(fade_surface, (0, 0))


def update():
    global game_state, fading, fade_alpha, fade_mode, score

    if game_state == 'menu':
        return

    if game_state == 'playing':
        player.move()

        for enemy in enemies:
            enemy.update()

        for coin in coins[:]:
            coin.update()
            if player.actor.colliderect(coin.actor):
                coins.remove(coin)
                score += 1
                sounds.collect_coin.play()

        for enemy in enemies:
            if player.actor.colliderect(enemy.actor):
                if not fading:
                    fading = True
                    fade_mode = 'out'

        door.update()

        if player.actor.colliderect(door.actor):
            game_state = 'victory'

    if fade_mode == 'out':
        fade_alpha += 8
        if fade_alpha >= 255:
            fade_alpha = 255
            fade_mode = 'in'
            reset_game()

    elif fade_mode == 'in':
        fade_alpha -= 8
        if fade_alpha <= 0:
            fade_alpha = 0
            fade_mode = None
            fading = False


def on_mouse_down(pos):
    global game_state, music_on

    if game_state == 'menu':
        sounds.click_001.play()

        if buttons['start'].collidepoint(pos):
            game_state = 'playing'

        elif buttons['quit'].collidepoint(pos):
            quit()

        elif buttons['sound'].collidepoint(pos):
            music_on = not music_on
            if music_on:
                sounds.soundtrack.play()
                sounds.soundtrack.set_volume(0.5)
            else:
                sounds.soundtrack.stop()


def reset_game():
    global enemies, score, game_state
    player.actor.pos = (32, HEIGHT - 64)
    player.velocity_x = 0
    player.velocity_y = 0
    player.anim_timer = 0
    player.actor.image = 'mage-right-0'
    enemies = generate_enemies()
    spawn_coins()
    score = 0
    game_state = 'playing'


def generate_enemies():
    spawn_options = [{
        'pos': (random.randint(32, WIDTH - 32), HEIGHT - 64),
        'platform': Rect((0, HEIGHT - 32), (WIDTH, 32))
    }]
    spawn_options += [{
        'pos': (plat.centerx, plat.top - 16),
        'platform': plat
    } for plat in platforms]

    return [Enemy(opt['pos'], opt['platform'])
            for opt in random.choices(spawn_options, k=5)]


enemies = generate_enemies()
spawn_coins()

sounds.soundtrack.play()
sounds.soundtrack.set_volume(0.5)

pgzrun.go()
