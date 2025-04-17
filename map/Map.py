import pygame
import os
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((640, 360))
pygame.display.set_caption("Pawland Boy")
clock = pygame.time.Clock()

# Load map 
map_path = os.path.join("map","map.png")
map_image = pygame.image.load(map_path).convert()

# Zoom settings
camera_width, camera_height =  160, 90
camera = pygame.Rect(0, 0, camera_width, camera_height)
zoom_surface = pygame.Surface((camera_width, camera_height))

# Player position
player_position = pygame.Vector2(200, 150)
speed = 2

# Restricted zones: more on left, water areas restricted, sand (top) not restricted
restricted_zones = [
    # Pond area (bottom-center right)
    pygame.Rect(360, 260, 60, 60),
    # Bottom left sea
    pygame.Rect(0, 440, 150, 40),
    # Left sea/blue edge
    pygame.Rect(0, 160, 50, 250),
    # Top-left blue water patch
    pygame.Rect(0, 0, 40, 100),
    # Far bottom-right blue edge
    pygame.Rect(600, 400, 40, 80),
    # Right-mid blue strip
    pygame.Rect(580, 180, 60, 140),
]

# Day-night overlay surface
overlay = pygame.Surface(screen.get_size()).convert_alpha()

# Day-night cycle timer (30s full cycle)
time_counter = 0
cycle_speed = (2 * math.pi) / 30  # 1 full sine wave every 30 seconds

running = True
while running:
    dt = clock.tick(60) / 1000  # Seconds per frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Store current position to test collision
    new_position = player_position.copy()

    # Player Movement Input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        new_position.y -= speed
    if keys[pygame.K_s]:
        new_position.y += speed
    if keys[pygame.K_a]:
        new_position.x -= speed
    if keys[pygame.K_d]:
        new_position.x += speed

    # Clamp to map boundaries
    new_position.x = max(0, min(new_position.x, map_image.get_width()))
    new_position.y = max(0, min(new_position.y, map_image.get_height()))

    # Collision check with restricted zones
    player_rect = pygame.Rect(new_position.x - 2, new_position.y - 2, 4, 4)
    if not any(zone.colliderect(player_rect) for zone in restricted_zones):
        player_position = new_position  # update only if safe

    # Camera Update
    camera.center = player_position
    camera.clamp_ip(map_image.get_rect())

    # Draw Zoomed View
    zoom_surface.blit(map_image, (0, 0), camera)
    zoomed_view = pygame.transform.scale(zoom_surface, screen.get_size())
    screen.blit(zoomed_view, (0, 0))

    # Draw Player (center of screen) 
    pygame.draw.circle(screen, (255, 0, 0), (screen.get_width() // 2, screen.get_height() // 2), 5)

    # Day-Night Cycle
    time_counter += dt
    alpha = int((math.sin(time_counter * cycle_speed) + 1) / 2 * 150)  # range 0–150
    overlay.fill((0, 0, 0, alpha))  # Black overlay with variable transparency
    screen.blit(overlay, (0, 0))

    # Update Display
    pygame.display.flip()

pygame.quit()
