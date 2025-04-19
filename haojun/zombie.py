import pygame
import math
import random
import time

# Setup
#start pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
#run the game in 60fps
clock = pygame.time.Clock()

zombie_img = pygame.image.load("haojun/image/zombie.png").convert_alpha()  # <--- STEP 1
zombie_img = pygame.transform.scale(zombie_img, (32, 32))
zombie_walk_images = [
    pygame.transform.scale(pygame.image.load("haojun/image/zombiewalk1.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("haojun/image/zombiewalk2.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("haojun/image/zombiewalk3.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("haojun/image/zombiewalk4.png").convert_alpha(), (32, 32)),
    pygame.transform.scale(pygame.image.load("haojun/image/zombiewalk5.png").convert_alpha(), (32, 32)),
]

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()#Run the constructor (__init__) of the pygame.sprite.Sprite class before doing anything else in Player
        self.image = pygame.Surface((32, 32))#the size of the player
        self.image.fill((0, 0, 255))  # blue player
        self.rect = self.image.get_rect(center=(400, 300))#detect the collision, help pygame to allocate where is the player
        self.health = 100
        self.last_attack_time = 0  # This will store the time of the last attack
        self.attack_cooldown = 1  # Cooldown time in seconds

    def update(self, keys):
        speed = 5#go 5 pixel every time press the wasd
        if keys[pygame.K_w]: self.rect.y -= speed
        if keys[pygame.K_s]: self.rect.y += speed
        if keys[pygame.K_a]: self.rect.x -= speed
        if keys[pygame.K_d]: self.rect.x += speed

    def can_attack(self):
        current_time = time.time()  # Get the current time
        # Check if enough time has passed since the last attack
        if current_time - self.last_attack_time >= self.attack_cooldown:
            return True
        return False

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        print(f"Player health: {self.health}")

    def draw_health_bar(self, surface):
        bar_width = 200
        bar_height = 20
        fill = (self.health / 100) * bar_width
        x = (surface.get_width() - bar_width) // 2
        y = 570  # Bottom of screen
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))  # Red background
        pygame.draw.rect(surface, (0, 255, 0), (x, y, fill, bar_height))       # Green fill
        pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_width, bar_height), 2)  # White border

# Zombie class
class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.image = zombie_img.copy()  # <--- STEP 2
        self.idle_image = zombie_img.copy()  # This is the original image as idle frame
        self.image = self.idle_image
        self.rect = self.image.get_rect(center=(x, y))#handle collision detection and positioning.
        self.player = player#build a link between player and the zombie, the zombie can get the info of the player(coordinate of the player)
        self.speed = 1.5
        self.attack_range = 32
        self.attack_damage = 10
        self.last_attack_time = 0
        self.attack_cooldown = 1
        self.hp = 50
        self.max_hp = 50
        self.is_moving = False  # Track if zombie is actually moving
        self.walk_images = zombie_walk_images
        self.image = self.walk_images[0]#set the zombie to the 1st walking frame
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_index = 0
        self.last_animation_time = time.time()
        self.animation_speed = 0.2  # Seconds between frames

        # Wandering
        self.is_wandering = True#need more explaination
        self.wander_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]#the zombie can moving left right or up and down
        self.last_wander_time = time.time()#how long since last wander
        self.wander_interval = 2#how long should zombie wander
        self.pause_duration = 2#stop 2s after wandering

    def update(self):
        current_time = time.time()
        dx = self.player.rect.x - self.rect.x
        dy = self.player.rect.y - self.rect.y
        dist = math.hypot(dx, dy)#hypothenuse

        chase_range = 200

        if dist < chase_range:
            if dist == 0:
                dist = 1#avoid 0 division
            dx, dy = dx / dist, dy / dist#let the zombie have consistent speed

            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.rect.x += dx * self.speed
                self.rect.y += dy * self.speed
                self.is_moving = True
            else:
                self.is_moving = False

            if dist < self.attack_range and current_time - self.last_attack_time >= self.attack_cooldown:
                self.attack_player()
        else:
            if self.is_wandering:
                self.rect.x += self.wander_direction[0] * self.speed * 0.5#this is for x
                self.rect.y += self.wander_direction[1] * self.speed * 0.5#this is for y
                self.is_moving = True


                if current_time - self.last_wander_time > self.wander_interval:#if the zombie have wander for 2s then stop
                    self.is_wandering = False
                    self.last_wander_time = current_time
            else:
                self.is_moving = False
                if current_time - self.last_wander_time > self.pause_duration:
                    self.is_wandering = True
                    self.last_wander_time = current_time
                    self.wander_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]
                    length = math.hypot(*self.wander_direction)
                    if length != 0:
                        self.wander_direction[0] /= length
                        self.wander_direction[1] /= length#repeat the code again to let the zombie change the direction

        if self.is_moving:
            if time.time() - self.last_animation_time > self.animation_speed:
                self.animation_index = (self.animation_index + 1) % len(self.walk_images)
                self.image = self.walk_images[self.animation_index]
                self.last_animation_time = time.time()
        else:
            self.image = self.idle_image # Show idle frame

    def attack_player(self):
        self.player.take_damage(self.attack_damage)
        self.last_attack_time = time.time()
        print("Zombie attacks!")

    def take_damage(self, amount, attacker_pos=None):
        self.hp -= amount
        print(f"Zombie HP: {self.hp}")

        if attacker_pos is not None:#check the attacker position
            dx = self.rect.centerx - attacker_pos[0]
            dy = self.rect.centery - attacker_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
                knockback_distance = 20
                self.rect.x += dx * knockback_distance
                self.rect.y += dy * knockback_distance

        if self.hp <= 0:
            print("Zombie died!")
            self.kill()#attribute of sprite

    def draw_health_bar(self, surface):
        bar_width = 30
        bar_height = 5
        fill = (self.hp / self.max_hp) * bar_width
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 10
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, fill, bar_height))

# Create player
player = Player()

# Sprite groups
all_sprites = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()
all_sprites.add(player)

# Function to spawn zombies (limit to 10)
def spawn_zombie():
    if len(zombie_group) < 10:
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        zombie = Zombie(x, y, player)
        zombie_group.add(zombie)
        all_sprites.add(zombie)

# Timer for spawning zombies
spawn_delay = 3
last_spawn_time = time.time()

# Game loop
running = True
while running:
    screen.fill((50, 50, 50))
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if keys[pygame.K_SPACE] and player.can_attack():
            for zombie in zombie_group:
                if player.rect.colliderect(zombie.rect):
                    zombie.take_damage(20, player.rect.center)
                    player.last_attack_time = time.time()
                    break  # Only hit one zombie at a time


    current_time = time.time()
    if current_time - last_spawn_time >= spawn_delay and len(zombie_group) < 10:
        spawn_zombie()
        last_spawn_time = current_time

    player.update(keys)
    zombie_group.update()

    all_sprites.draw(screen)

    for zombie in zombie_group:
        zombie.draw_health_bar(screen)

    player.draw_health_bar(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
