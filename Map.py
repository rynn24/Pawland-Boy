import pygame
import os
import math

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Pawland Boy")
clock = pygame.time.Clock()

# Load assets
map_image = pygame.image.load(os.path.join("Map.png")).convert()

# Game settings
camera_width, camera_height = 640, 360
camera = pygame.Rect(0, 0, camera_width, camera_height)
zoom_surface = pygame.Surface((camera_width, camera_height))
player_position = pygame.Vector2(320, 180)
speed = 3
restricted_zones = [
    
]

# Day-night cycle
overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
time_counter = 0
cycle_speed = (2 * math.pi) / 30  # 30 second cycle

# Minimap settings
minimap_radius = 80
minimap_pos = (minimap_radius + 10, minimap_radius + 10)
minimap_zoom_factor = 1.5
minimap_border_color = (0, 0, 0)
minimap_border_width = 2
minimap_viewport_color = (255, 100, 100, 180)
player_minimap_color = (255, 50, 50)
minimap_mask = pygame.Surface((minimap_radius*2, minimap_radius*2), pygame.SRCALPHA)
pygame.draw.circle(minimap_mask, (255, 255, 255), (minimap_radius, minimap_radius), minimap_radius)

running = True
while running:
    dt = clock.tick(60) / 1000

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:  # Zoom in with '+'
                minimap_zoom_factor = min(4.0, minimap_zoom_factor + 0.1)
            elif event.key == pygame.K_MINUS:  # Zoom out with '-'
                minimap_zoom_factor = max(0.5, minimap_zoom_factor - 0.1)

    # Player movement
    new_position = player_position.copy()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: new_position.y -= speed
    if keys[pygame.K_s]: new_position.y += speed
    if keys[pygame.K_a]: new_position.x -= speed
    if keys[pygame.K_d]: new_position.x += speed

    # Boundary and collision
    new_position.x = max(0, min(new_position.x, map_image.get_width()))
    new_position.y = max(0, min(new_position.y, map_image.get_height()))
    player_rect = pygame.Rect(new_position.x - 2, new_position.y - 2, 4, 4)
    if not any(zone.colliderect(player_rect) for zone in restricted_zones):
        player_position = new_position

    # Camera update
    camera.center = player_position
    camera.clamp_ip(map_image.get_rect())

    # World view
    zoom_surface.blit(map_image, (0, 0), camera)
    zoomed_view = pygame.transform.scale(zoom_surface, screen.get_size())
    screen.blit(zoomed_view, (0, 0))

    # Player
    pygame.draw.circle(screen, (255, 0, 0), 
                     (screen.get_width() // 2, screen.get_height() // 2), 8)

    # -- MINIMAP RENDERING --
    minimap_surface = pygame.Surface((minimap_radius*2, minimap_radius*2), pygame.SRCALPHA)
    
    # Apply zoom factor
    scale = (minimap_radius * 2) / (max(map_image.get_width(), map_image.get_height()) / minimap_zoom_factor)
    scaled_width = int(map_image.get_width() * scale)
    scaled_height = int(map_image.get_height() * scale)
    
    scaled_map = pygame.transform.scale(map_image, (scaled_width, scaled_height))
    map_pos = ((minimap_radius*2 - scaled_width) // 2, 
              (minimap_radius*2 - scaled_height) // 2)
    minimap_surface.blit(scaled_map, map_pos)
    
    # Apply mask and draw elements
    masked_minimap = minimap_surface.copy()
    masked_minimap.blit(minimap_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    
    viewport_rect = pygame.Rect(
        map_pos[0] + camera.x * scale,
        map_pos[1] + camera.y * scale,
        camera.width * scale,
        camera.height * scale
    )
    pygame.draw.rect(masked_minimap, minimap_viewport_color, viewport_rect, 1)
    
    player_pos = (
        map_pos[0] + player_position.x * scale,
        map_pos[1] + player_position.y * scale
    )
    pygame.draw.circle(masked_minimap, player_minimap_color, player_pos, 3)
    pygame.draw.circle(masked_minimap, minimap_border_color, 
                      (minimap_radius, minimap_radius), minimap_radius, minimap_border_width)
    
    screen.blit(masked_minimap, (minimap_pos[0] - minimap_radius, minimap_pos[1] - minimap_radius))

    # Day-night overlay
    time_counter += dt
    alpha = int((math.sin(time_counter * cycle_speed) + 1) / 2 * 150)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))

    pygame.display.flip()

pygame.quit()