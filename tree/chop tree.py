import pygame
import sys
import time

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

# Load tree sprite images
tree_image = pygame.image.load("Tree.png").convert_alpha()
tree_sprite_sheet = pygame.image.load("tree sprite.png").convert_alpha()
frame_width, frame_height = 100, 100
chop_frames = [
    tree_sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
    for i in range(tree_sprite_sheet.get_width() // frame_width)
]

# Load player image
player_img = pygame.image.load("minting/down1.png").convert_alpha()
player_rect = player_img.get_rect(center=(300, 300))

# Tree class
class Tree(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = tree_image
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.chopping = False
        self.chop_index = 0
        self.last_chop_time = 0
        self.chop_delay = 0.15
        self.regrow_time = 3
        self.hide_time = None
        self.alive = True

    def update(self):
        if self.chopping:
            now = time.time()
            if now - self.last_chop_time > self.chop_delay:
                self.chop_index += 1
                if self.chop_index < len(chop_frames):
                    self.image = chop_frames[self.chop_index]
                    self.last_chop_time = now
                else:
                    self.chopping = False
                    self.alive = False
                    self.image = pygame.Surface((0, 0))
                    self.hide_time = now

        elif not self.alive and self.hide_time and time.time() - self.hide_time > self.regrow_time:
            self.image = self.original_image
            self.chop_index = 0
            self.alive = True

    def start_chopping(self):
        if self.alive and not self.chopping:
            self.chopping = True
            self.chop_index = 0
            self.last_chop_time = time.time()

# Setup
trees = pygame.sprite.Group()
trees.add(Tree((200, 200)), Tree((400, 250)))

# Game loop
running = True
while running:
    dt = clock.tick(60) / 1000
    screen.fill((50, 180, 50))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            for tree in trees:
                if player_rect.colliderect(tree.rect.inflate(50, 50)):
                    tree.start_chopping()

    keys = pygame.key.get_pressed()
    speed = 150 * dt
    if keys[pygame.K_a]: player_rect.x -= speed
    if keys[pygame.K_d]: player_rect.x += speed
    if keys[pygame.K_w]: player_rect.y -= speed
    if keys[pygame.K_s]: player_rect.y += speed

    trees.update()
    trees.draw(screen)
    screen.blit(player_img, player_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
