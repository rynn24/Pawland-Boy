import pygame
import sys

pygame.init()

# Window setup

FRAME_WIDTH, FRAME_HEIGHT =200 , 200
WIDTH = 5 * FRAME_WIDTH  
HEIGHT = 4 * FRAME_HEIGHT  
win = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("PAWLAND BOY")

#Load the spriteseet
walk_sheet = pygame.image.load("minting/character.png").convert_alpha()
attack_sheet = pygame.image.load("minting/attack.png").convert_alpha()  # Attack spritesheet

# extract frames from row i the spritesheet
def load_frames(sheet , frame_width , frame_height , row , num_frames):
    frames = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, row * frame_height ,frame_width ,frame_height)
        frame = sheet.subsurface(rect)
        frames.append(frame)
    return frames

# Extract frames from the spritesheet
walk_down = load_frames(walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, row=0, num_frames=3)
walk_up = load_frames(walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, row=1, num_frames=4)
walk_left = load_frames(walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, row=2, num_frames=4)
walk_right = load_frames(walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, row=3, num_frames=4)

# Attack frames (from separate attack sprite sheet)
attack_right = load_frames(attack_sheet, FRAME_WIDTH, FRAME_HEIGHT, row=0, num_frames=4)
attack_left = load_frames(attack_sheet, FRAME_WIDTH, FRAME_HEIGHT, row=1, num_frames=4)


# Character position
x, y = 300, 200
speed = 9

# Animation control
frame = 0
attack_frame = 0
direction = 'down'
attacking = False
clock = pygame.time.Clock()

# Main loop
running = True
while running:
    clock.tick(15)  # Limits the loop to 15 frames per second (controls animation speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()
    moving = False

    # Start attack when space pressed (if not already attacking)
    if not attacking and keys[pygame.K_SPACE]:
        attacking = True
        attack_frame = 0

    if attacking:
        if direction == 'left':
            sprite = attack_left[attack_frame // 2]
        else:
            sprite = attack_right[attack_frame // 2]
        attack_frame += 1
        if attack_frame // 2 >= len(attack_right):
            attacking = False 
   
    else:    
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

  

        # Choose sprite based on direction
        if direction == 'down':
            sprite = walk_down[frame % len(walk_down)]
        elif direction == 'up':
            sprite = walk_up[frame % len(walk_up)]
        elif direction == 'left':
            sprite = walk_left[frame % len(walk_left)]
        elif direction == 'right':
            sprite = walk_right[frame % len(walk_right)]

        # Update frame
        if moving:
            frame += 1
        else:
            frame = 0  # reset to idle

    # Draw everything
    win.fill((230, 230, 255))
    win.blit(sprite, (x, y))
    pygame.display.update()

pygame.quit()
sys.exit()