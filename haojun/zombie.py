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
zombie_img = pygame.transform.scale(zombie_img, (64, 64))


def load_frames_from_sheet(sheet_path, frame_width, frame_height, rows, columns, resize_to=None):
    sheet = pygame.image.load(sheet_path).convert_alpha()
    frames = []

    for row in range(rows):
        row_frames = []
        for col in range(columns):
            x = col * frame_width
            y = row * frame_height
            frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
            if resize_to:
                frame = pygame.transform.scale(frame, resize_to)  # resize only if needed
            row_frames.append(frame)
        frames.append(row_frames)
    
    return frames  # e.g., frames[0] = walk, frames[1] = attack

zombie_walk_images =load_frames_from_sheet("haojun/image/zombie walk.png", 64, 64, 1, 5)[0]
boss_attack_frames = load_frames_from_sheet("haojun/image/boss attack.png", 96, 96, 1, 5)[0]
zombie_attack_images = load_frames_from_sheet("haojun/image/zombie attack.png", 64, 64,1, 4)[0]
zombie_die_images = load_frames_from_sheet("haojun/image/zombie get attack.png", 64, 64,1, 4)[0]
boss_walk_frames = load_frames_from_sheet("haojun/image/boss walk.png", 96, 96, 1, 3)[0]
boss_die_frames = load_frames_from_sheet("haojun/image/boss die.png", 96, 96, 1, 3)[0]
boss_ult_frames = load_frames_from_sheet("haojun/image/boss ult.png", 96, 96, 1, 6)[0]

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
        self.facing_left= False
        self.walk_images = zombie_walk_images
        self.image = self.walk_images[0]#set the zombie to the 1st walking frame
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_index = 0
        self.last_animation_time = time.time()
        self.animation_speed = 0.5  # Seconds between frames
        

        # Wandering
        self.is_wandering = True#need more explaination
        self.wander_direction = [random.uniform(-1, 1), random.uniform(-1, 1)]#the zombie can moving left right or up and down
        self.last_wander_time = time.time()#how long since last wander
        self.wander_interval = 2#how long should zombie wander
        self.pause_duration = 2#stop 2s after wandering

        self.attack_images = zombie_attack_images
        self.die_images = zombie_die_images

        self.state = "idle"  # could be "idle", "walk", "attack", "die"
        self.animation_index = 0
        self.last_animation_time = time.time()
        self.animation_speed = 0.2
        self.is_dead = False
        self.death_time = 0
        self.death_duration = 1  # 1 second to play die animation

    def update_facing_direction(self):
        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self):
        current_time = time.time()
        dx = self.player.rect.x - self.rect.x
        if dx < 0:
            self.facing_left = True
        else:
            self.facing_left = False
        dy = self.player.rect.y - self.rect.y
        dist = math.hypot(dx, dy)#hypothenuse
        

        chase_range = 200
        if self.state == "attack" and time.time() - self.last_attack_time < len(self.attack_images) * self.animation_speed:
            # During attack animation, don't move or switch states
            self.is_moving = False
            if time.time() - self.last_animation_time > self.animation_speed:
                self.animation_index += 1
                if self.animation_index < len(self.attack_images):
                    self.image = self.attack_images[self.animation_index]
                    self.update_facing_direction()
                else:
                    self.state = "walk"
                    self.animation_index = 0
                self.last_animation_time = time.time()
            return  # <--- Don't do anything else while attacking

        if self.is_dead:
            if time.time() - self.last_animation_time > self.animation_speed:
                self.animation_index += 1
                if self.animation_index < len(self.die_images):
                    self.image = self.die_images[self.animation_index]
                    self.update_facing_direction()
                else:
                    self.image = self.die_images[-1]
                self.last_animation_time = time.time()

            if time.time() - self.death_time > self.death_duration:
                self.kill()
            return

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
                self.update_facing_direction()
                self.last_animation_time = time.time()

        else:
            if self.state == "idle":
                self.image = self.idle_image  # Only set to idle image if actually idle
            elif self.state == "walk":
                if time.time() - self.last_animation_time > self.animation_speed:
                    self.animation_index = (self.animation_index + 1) % len(self.walk_images)
                    self.image = self.walk_images[self.animation_index]
                    self.update_facing_direction()
                    self.last_animation_time = time.time()
            elif self.state == "attack":
                if time.time() - self.last_animation_time > self.animation_speed:
                    self.animation_index += 1
                    if self.animation_index < len(self.attack_images):
                        self.image = self.attack_images[self.animation_index]
                        self.update_facing_direction()
                    else:
                        self.state = "walk"
                        self.animation_index = 0
                    self.last_animation_time = time.time()


    def attack_player(self):
        self.player.take_damage(self.attack_damage)
        self.last_attack_time = time.time()
        self.state = "attack"
        self.animation_index = 0
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

        if self.hp <= 0 and not self.is_dead:
            print("Zombie died!")
            self.state = "die"
            self.animation_index = 0
            self.is_dead = True
            self.death_time = time.time()

    def draw_health_bar(self, surface):
        bar_width = 30
        bar_height = 5
        fill = (self.hp / self.max_hp) * bar_width
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 10
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, fill, bar_height))

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, player, area_rect):
        super().__init__()
        self.walk_images = boss_walk_frames
        self.attack_images = boss_attack_frames
        self.ult_image = boss_ult_frames
        self.image = self.walk_images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.player = player
        self.area_rect = area_rect  # pygame.Rect defining movement area
        self.speed = 1
        self.attack_range = 40
        self.attack_damage = 20
        self.last_attack_time = 0
        self.attack_cooldown = 2
        self.hp = 200
        self.max_hp = 200
        self.attack_duration = 0.5  # seconds to show attack animation
        self.attack_animation_end_time = 0  # when the attack animation should stop
        self.state = "idle"  # or "walking", "attacking"
        self.animation_index = 0
        self.last_animation_time = time.time()
        self.animation_speed = 0.2
        self.attack_count = 0
        self.is_using_ult = False
        self.ult_frame_index = 0
        self.ult_timer = 0

    def update(self):
        self.facing_left = False
        current_time = time.time()
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # Check if we're still in attack animation lock
        if self.player.rect.centerx < self.rect.centerx:
            self.facing_left = True
        else:
            self.facing_left = False   
        if self.is_using_ult:
            self.state = "ult"
            if current_time > self.ult_end_time:
                self.is_using_ult = False
                self.state = "idle"
        elif current_time < self.attack_animation_end_time:#let the animation go more smooth
            self.state = "attacking"
        elif dist < 300:
            if dist == 0:
                dist = 1
            dx, dy = dx / dist, dy / dist
            new_x = self.rect.x + dx * self.speed
            new_y = self.rect.y + dy * self.speed

            if self.area_rect.collidepoint(new_x, new_y):#check if the boss can go
                self.rect.x = new_x
                self.rect.y = new_y

            if dist < self.attack_range and current_time - self.last_attack_time >= self.attack_cooldown:
                self.attack_player()
            self.state = "walking"
        else:
            self.state = "idle"
        if self.state == "ult":
            if time.time() > self.ult_end_time:
                self.state = "idle"

        # Animation update
        if time.time() - self.last_animation_time > self.animation_speed:#check if enough time to pass to next frame
            if self.state == "walking":
                self.animation_index = (self.animation_index + 1) % len(self.walk_images)
                self.image = self.walk_images[self.animation_index]
                image = self.walk_images[self.animation_index]
                if self.facing_left:
                     self.image = pygame.transform.flip(image, True, False)
                else:
                    self.image = image
                    self.rect = self.image.get_rect(center=self.rect.center)  # keep position consistent
            elif self.state == "attacking":
                self.animation_index = (self.animation_index + 1) % len(self.attack_images)
                image = self.attack_images[self.animation_index]
                self.image = pygame.transform.flip(image, True, False) if self.facing_left else image
                self.rect = self.image.get_rect(center=self.rect.center) 
            elif self.state == "ult":
                self.ult_frame_index += 1
                if self.ult_frame_index >= len(self.ult_image):
                    self.ult_frame_index = len(self.ult_image) - 1  # Stop at last frame
                    self.is_using_ult = False
                    self.state = "idle"
                image = self.ult_image[self.ult_frame_index]
                self.image = pygame.transform.flip(image, True, False) if self.facing_left else image

                if time.time() > self.ult_end_time:
                    self.state = "idle"
                    self.is_using_ult = False
            else:
                self.image = self.walk_images[0]
            self.last_animation_time = time.time()


    def attack_player(self):
        self.player.take_damage(self.attack_damage)
        self.last_attack_time = time.time()
        self.attack_animation_end_time = self.last_attack_time + self.attack_duration
        print("Boss attacks!")
        if not self.is_using_ult:
            # Normal attack
            self.attack_count += 1
            print(f"Boss normal attack ({self.attack_count})")
            
        if self.attack_count >= 5:
            self.trigger_ultimate()

    def take_damage(self, amount):
        self.hp -= amount
        print(f"Boss HP: {self.hp}")
        if self.hp <= 0:
            print("Boss defeated!")
            self.kill()

    def draw_health_bar(self, surface):
        bar_width = 100
        bar_height = 10
        fill = (self.hp / self.max_hp) * bar_width
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 15
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 0, 255), (x, y, fill, bar_height))
    
    def trigger_ultimate(self):
        self.is_using_ult = True
        print("BOSS ULTIMATE ATTACK!!!")
        self.ult_end_time = time.time() + 2  # 2 seconds for ult animation

        self.state = "ult"
        self.ult_frame_index = 0
        self.ult_timer = 0

        self.attack_count = 0


# Create player
player = Player()

# Sprite groups
all_sprites = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()
boss_area = pygame.Rect(0, 0, 400, 300)  # x, y, width, height
boss = Boss(50, 50, player, boss_area)
all_sprites.add(boss)
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
            else:
                # If no zombie was hit, check the boss
                if player.rect.colliderect(boss.rect):
                    boss.take_damage(20)
                    player.last_attack_time = time.time()


    current_time = time.time()
    if current_time - last_spawn_time >= spawn_delay and len(zombie_group) < 10:
        spawn_zombie()
        last_spawn_time = current_time

    player.update(keys)
    zombie_group.update()
    boss.update()
    boss.draw_health_bar(screen)
    pygame.draw.rect(screen, (255, 0, 0), boss_area, 2)  # Red outline, 2 pixels thick

    all_sprites.draw(screen)

    for zombie in zombie_group:
        zombie.draw_health_bar(screen)

    player.draw_health_bar(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()