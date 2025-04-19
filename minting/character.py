import pygame
import sys

pygame.init()

# Window setup
WIDTH, HEIGHT = 640, 480
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PAWLAND BOII")

# Load walking frames
walk_down = [pygame.image.load("minting/down1.png"),pygame.image.load("minting/down2.png"), pygame.image.load("minting/down1.png"),pygame.image.load("minting/down3.png")]
walk_up = [pygame.image.load("minting/up1.png"),pygame.image.load("minting/up2.png"),pygame.image.load("minting/up4.png")]
walk_left = [pygame.image.load("minting/L1.png"), pygame.image.load("minting/L2.png"),pygame.image.load("minting/L3.png"),pygame.image.load("minting/L4.png")]
walk_right = [pygame.image.load("minting/R0.png"),pygame.image.load("minting/R1.png"), pygame.image.load("minting/R2.png"),pygame.image.load("minting/R3.png")]

# Character position
x, y = 300, 200
speed = 4

# Animation control
frame = 0
direction = 'down'
moving = False
clock = pygame.time.Clock()

# Load a sample image
item_image = pygame.Surface((64, 64))
item_image.fill((255, 0, 0))  # Red block = item

 
# Main loop
running = True
while running:
    clock.tick(10)  # Limits the loop to 10 frames per second (controls animation speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_a]:
        x -= speed
        direction = 'left'
        moving = True
    elif keys[pygame.K_d]:
        x += speed
        direction = 'right'
        moving = True
    elif keys[pygame.K_w]:
        y -= speed
        direction = 'up'
        moving = True
    elif keys[pygame.K_s]:
        y += speed
        direction = 'down'
        moving = True

    # Choose frame based on direction and animation frame
    if direction == 'down':
        sprite = walk_down[frame % 2]
    elif direction == 'up':
        sprite = walk_up[frame % 2]
    elif direction == 'left':
        sprite = walk_left[frame % 2]
    elif direction == 'right':
        sprite = walk_right[frame % 2]

    # Update frame only when moving
    if moving:
        frame += 1
      
    # Redraw screen
    win.fill((230, 230, 255))
    win.blit(sprite, (x, y))
    pygame.display.update()

     

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
