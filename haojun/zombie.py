import pygame
import os
import math
import sys
import random
import time
import json

# Initialize
pygame.init()
window_size = (620, 480)
is_fullscreen = False
screen = pygame.display.set_mode(window_size)
overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
pygame.display.set_caption("Pawland Boy")
clock = pygame.time.Clock()

# Scaling variables
character_scale = 1.0  # Normal size
fullscreen_scale = 2.0  # Scale factor when in fullscreen

# fonts
font = pygame.font.SysFont(None, 24)
reward_font = pygame.font.Font(None, 45) # font for fishing reward

# Load map image
map_image = pygame.image.load(os.path.join("rynn/Map.png")).convert()

# Load abandoned house image
house_image = pygame.image.load("rynn/house.png").convert_alpha()
house_rect = house_image.get_rect(topleft=(1500, 125))

inside_house_image = pygame.image.load("rynn/inside-house.jpg").convert()
inside_house = False

# Camera and player position 
camera_width, camera_height = 320, 180
camera = pygame.Rect(0, 0, camera_width, camera_height)
zoom_surface = pygame.Surface((camera_width, camera_height))
player_position = pygame.Vector2(1500, 125)
speed = 2

# Player restricted area
restricted_zones = [
    # Pond area
    {
        "type": "ellipse",
        "center": (1554, 585),
        "radius_x": 165,
        "radius_y": 162
    },
        {
        "type": "rect",
        "rect": pygame.Rect(753, 0, 440, 275)  # x, y, width, height
    }   
] 

# Trees restricted area
tree_restricted_zones = [
    # Pond area 
    {
        "type": "ellipse",
        "center": (1554, 585),
        "radius_x": 165,
        "radius_y": 162
    },
    # Boss & top water area 
    {
        "type": "rect",
        "rect": pygame.Rect(0, 0, 1500, 340)  # x, y, width, height
    }
]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)

def  login_menu(user_system) :

    while True:
        print("=== Welcome to Pawland Boy ===")
        print("1. Open new profile")
        print("2. Enter profile")
        print("3. Quit")
        choice = input("Choose an option: ")

        if choice == "1":
            username = input("New Username: ")
            if user_system.register(username):
                print("Successfully create new profile!")
            else:
                print("Username already exists.")
        elif choice == "2":
            print("Available profiles:")
            for profile_name in user_system.users.keys():
                print(f"- {profile_name}")

            username = input("Enter username: ")
            if username in user_system.users:
                user_system.current_user = username
                print(f"Profile '{username}' loaded.")
                health, position, inventory = user_system.get_player_data(username)
                return username
            else:
                print("Profile not found.")
        elif choice == "3":
            quit()
        else:
            print("Invalid choice.") 


def scale_sprite(sprite, scale):
    if scale == 1.0:
        return sprite  # No scaling needed
    original_size = sprite.get_size()
    new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
    return pygame.transform.scale(sprite, new_size)

def is_in_ellipse(point, center, radius_x, radius_y):
    px, py = point
    cx, cy = center
    dx = (px - cx) ** 2 / (radius_x ** 2)
    dy = (py - cy) ** 2 / (radius_y ** 2)
    result = dx + dy <= 1
    return result

def is_in_restricted_zone(point, zones):
    for zone in zones:
        if zone["type"] == "ellipse":
            if is_in_ellipse(point, zone["center"], zone["radius_x"], zone["radius_y"]):
                return True
        elif zone["type"] == "rect":
            rect = pygame.Rect(*zone["rect"])
            if rect.collidepoint(point):
                return True
    return False

# For trees restricted zone
def is_valid_tree_position(pos, restricted_zones):
    for zone in restricted_zones:
        if zone["type"] == "ellipse":
            if is_in_ellipse(pos, zone["center"], zone["radius_x"], zone["radius_y"]):
                return False  # Tree cannot grow here
        elif zone["type"] == "rect":
            if zone["rect"].collidepoint(pos):
                return False  # Tree cannot grow here
    return True  

# Day-night cycle
cycle_duration = 60  # 60 seconds total for one full cycle
day_duration = cycle_duration * 0.66  # 66% day → 39.6 seconds
night_duration = cycle_duration * 0.34  # 34% night → 20.4 seconds
time_counter = 0


# Minimap settings
minimap_radius = 60
minimap_zoom_factor = 0.8
minimap_pos = (minimap_radius + 10, minimap_radius + 10)
minimap_border_color = (0, 0, 0)
minimap_border_width = 2
player_minimap_color = (255, 50, 50)
minimap_mask = pygame.Surface((minimap_radius * 2, minimap_radius * 2), pygame.SRCALPHA)
pygame.draw.circle(minimap_mask, (255, 255, 255), (minimap_radius, minimap_radius), minimap_radius)

FRAME_WIDTH, FRAME_HEIGHT = 200, 200

def load_frames(sheet, frame_width, frame_height, row, num_frames, spacing=0):
    return [sheet.subsurface(pygame.Rect(i * frame_width, row * frame_height, frame_width, frame_height)) for i in range(num_frames)]

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

zombie_img = pygame.image.load("haojun/image/zombie.png").convert_alpha()  # <--- STEP 1
zombie_img = pygame.transform.scale(zombie_img, (46, 46))
zombie_attack_images = load_frames_from_sheet("haojun/image/zombie attack.png", 46, 46,1, 4)[0]
zombie_die_images = load_frames_from_sheet("haojun/image/zombie get attack.png", 46, 46,1, 4)[0]
zombie_walk_images =load_frames_from_sheet("haojun/image/zombie walk.png", 46, 46, 1, 5)[0]
boss_attack_frames = load_frames_from_sheet("haojun/image/boss attack.png", 76, 76, 1, 5)[0]
boss_walk_frames = load_frames_from_sheet("haojun/image/boss walk.png", 76, 76, 1, 3)[0]
boss_die_frames = load_frames_from_sheet("haojun/image/boss die.png", 76, 76, 1, 4)[0]
boss_ult_frames = load_frames_from_sheet("haojun/image/boss ult.png", 76, 76, 1, 6)[0]


class Inventory:
    def __init__(self, max_slots=20):
        self.items = {}
        self.max_slots = max_slots
        self.slots = [None] * max_slots  # Initial empty slots
        self.slot_rects = []
        self.font = pygame.font.SysFont("Arial", 20)
        self.item_icons = {
                "Wood": pygame.image.load("minting/Wood.png").convert_alpha(),
                "Fruit": pygame.image.load("minting/Fruit.png").convert_alpha(),
                "Fish": pygame.image.load("minting/fish_1.png").convert_alpha(),
                "Big Fish": pygame.image.load("minting/Fish_2.png").convert_alpha(),
                "Crystal": pygame.image.load("minting/Crystal.png").convert_alpha(),
                "Boat": pygame.image.load("minting/Boat.png").convert_alpha(),
                "Firefly": pygame.image.load("minting/Firefly.jpg").convert_alpha(),
            }
        self.slot_size = 60
        self.slot_margin = 10
        self.is_inventory_open = False  # Track whether inventory is open

        # Increase the size of the inventory window for better spacing
        self.window_width = 5.4 * (self.slot_size + self.slot_margin) + self.slot_margin  # 5 columns of slots + margin
        self.window_height = 4.4 * (self.slot_size + self.slot_margin) + self.slot_margin  # 4 rows of slots + margin
        self.window_rect = pygame.Rect(50, 100, self.window_width, self.window_height)  # Position and size of the window (stick to the left)
        self.window_color = (139, 69, 19)  # Brown color for the window (wood-like)

        # Define positions of the 5 visible slots (always on the screen)
        self.visible_slots_rects = []
        self.visible_slots_x = (800 - 5 * (self.slot_size + self.slot_margin)) // 2  # Centered on top
        self.visible_slots_y = 50  # Start y position for visible slots
        self.generate_slot_rects()

    def generate_slot_rects(self):
        """Generate the positions for all the inventory slots"""
        self.slot_rects = []

        # After the window is positioned on the left, calculate the positions for the slots
        start_x = self.window_rect.x + 20  # Position slots inside window starting with a margin from the left
        start_y = self.window_rect.y + 20  # Position slots inside window starting with a margin from the top

        # Calculate the positions for each of the 20 slots (5 columns x 4 rows)
        for i in range(self.max_slots):
            x = start_x + (i % 5) * (self.slot_size + self.slot_margin)  # 5 slots per row
            y = start_y + (i // 5) * (self.slot_size + self.slot_margin)  # Stack 4 rows
            self.slot_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

        # Define the visible slots (always on the screen)
        self.visible_slots_rects = []
        for i in range(5):  # Just 5 visible boxes at the top of the screen
            x = self.visible_slots_x + (i % 5) * (self.slot_size + self.slot_margin)
            y = self.visible_slots_y
            self.visible_slots_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def toggle_inventory(self):
        """Toggle the inventory screen (open/close)"""
        self.is_inventory_open = not self.is_inventory_open

    def draw(self, surface):
        """Draw the inventory window and slots"""
        # Draw the visible 5 slots (always on screen)
        for i, rect in enumerate(self.visible_slots_rects):
            pygame.draw.rect(surface, (200, 200, 200), rect)

            item = self.slots[i]
            if item:
                name, count = item
                self.draw_item_icon(surface, name, count, rect)  # 🎯 Draw icon + count


        # Draw the inventory window when it is open
        if self.is_inventory_open:
            # Draw the window background (wooden texture/solid color)
            pygame.draw.rect(surface, self.window_color, self.window_rect)

            # Draw the slots inside the window
            for rect in self.slot_rects:
                pygame.draw.rect(surface, (200, 200, 200), rect)  # Draw slot box (gray)
                item = self.slots[self.slot_rects.index(rect)]
                if item:
                    name, count = item
                    self.draw_item_icon(surface, name, count, rect)

    def add_item(self, name, count):
        """Add or combine an item into the inventory"""

        # 1. Try to find and combine with existing item of same name
        for i in range(self.max_slots):
            item = self.slots[i]
            if item is not None and item[0] == name:
                current_name, current_count = item
                self.slots[i] = (current_name, current_count + count)
                return True

        # 2. If not found, find an empty slot to insert
        for i in range(self.max_slots):
            if self.slots[i] is None:
                self.slots[i] = (name, count)
                return True

        # 3. Inventory full
        return False

    def draw_item_icon(self, surface, name, count, rect):
        if name in self.item_icons:
            icon = self.item_icons[name]
            icon = pygame.transform.smoothscale(icon, (self.slot_size - 10, self.slot_size - 10))  # Auto resize
            icon_rect = icon.get_rect(center=rect.center)
            surface.blit(icon, icon_rect)

            # Draw item count
            count_text = self.font.render(f"x{count}", True, (0, 0, 0))
            count_rect = count_text.get_rect(bottomright=(rect.right - 4, rect.bottom - 2))
            surface.blit(count_text, count_rect)
            
    def get_inventory_dict(self):
        """Return inventory as a dictionary for saving purposes."""
        data = {}
        for slot in self.slots:
            if slot:
                item_name, item_count = slot
                data[item_name] = item_count  # Store just the name and count
        return data

    
    def set_items(self, items_dict):
        """Load saved items into the inventory"""
        self.slots = [None] * self.max_slots
        index = 0
        for name, count in items_dict.items():
            if index < self.max_slots:
                self.slots[index] = (name, count)
                index += 1


class UserSystem:
    def __init__(self, filename="profile.json"):
        self.filename = filename
        self.users = self.load_users()
        self.current_user = None

    def save_users(self):
        try:
            # Test if the data is serializable
            json.dumps(self.users)  # This will raise TypeError if anything is unserializable
            with open(self.filename, "w") as f:
                json.dump(self.users, f)
            print("✅ Users saved successfully.")
        except TypeError as e:
            print("❌ Serialization error! Non-serializable object found:")
            print(e)

            import pprint
            pprint.pprint(self.users)  # Pretty print for easier debugging

            # Optional: show exactly which part failed
            self.inspect_for_unserializables(self.users)

    def inspect_for_unserializables(self, data, path="root"):
        if isinstance(data, dict):
            for key, value in data.items():
                self.inspect_for_unserializables(value, f"{path}['{key}']")
        elif isinstance(data, list):
            for index, item in enumerate(data):
                self.inspect_for_unserializables(item, f"{path}[{index}]")
        else:
            try:
                json.dumps(data)
            except TypeError:
                print(f"❗ Unserializable data at {path}: {type(data)} -> {repr(data)}")


    def load_users(self):
        if not os.path.exists(self.filename):
            return {}
        with open(self.filename, "r") as f:
            return json.load(f)
        
    def register(self, username):
        if username in self.users:
            return False  # Username taken
        # Store initial player data
        self.users[username] = {
            "health": 100,  # Initial health
            "position": [1500,125],  # Initial position (center of screen)
            "inventory": {
                "sword": 1,  # Starting item
            }
        }
        self.save_users()
        return True

    def login(self, username):
        if username in self.users :
            self.current_user = username
            return True
        return False

    def logout(self):
        self.current_user = None

    def get_player_data(self, username):
        if username not in self.users:
            print(f"Error: User '{username}' not found in users database!")  # More descriptive error
            return 100, pygame.Vector2(1500, 125), {}  # Default values, but now you know the user is missing
        
        user_data = self.users.get(username, {})
        health = user_data.get("health", 100)
        position = user_data.get("position", [1500, 125])
        inventory = user_data.get("inventory", {})
    
        if isinstance(position, dict):
            position = [position.get("0", 1500), position.get("1", 125)]

        return health, position, inventory

    def get_inventory_dict(self, username):
        inventory = self.users[username]["inventory"]
        inventory_dict = {}

        # Ensure we are iterating correctly based on the inventory structure
        for item_name, item_data in inventory.items():
            if isinstance(item_data, tuple) or isinstance(item_data, list):
                # Handle if the item data is a tuple or list (e.g., item count might be the first element)
                item_count = item_data[0]  # assuming the first element is the count
                inventory_dict[item_name] = item_count
            else:
                # If it's just a simple count value
                inventory_dict[item_name] = item_data

        return inventory_dict

    def save_progress(self, username, health, position, inventory_dict):
        if username in self.users:
            # Ensure position is serializable (convert pygame.Vector2 to list)
            if isinstance(position, pygame.Vector2):
                position = [position.x, position.y]  # Convert to list
            
            self.users[username]["health"] = health
            self.users[username]["position"] = position  # Store position as a list
            self.users[username]["inventory"] = inventory_dict
            print(f"Updated inventory for {username}: {self.users[username]['inventory']}")  # Debugging line
            self.save_users()



class SettingsMenu:
    def __init__(self):
        self.visible = False
        self.buttons = []
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Initialize music
        pygame.mixer.init()
        try:
            self.music = pygame.mixer.Sound("haojun/music.mp3")  # Replace with your music file
            self.music_volume = 0.5  # Default volume (0.0 to 1.0)
            self.music.play(-1)  # Loop indefinitely
            self.music.set_volume(self.music_volume)
        except:
            self.music = None
            print("Could not load music file")
        
        # Create buttons
        self.create_buttons()
    
    def create_buttons(self):
        # Quit button
        quit_button = Button(
            window_size[0]//2 - 100, window_size[1]//2 + 60,
            200, 40, "Quit Game",
            (200, 50, 50), (250, 100, 100), (255, 255, 255)
        )
        self.buttons.append(quit_button)
        
        # Back button
        back_button = Button(
            window_size[0]//2 - 100, window_size[1]//2 + 10,
            200, 40, "Back to Game",
            (50, 50, 200), (100, 100, 250), (255, 255, 255)
        )
        self.buttons.append(back_button)
    
    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            button.check_hover(mouse_pos)
            if button.is_clicked(mouse_pos, event):
                if button.text == "Quit Game":
                    return "quit"
                elif button.text == "Back to Game":
                    self.visible = False
                    return "back"
        
        # Handle volume keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.adjust_volume(-0.1)
            elif event.key == pygame.K_RIGHT:
                self.adjust_volume(0.1)
    
    def adjust_volume(self, change):
        self.music_volume = max(0.0, min(1.0, self.music_volume + change))
        if self.music:
            self.music.set_volume(self.music_volume)
    
    def draw(self, screen):
        # Darken the background
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw menu box
        menu_rect = pygame.Rect(
            window_size[0]//2 - 200, window_size[1]//2 - 150,
            400, 300
        )
        pygame.draw.rect(screen, (100, 100, 100), menu_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), menu_rect, 2, border_radius=10)
        
        # Draw title
        title = self.font.render("Settings", True, (255, 255, 255))
        screen.blit(title, (window_size[0]//2 - title.get_width()//2, window_size[1]//2 - 120))
        
        # Draw volume controls
        vol_text = self.font.render(f"Music Volume: {int(self.music_volume * 100)}%", True, (255, 255, 255))
        screen.blit(vol_text, (window_size[0]//2 - vol_text.get_width()//2, window_size[1]//2 - 60))
        
        controls_text = self.small_font.render("Use LEFT/RIGHT arrows to adjust", True, (200, 200, 200))
        screen.blit(controls_text, (window_size[0]//2 - controls_text.get_width()//2, window_size[1]//2 - 30))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont(None, font_size)
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=5)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False
    
class Player:
    def __init__(self, position, speed, username):
        self.username = username
        self.user_system = UserSystem()
        self.health, self.position, self.inventory = self.user_system.get_player_data(self.username)
        self.position = pygame.Vector2(self.position[0], self.position[1])
        self.speed = speed 
        if isinstance(self.position, list) or isinstance(self.position, tuple):
            self.position = pygame.Vector2(self.position[0], self.position[1])

        self.image = pygame.image.load("minting/character.png").convert_alpha()
        self.rect = self.image.get_rect(center=(self.position.x, self.position.y))
        
        self.direction = 'down'
        self.attacking = False
        self.frame = 0
        self.attack_frame = 0
        self.last_frame_time = 0
        self.frame_speed = 0.1
        self.attack_frame_delay = 3
        self.attack_frame_counter = 0
        self.weapons = ['hand', 'axe', 'sword']
        self.current_weapon = 'hand'
        self.last_update = pygame.time.get_ticks()
        self.animation_cooldown = 100
        
        self.current_attack_targets = []

        self.weapon_icons = {
            "sword": pygame.image.load("minting/sword.png").convert_alpha(),
            "axe": pygame.image.load("minting/axe.png").convert_alpha(),
            "hand": pygame.image.load("minting/hand.png").convert_alpha()
        }

        self.weapon_damage = {
            'hand': 5,
            'axe': 15,
            'sword': 10
        }
        
        self.weapon_range = {
            'hand': 30,
            'axe': 40,
            'sword': 50
        }


        # Fixed HP Bar Loading (330x30 sprite sheet with 5 frames)

        self.hp_frames = {
            100:pygame.image.load("haojun/image/hp.100.png").convert_alpha(),
            90: pygame.image.load("haojun/image/hp.90.png").convert_alpha(),
            80: pygame.image.load("haojun/image/hp.80.png").convert_alpha(),
            70: pygame.image.load("haojun/image/hp.70.png").convert_alpha(),
            60: pygame.image.load("haojun/image/hp.60.png").convert_alpha(),
            50: pygame.image.load("haojun/image/hp.50.png").convert_alpha(),
            40: pygame.image.load("haojun/image/hp.40.png").convert_alpha(),
            30: pygame.image.load("haojun/image/hp.30.png").convert_alpha(),
            20: pygame.image.load("haojun/image/hp.20.png").convert_alpha(),
            10: pygame.image.load("haojun/image/hp.10.png").convert_alpha(),
            0 : pygame.image.load("haojun/image/hp.0.png").convert_alpha(),
        }

        self.walk_sheet = pygame.image.load("minting/character.png").convert_alpha()
        self.walk_down = load_frames(self.walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, 0, 3)
        self.walk_up = load_frames(self.walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, 1, 4)
        self.walk_left = load_frames(self.walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, 2, 4)
        self.walk_right = load_frames(self.walk_sheet, FRAME_WIDTH, FRAME_HEIGHT, 3, 4)
       
        self.attack_sheets = {
            'hand': pygame.image.load("minting/hand_attack.png").convert_alpha(),
            'axe': pygame.image.load("minting/axe_attack.png").convert_alpha(),
            'sword': pygame.image.load("minting/sword_attack.png").convert_alpha()
        }
        
        self.attack_frames = {
            'hand': {
                'right': load_frames(self.attack_sheets['hand'], FRAME_WIDTH, FRAME_HEIGHT, 0, 2),
                'left': load_frames(self.attack_sheets['hand'], FRAME_WIDTH, FRAME_HEIGHT, 1, 2)
            },
            'axe': {
                'right': load_frames(self.attack_sheets['axe'], FRAME_WIDTH, FRAME_HEIGHT, 0, 2),
                'left': load_frames(self.attack_sheets['axe'], FRAME_WIDTH, FRAME_HEIGHT, 1, 2)
            },
            'sword': {
                'right': load_frames(self.attack_sheets['sword'], FRAME_WIDTH, FRAME_HEIGHT, 0, 4),
                'left': load_frames(self.attack_sheets['sword'], FRAME_WIDTH, FRAME_HEIGHT, 1, 4)
            }
        }

    def move(self, keys, dt):
        move_distance = self.speed * dt 
        moving = False
        direction_vector = pygame.math.Vector2(0, 0)

        if self.attacking:
            self.rect.center = (self.position.x, self.position.y)
            return self.position, self.get_attack_sprite()

        if keys[pygame.K_w]:
            self.position.y -= move_distance
            self.direction = 'up'
            moving = True
        if keys[pygame.K_s]:
            self.position.y += move_distance
            self.direction = 'down'
            moving = True
        if keys[pygame.K_a]:
            self.position.x -= move_distance
            self.direction = 'left'
            moving = True
        if keys[pygame.K_d]:
            self.position.x += move_distance
            self.direction = 'right'
            moving = True
        
        if moving:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_frame_time > self.frame_speed * 1000:
                self.frame += 1
                self.last_frame_time = current_time
            
            current_sprite = self.get_current_sprite()
        else:
            current_sprite = self.walk_down[0]
        self.rect.center = (self.position.x, self.position.y)
        return self.position, current_sprite
    
    def switch_weapon(self, key):
        if key == pygame.K_TAB:
            current_index = self.weapons.index(self.current_weapon)
            next_index = (current_index + 1) % len(self.weapons)
            self.current_weapon = self.weapons[next_index]

    def attack(self, trees, zombies):
        if not self.attacking:
            self.current_attack_targets.clear()
            return None

        if self.attack_frame_counter >= self.attack_frame_delay:
            self.attack_frame += 1
            self.attack_frame_counter = 0
        else:
            self.attack_frame_counter += 1

        sprite = self.get_attack_sprite()

        current_attack_frames = self.attack_frames[self.current_weapon]

        if self.direction == 'left':
            max_frames = len(current_attack_frames['left'])
        else:
            max_frames = len(current_attack_frames['right'])

        if self.attack_frame // 2 >= max_frames:
            self.attacking = False
            self.attack_frame = 0
            self.current_attack_targets.clear()
            return None

        if self.attack_frame // 2 == 1:
            attack_rect = self.get_attack_rect(50)

            if self.current_weapon == 'axe':
                for tree in trees + trees_2:
                    if attack_rect.colliderect(tree.get_hitbox()) and not tree.was_hit:
                        tree.start_animation()
                        tree.was_hit = True
                        # Add wood to inventory
                        inventory.add_item("Wood", 1)
                        
                        # If it's from trees_2
                        if tree in trees_2:
                            inventory.add_item("Fruit", 1)

                        tree.update(pygame.time.get_ticks() / 1000)

            if self.current_weapon == 'sword':
                for zombie in zombies:
                    if attack_rect.colliderect(zombie.rect) and zombie not in self.current_attack_targets:
                        damage = self.weapon_damage[self.current_weapon]
                        zombie.take_damage(damage, self.position)
                        self.current_attack_targets.append(zombie)
            else:
                if not self.current_attack_targets:
                    for zombie in zombies:
                        if attack_rect.colliderect(zombie.rect):
                            damage = self.weapon_damage[self.current_weapon]
                            zombie.take_damage(damage, self.position)
                            self.current_attack_targets.append(zombie)
                            break

            if attack_rect.colliderect(boss.rect) and boss not in self.current_attack_targets:
                damage = self.weapon_damage[self.current_weapon]
                boss.take_damage(damage)
                self.current_attack_targets.append(boss)

        return sprite
    
    def get_attack_sprite(self):
        idx = self.attack_frame // 2
        max_idx = len(self.attack_frames[self.current_weapon]['right']) - 1
        idx = min(idx, max_idx)
        
        if self.direction == 'left':
            return self.attack_frames[self.current_weapon]['left'][idx]
        else:
            return self.attack_frames[self.current_weapon]['right'][idx]
    
    def get_attack_rect(self, range):
        range = int(range * character_scale)
        size = int(40 * character_scale)
        
        if self.direction == 'up':
            return pygame.Rect(self.position.x - size//2, self.position.y - range, size, range)
        elif self.direction == 'down':
            return pygame.Rect(self.position.x - size//2, self.position.y, size, range)
        elif self.direction == 'left':
            return pygame.Rect(self.position.x - range, self.position.y - size//2, range, size)
        elif self.direction == 'right':
            return pygame.Rect(self.position.x, self.position.y - size//2, range, size)

    def get_current_sprite(self):
        sprite_list = {
            'up': self.walk_up,
            'down': self.walk_down,
            'left': self.walk_left,
            'right': self.walk_right
        }[self.direction]

        self.frame %= len(sprite_list)
        return sprite_list[self.frame]

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw_health_bar(self, surface):
        bar_width = 200
        bar_height = 20
        x = (surface.get_width() - bar_width) // 2
        y = surface.get_height() - bar_height - 10  # Bottom of screen


        # Round to nearest 10
        hp_level = max(0, min(100, int(round(self.health / 10) * 10)))
        current_frame = self.hp_frames.get(hp_level, self.hp_frames[0])

        # No need to scale unless needed
        # If too small visually, you can still scale like this:
        scale_factor = 2
        scaled_frame = pygame.transform.scale(current_frame, (
            current_frame.get_width() * scale_factor,
            current_frame.get_height() * scale_factor
        ))

        x = (surface.get_width() - scaled_frame.get_width()) // 2
        y = surface.get_height() - scaled_frame.get_height() + 60
        surface.blit(scaled_frame, (x, y))

        # HP number
        health_text = font.render(f"{int(self.health)}/100", True, (255, 255, 255))
        text_x = x + scaled_frame.get_width() + 10
        text_y = y + (scaled_frame.get_height() - health_text.get_height()) // 2
        surface.blit(health_text, (text_x, text_y))
        

        # Load sprite sheet

    def load_frames(self):
        frame_width = self.spritesheet.get_width() // self.cols
        frame_height = self.spritesheet.get_height() // self.rows
        frames = []
        for row in range(self.rows):
            for col in range(self.cols):
                frame = self.spritesheet.subsurface(
                    pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                )
                frames.append(frame)
        return frames

    def is_player_inside(self, player_pos):
        dx = (player_pos[0] - self.center[0]) / self.detection_radius_x
        dy = (player_pos[1] - self.center[1]) / self.detection_radius_y
        return dx * dx + dy * dy <= 1

    def update(self, player_pos, keys):
        if self.is_player_inside(player_pos) and keys[pygame.K_j]:
            self.show_animation = True
            self.current_frame = 0  # Restart animation

        if self.show_animation:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_delay:
                self.current_frame += 1
                self.last_update = now
                if self.current_frame >= len(self.frames):
                    self.current_frame = 0
                    self.show_animation = False  # Stop after one loop

    def draw(self, screen):
        if self.show_animation:
            frame = self.frames[self.current_frame]
            scaled_frame = pygame.transform.scale(frame, screen.get_size())
            screen.blit(scaled_frame, (0, 0))

user_system = UserSystem()  # Create UserSystem instance
current_user = login_menu(user_system)  # Get current user (should return a string)
speed = 2.5  # Adjust as needed
player_position = pygame.Vector2(1500, 125)
player_instance = Player(player_position, speed, current_user)  # Create Player instance


class Tree:
    def __init__(self, position, frames):
        self.position = pygame.Vector2(position)
        self.frames = frames
        self.index = 0
        self.animating = False
        self.animation_speed = 0.2
        self.last_update_time = 0
        self.hold_duration = 10
        self.hold_start_time = 0
        self.is_holding = False
        self.frame_width = 100
        self.frame_height = 100

        self.was_hit = False  # To track if the tree has been hit
        self.hit_timer = 0  # Timer for cooldown
        self.hit_cooldown = 0.3  # cooldown before tree can be hit again

        
    def start_animation(self):
        if not self.animating and not self.is_holding:
            self.animating = True
            self.index = 0
            self.last_update_time = pygame.time.get_ticks() / 1000

    def update(self, current_time):
        if self.animating:
            if current_time - self.last_update_time > self.animation_speed:
                self.index += 1
                self.last_update_time = current_time
                if self.index >= 6:
                    self.index = 6
                    self.animating = False
                    self.is_holding = True
                    self.hold_start_time = current_time
        elif self.is_holding:
            if current_time - self.hold_start_time > self.hold_duration:
                self.is_holding = False
                self.index = 0
                self.index = 0
                self.was_hit = False  # reset hit status


        if self.was_hit:
            self.hit_timer += current_time - self.last_update_time
            if self.hit_timer >= self.hit_cooldown:
                self.was_hit = False  # Reset after cooldown
                self.hit_timer = 0  # Reset the timer



    def get_hitbox(self):
        hitbox_height = 20
        return pygame.Rect(
            self.position.x + 20,
            self.position.y + 100 - hitbox_height,
            100 - 40,
            hitbox_height
        )

    def draw(self, surface, camera):
        pos_on_surface = self.position - pygame.Vector2(camera.topleft)
        surface.blit(self.frames[self.index], pos_on_surface)

# Regular trees (wood only)
tree_sheet = pygame.image.load("rynn/tree-new.png").convert_alpha()
tree_frames = load_frames(tree_sheet, 100, 100, 0, 7, spacing=5)
trees = []
for _ in range(20):
    valid_position = False
    attempts = 0
    while not valid_position and attempts < 100:  # Try 100 times max
        x = random.randint(0, map_image.get_width() - 100)
        y = random.randint(0, map_image.get_height() - 100)
        tree_center = (x + 50, y + 50)  # Check the tree's center point
        if is_valid_tree_position(tree_center, tree_restricted_zones):
            trees.append(Tree((x, y), tree_frames))
            valid_position = True
        attempts += 1

# Fruit trees (wood + fruit)
tree_sheet_2 = pygame.image.load("rynn/tree-fruit.png").convert_alpha()
tree_frames_2 = load_frames(tree_sheet_2, 100, 100, 0, 7, spacing=5)
trees_2 = []
for _ in range(20):
    valid_position = False
    attempts = 0
    while not valid_position and attempts < 100:
        x = random.randint(0, map_image.get_width() - 100)
        y = random.randint(0, map_image.get_height() - 100)
        tree_center = (x + 50, y + 50)
        if is_valid_tree_position(tree_center, tree_restricted_zones):
            trees_2.append(Tree((x, y), tree_frames_2))
            valid_position = True
        attempts += 1

class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, player):
        super().__init__()
        self.image = zombie_img.copy()
        self.idle_image = zombie_img.copy()
        self.image = self.idle_image
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.Vector2(x, y)  # Add Vector2 position tracking
        self.player = player
        self.speed = 1.5
        self.attack_range = 30
        self.attack_damage = 10
        self.last_attack_time = 0
        self.attack_cooldown = 1
        self.attack_windup_time = 0.3
        self.windup_start_time = None
        self.hp = 100
        self.max_hp = 100
        self.is_moving = False
        self.facing_left = False

        self.walk_images = zombie_walk_images
        self.attack_images = zombie_attack_images
        self.die_images = zombie_die_images

        self.animation_index = 0
        self.last_animation_time = time.time()
        self.animation_speed = 0.2

        self.is_wandering = True
        self.wander_direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()#let the zombie have the same speed while wandering
        self.last_wander_time = time.time()
        self.wander_interval = 2
        self.pause_duration = 2

        self.state = "idle"
        self.is_dead = False
        self.death_time = 0
        self.death_duration = 1
        self.chase_range = 90

    def update_facing_direction(self):
        self.image = pygame.transform.flip(self.image, self.facing_left, False)

    def update(self):
        current_time = time.time()

        if self.is_dead:
            if current_time - self.last_animation_time > self.animation_speed:
                self.animation_index += 1
                if self.animation_index < len(self.die_images):
                    self.image = self.die_images[self.animation_index]
                    self.update_facing_direction()
                else:
                    self.image = self.die_images[-1]
                self.last_animation_time = current_time

            if current_time - self.death_time > self.death_duration:
                self.kill()
            return

        # Get player position (works with both Vector2 and rect)
        player_pos = getattr(self.player, 'position', pygame.Vector2(self.player.rect.center))#this can check if the player is using rect.center or Vector 2
        
        # Calculate direction vector
        direction = player_pos - self.position#use hypothenius to calculate the distance
        distance = direction.length()
        
        # Update facing direction
        self.facing_left = direction.x < 0

        # Attack state handling
        if self.state == "attack":
            if self.windup_start_time:
                if current_time - self.windup_start_time >= self.attack_windup_time:
                    self.apply_attack_damage()
                    self.windup_start_time = None

            if current_time - self.last_animation_time > self.animation_speed:
                self.animation_index += 1
                if self.animation_index < len(self.attack_images):
                    self.image = self.attack_images[self.animation_index]
                    self.update_facing_direction()
                else:
                    self.state = "walk"
                    self.animation_index = 0
                self.last_animation_time = current_time
            return

        # Movement logic
        if distance < self.chase_range:
            if distance > self.attack_range:
                # Chase player
                if distance > 0:
                    direction = direction.normalize()#prevent if the distance is longer the zombie will walk faster
                self.position += direction * self.speed
                self.is_moving = True
            elif current_time - self.last_attack_time >= self.attack_cooldown:
                self.start_attack()
        else:
            # Wandering behavior
            if self.is_wandering:
                self.position += self.wander_direction * self.speed * 0.5
                self.is_moving = True

                if current_time - self.last_wander_time > self.wander_interval:
                    self.is_wandering = False
                    self.last_wander_time = current_time
            else:
                self.is_moving = False
                if current_time - self.last_wander_time > self.pause_duration:
                    self.is_wandering = True
                    self.last_wander_time = current_time
                    self.wander_direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                    if self.wander_direction.length() > 0:
                        self.wander_direction = self.wander_direction.normalize()

        # Update rect position to match Vector2 position
        self.rect.center = (round(self.position.x), round(self.position.y))#use round since the rect.center only accept integer

        # Animation updates
        if self.is_moving:
            if current_time - self.last_animation_time > self.animation_speed:
                self.animation_index = (self.animation_index + 1) % len(self.walk_images)
                self.image = self.walk_images[self.animation_index]
                self.update_facing_direction()
                self.last_animation_time = current_time
        else:
            if self.state == "idle":
                self.image = self.idle_image
            elif self.state == "walk":
                if current_time - self.last_animation_time > self.animation_speed:
                    self.animation_index = (self.animation_index + 1) % len(self.walk_images)
                    self.image = self.walk_images[self.animation_index]
                    self.update_facing_direction()
                    self.last_animation_time = current_time

    def start_attack(self):
        self.state = "attack"
        self.animation_index = 0
        self.windup_start_time = time.time()
        self.last_attack_time = time.time()
        print("Zombie starts wind-up...")

    def apply_attack_damage(self):
        # Recheck distance before applying damage
        player_pos = getattr(self.player, 'position', pygame.Vector2(self.player.rect.center))
        distance = (player_pos - self.position).length()

        if distance <= self.attack_range:
            print("Zombie attacks!")
            self.player.take_damage(self.attack_damage)
        else:
            print("Attack missed — player moved out of range.")

    def take_damage(self, amount, attacker_pos=None):
        if self.is_dead:  # Prevent further damage if the zombie is dead
            return

        self.hp -= amount
        print(f"Zombie HP: {self.hp}")

        if attacker_pos is not None:
            direction = self.position - pygame.Vector2(attacker_pos)
            if direction.length() > 0:
                direction = direction.normalize()
                knockback_distance = 20
                self.position += direction * knockback_distance
                self.rect.center = (round(self.position.x), round(self.position.y))#keep using this to let the rect.center have the current position of zombie

        if self.hp <= 0 and not self.is_dead:
            print("Zombie died!")
            self.state = "die"
            self.animation_index = 0
            self.is_dead = True
            self.death_time = time.time()
    def draw_health_bar(self, surface, camera):
        if self.hp <= 0:  # Do not draw health bar if the zombie is dead
            return

        bar_width = 30
        bar_height = 5
        fill = (self.hp / self.max_hp) * bar_width  # Fill ratio based on health
        fill = max(0, min(fill, bar_width))  # Ensure the fill is clamped to the max width
        x = self.rect.centerx - bar_width // 2 - camera.x  # Centered above zombie, considering camera offset
        y = self.rect.top - 10 - camera.y  # Positioned above the zombie

        # Outer black border with rounded corners
        border_rect = pygame.Rect(x - 1, y - 1, bar_width + 2, bar_height + 2)
        pygame.draw.rect(surface, (0, 0, 0), border_rect, border_radius=3)

        # Red background bar
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), bg_rect, border_radius=3)

        # Green health fill
        fill_rect = pygame.Rect(x, y, fill, bar_height)
        pygame.draw.rect(surface, (0, 255, 0), fill_rect, border_radius=3)

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, player, area_rect):
        super().__init__()
        self.walk_images = boss_walk_frames
        self.attack_images = boss_attack_frames
        self.ult_image = boss_ult_frames
        self.death_images = boss_die_frames
        self.image = self.walk_images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.Vector2(x, y)
        self.player = player
        self.area_rect = area_rect
        self.speed = 1.75
        self.attack_range = 60
        self.attack_damage = 20
        self.last_attack_time = 0
        self.attack_cooldown = 1.2
        self.hp = 200
        self.max_hp = 200
        self.attack_duration = 0.5
        self.attack_animation_end_time = 0
        self.state = "idle"
        self.animation_index = 0
        self.last_animation_time = time.time()
        self.animation_speed = 0.15
        self.attack_count = 0
        self.is_using_ult = False
        self.ult_frame_index = 0
        self.ult_end_time = 0
        self.is_dead = False
        self.death_index = 0
        self.pending_attack = False
        self.facing_left = False
        self.attack_animation_active = False
        self.dodged = False  # Flag to prevent continuous dodge message
        self.attack_in_progress = False  # Flag to prevent multiple attacks per animation cycle

    def update(self):
        if self.is_dead:
            self.handle_death()
            return

        player_pos = pygame.Vector2(self.player.rect.center)
        direction = player_pos - self.position
        distance = direction.length()

        # Avoid jitter when directly on top of player
        if abs(direction.x) > 2:
            self.facing_left = direction.x < 0

        if self.is_using_ult:
            self.handle_ultimate()
        elif self.attack_animation_active:
            if time.time() >= self.attack_animation_end_time:
                self.attack_animation_active = False
                self.state = "idle"
                if self.pending_attack:
                    self.apply_attack_damage()
                    self.pending_attack = False
            else:
                # Check if the player dodged out of attack range during animation, but allow animation to continue
                self.handle_attack_dodge()

        elif distance <= self.attack_range and time.time() - self.last_attack_time >= self.attack_cooldown:
            self.attack_player()
        elif distance <= 200:
            self.move_toward_player(direction, distance)
        else:
            self.state = "idle"

        self.update_animation()

    def move_toward_player(self, direction, distance):
        if distance > self.attack_range - 5 and not self.attack_animation_active and not self.is_using_ult:
            direction = direction.normalize()
            new_pos = self.position + direction * self.speed
            if self.area_rect.collidepoint(new_pos):
                self.position = new_pos
                self.rect.center = (round(self.position.x), round(self.position.y))
                self.state = "chasing"

    def update_animation(self):
        current_time = time.time()
        if current_time - self.last_animation_time > self.animation_speed:
            if self.state == "chasing":
                self.animation_index = (self.animation_index + 1) % len(self.walk_images)
                image = self.walk_images[self.animation_index]
            elif self.state == "attacking":
                self.animation_index = (self.animation_index + 1) % len(self.attack_images)
                image = self.attack_images[self.animation_index]
            elif self.state == "ultimate":
                self.ult_frame_index = min(self.ult_frame_index + 1, len(self.ult_image) - 1)
                image = self.ult_image[self.ult_frame_index]
            elif self.state == "dying":
                image = self.death_images[min(self.death_index, len(self.death_images) - 1)]
            else:
                image = self.walk_images[0]

            if self.facing_left:
                image = pygame.transform.flip(image, True, False)

            self.image = image
            self.last_animation_time = current_time

    def attack_player(self):
        # Only attack if the player is within attack range and the attack isn't already in progress
        if self.attack_in_progress:
            return  # Prevent multiple attacks during the same attack animation cycle

        player_pos = pygame.Vector2(self.player.rect.center)
        distance = (player_pos - self.position).length()

        if distance <= self.attack_range:
            self.state = "attacking"
            self.attack_animation_active = True
            self.last_attack_time = time.time()
            self.attack_animation_end_time = self.last_attack_time + len(self.attack_images) * self.animation_speed
            self.pending_attack = True
            self.attack_in_progress = True  # Mark that an attack is in progress
            self.animation_index = 0
            self.last_animation_time = time.time()

            self.attack_count += 1
            if self.attack_count >= 3:
                self.trigger_ultimate()

    def handle_attack_dodge(self):
        """Check if the player has dodged out of range, but still allow the attack animation to continue."""
        if self.is_player_out_of_range() and not self.dodged:
            self.dodged = True
            print("Player dodged, but attack animation continues.")
        elif not self.is_player_out_of_range():
            self.dodged = False  # Reset dodged flag if player is back in range

    def is_player_out_of_range(self):
        """Check if the player has moved out of the attack range during the attack animation"""
        player_pos = pygame.Vector2(self.player.rect.center)
        distance = (player_pos - self.position).length()
        return distance > self.attack_range

    def apply_attack_damage(self):
        # Apply damage only when the player is still in range at the time of attack animation end
        player_pos = pygame.Vector2(self.player.rect.center)
        distance = (player_pos - self.position).length()
        if distance <= self.attack_range:
            self.player.take_damage(self.attack_damage)
            print("Boss hit player!")
        self.attack_in_progress = False  # Reset the attack flag after applying damage

    def trigger_ultimate(self):
        self.is_using_ult = True
        self.state = "ultimate"
        self.ult_frame_index = 0
        self.ult_end_time = time.time() + len(self.ult_image) * self.animation_speed
        self.last_animation_time = time.time()
        self.attack_count = 0

    def handle_ultimate(self):
        if time.time() > self.ult_end_time:
            self.is_using_ult = False
            self.state = "idle"

    def take_damage(self, amount):
        if self.is_dead:
            return

        self.hp -= amount
        print(f"Boss HP: {self.hp}/{self.max_hp}")
        if self.hp <= 0:
            self.is_dead = True
            self.state = "dying"
            self.death_index = 0
            self.last_animation_time = time.time()

    def handle_death(self):
        current_time = time.time()

        if self.death_index < len(self.death_images):
            if current_time - self.last_animation_time > self.animation_speed:
                self.image = self.death_images[self.death_index]
                if self.facing_left:
                    self.image = pygame.transform.flip(self.image, True, False)
                self.death_index += 1
                self.last_animation_time = current_time
                if self.death_index == len(self.death_images):
                    self.death_complete_time = current_time + 0.4  # Delay before killing
        elif hasattr(self, "death_complete_time") and current_time > self.death_complete_time:
            self.kill()

    def draw_health_bar(self, surface, camera=None):
        bar_width = 100
        bar_height = 10
        fill = (self.hp / self.max_hp) * bar_width
        if camera:
            x = self.rect.centerx - bar_width // 2 - camera.x
            y = self.rect.top - 15 - camera.y
        else:
            x = self.rect.centerx - bar_width // 2
            y = self.rect.top - 15
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (x, y, fill, bar_height))

# Fishing
class PondArea:
    def __init__(self, center, radius_x, radius_y, day_spritesheet_path, night_spritesheet_path, rows, cols, detection_scale=1.5):
        self.center = center
        self.visual_radius_x = radius_x
        self.visual_radius_y = radius_y
        self.detection_radius_x = radius_x * detection_scale
        self.detection_radius_y = radius_y * detection_scale

        self.rect = pygame.Rect(
            center[0] - self.visual_radius_x,
            center[1] - self.visual_radius_y,
            self.visual_radius_x * 2,
            self.visual_radius_y * 2
        )

        # Load the day and night spritesheets
        self.day_spritesheet = pygame.image.load(day_spritesheet_path).convert_alpha()
        self.night_spritesheet = pygame.image.load(night_spritesheet_path).convert_alpha()

        # Use the day sprite sheet by default
        self.spritesheet = self.day_spritesheet
        self.rows = rows
        self.cols = cols
        self.frames = self.load_frames()
        self.current_frame = 0
        self.frame_delay = 100  # milliseconds
        self.last_update = pygame.time.get_ticks()
        self.show_animation = False
        # rewards
        self.result_display_time = 3000  # milliseconds to show result
        self.result_start_time = 0
        self.fishing_result = None  # None means nothing to show

        self.rewards = [
    {
        "id": "fish_1",
        "name": "Fish",
        "message": "You got a fish!",
        "image": pygame.image.load("rynn/fish_1.png").convert_alpha(),
        "chance": 0.4
    },
    {
        "id": "fish_2",
        "name": "Big Fish",
        "message": "You got a fish!",
        "image": pygame.image.load("rynn/fish_2.png").convert_alpha(),
        "chance": 0.3
    },
    {
        "id": "nothing",
        "name": "Nothing",
        "message": "You got nothing...",
        "image": pygame.image.load("rynn/nothing.png").convert_alpha(),
        "chance": 0.27
    },
    {
        "id": "crystal",
        "name": "Crystal",
        "message": "Congratulations! You got a rare item!",
        "image": pygame.image.load("rynn/crystal.png").convert_alpha(),
        "chance": 0.03
    }
]

        
    def load_frames(self):
        frame_width = self.spritesheet.get_width() // self.cols
        frame_height = self.spritesheet.get_height() // self.rows
        frames = []
        for row in range(self.rows):
            for col in range(self.cols):
                frame = self.spritesheet.subsurface(
                    pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                )
                frames.append(frame)
        return frames

    def is_player_inside(self, player_pos):
        dx = (player_pos[0] - self.center[0]) / self.detection_radius_x
        dy = (player_pos[1] - self.center[1]) / self.detection_radius_y
        return dx * dx + dy * dy <= 1

    def update(self, player_pos, keys):
        if self.is_player_inside(player_pos) and keys[pygame.K_j]:
            self.show_animation = True
            self.current_frame = 0
            inventory.add_item("fish", 1)


        if self.show_animation:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_delay:
                self.current_frame += 1
                self.last_update = now
                if self.current_frame >= len(self.frames):
                    self.current_frame = 0
                    self.show_animation = False
                    self.choose_fishing_result()

    def choose_fishing_result(self):
        weights = [r["chance"] for r in self.rewards]
        result = random.choices(self.rewards, weights=weights, k=1)[0]
        self.fishing_result = result
        self.result_start_time = pygame.time.get_ticks()

        if result["id"] != "nothing":
            inventory.add_item(result["name"], 1)

                    
    def draw(self, screen, player_position, font, reward_font):
        if self.show_animation:
            frame = self.frames[self.current_frame]
            scaled_frame = pygame.transform.scale(frame, screen.get_size())
            screen.blit(scaled_frame, (0, 0))
        # Show "Press J to fish" if player is in detection radius
        else:
            if self.is_player_inside(player_position):
                text_surface = font.render("Press J to fish", True, (255, 255, 255))  # White text
                text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 100))
                screen.blit(text_surface, text_rect)
        # Update spritesheet based on cycle 
        if self.fishing_result:
            now = pygame.time.get_ticks()
            if now - self.result_start_time < self.result_display_time:
                if "image" in self.fishing_result:
                    fishing_image = self.fishing_result["image"]
                    image = pygame.transform.rotozoom(fishing_image, 0, 1.5)
                    image_rect = image.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 50))
                    screen.blit(image, image_rect)

                # Draw the result message below the image
                text_surface = reward_font.render(self.fishing_result["message"], True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 70))
                screen.blit(text_surface, text_rect)
            else:
                self.fishing_result = None  # Clear result after time is up
                    
     # Update sprite sheet based on day or night
    def update_time_of_day(self, is_daytime):
        if is_daytime:
            self.spritesheet = self.day_spritesheet
        else:
            self.spritesheet = self.night_spritesheet
        self.frames = self.load_frames()  # Reload frames for the new spritesheet 
                  
pond = PondArea(
    center=(1554, 585),
    radius_x=165,
    radius_y=162,
    day_spritesheet_path="rynn/new-fish-sprite.png",
    night_spritesheet_path="rynn/night-fish-sprite.png",

    rows=1,  
    cols=17,
    detection_scale=1.1
)        

# Sprite groups
all_sprites = pygame.sprite.Group()
zombie_group = pygame.sprite.Group()
boss_area = pygame.Rect(240, 144, 342, 129)  # x, y, width, height
boss = Boss(399, 145, player_instance, boss_area)
all_sprites.add(boss)
settings_menu = SettingsMenu()
game_state = "game"

spawn_delay = 3
last_spawn_time = time.time()

# Function to spawn zombies (limit to 10)
def spawn_zombie():
    if len(zombie_group) < 10:
        # Get a random spawn position from defined zones
        x, y = get_random_spawn_position_from_zones(zombie_spawn_zones)
        
        # Create the zombie at that position
        zombie = Zombie(x, y, player_instance)
        
        # Add the zombie to the groups
        zombie_group.add(zombie)
        all_sprites.add(zombie)
        print(f"Spawned zombie at ({x}, {y})")

def get_random_spawn_position_from_zones(zones):
    zone = random.choice(zones)  # Pick a random zone
    x = random.randint(zone.left, zone.right)
    y = random.randint(zone.top, zone.bottom)
    return (x, y)

zombie_spawn_zones = [
    pygame.Rect(121, 1221, 1235, 133),  # zone 1
]
def draw_settings_menu(screen):
    screen.fill((30, 30, 30))  # dark background
    font = pygame.font.SysFont(None, 48)

    # Example buttons
    music_text = font.render("Music Volume: [Use Arrow Keys]", True, (255, 255, 255))
    quit_text = font.render("Press Q to Quit", True, (255, 255, 255))

    screen.blit(music_text, (100, 150))
    screen.blit(quit_text, (100, 250))

inventory = Inventory()
# Main loop
running = True
while running:
    dt = clock.tick(60) / 1000
    current_time = pygame.time.get_ticks() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save progress before exiting
            inventory_dict = inventory.get_inventory_dict()
            progress_data = {
                "position": [player_instance.position.x, player_instance.position.y],
                "health": player_instance.health,
                "inventory":inventory_dict
            }
            # Save the progress
            user_system.save_progress(
                player_instance.username,
                player_instance.health,
                [player_instance.position.x, player_instance.position.y],
                player_instance.inventory
                )
            running = False        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "game":
                    game_state = "settings"
                    settings_menu.visible = True
                elif game_state == "settings":
                    game_state = "game"
                    settings_menu.visible = False
            if event.key == pygame.K_EQUALS:
                minimap_zoom_factor = min(4.0, minimap_zoom_factor + 0.1)
            elif event.key == pygame.K_MINUS:
                minimap_zoom_factor = max(0.5, minimap_zoom_factor - 0.1)
            elif event.key == pygame.K_TAB:
                player_instance.switch_weapon(event.key)
            elif event.key == pygame.K_f:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    character_scale = fullscreen_scale
                else:
                    screen = pygame.display.set_mode(window_size)
                    character_scale = 1.0
                overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            elif event.key == pygame.K_b:
                inventory.toggle_inventory()

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                player_instance.attacking = True

        # Handle settings menu events
        if game_state == "settings":
            result = settings_menu.handle_events(event)
            if result == "quit":
                running = False
            elif result == "back":
                game_state = "game"
                settings_menu.visible = False

    # ========== GAME LOGIC ONLY WHEN IN "GAME" STATE ==========
    if game_state == "game":
        keys = pygame.key.get_pressed()
        new_position, current_sprite = player_instance.move(keys, dt)
        move_distance = speed * dt * 60

        current_time = time.time()
        if current_time - last_spawn_time >= spawn_delay and len(zombie_group) < 10:
            spawn_zombie()
            last_spawn_time = current_time

        zombie_group.update()
        boss.update()

        # Movement with restriction zone logic
        proposed_position = player_instance.position.copy()
        for direction in ["w", "s", "a", "d"]:
            if keys[getattr(pygame, f"K_{direction}")]:
                test_pos = proposed_position.copy()
                if direction == "w": test_pos.y -= move_distance
                if direction == "s": test_pos.y += move_distance
                if direction == "a": test_pos.x -= move_distance
                if direction == "d": test_pos.x += move_distance
                test_rect = pygame.Rect(test_pos.x - 20, test_pos.y - 20, 40, 40)
                if not is_in_restricted_zone(test_rect.center, restricted_zones):
                    if direction == "w": proposed_position.y -= move_distance; player_instance.direction = "up"
                    if direction == "s": proposed_position.y += move_distance; player_instance.direction = "down"
                    if direction == "a": proposed_position.x -= move_distance; player_instance.direction = "left"
                    if direction == "d": proposed_position.x += move_distance; player_instance.direction = "right"

        proposed_position.x = max(0, min(proposed_position.x, map_image.get_width()))
        proposed_position.y = max(0, min(proposed_position.y, map_image.get_height()))
        player_instance.position = proposed_position
        player_position = proposed_position

        attack_sprite = player_instance.attack(trees, zombie_group)

        camera.center = player_position
        camera.clamp_ip(map_image.get_rect())

        # Drawing to zoom_surface
        zoom_surface.fill((0, 0, 0))
        zoom_surface.blit(map_image, (0, 0), camera)

        for tree in trees:
            tree.update(current_time)
            tree.draw(zoom_surface, camera)

    for tree in trees_2:
        tree.update(current_time)
        tree.draw(zoom_surface, camera)

    for zombie in zombie_group:
        zoom_surface.blit(zombie.image, zombie.rect.move(-camera.x, -camera.y))
        zombie.draw_health_bar(zoom_surface, camera)

    keys = pygame.key.get_pressed()
    pond.update(player_instance.rect.center, keys)
   
        # Boss draw
    if boss.alive():  # Check if boss hasn't been killed
        boss_rect_on_screen = boss.rect.move(-camera.x, -camera.y)
        zoom_surface.blit(boss.image, boss_rect_on_screen)
        if not boss.is_dead:
            boss.draw_health_bar(zoom_surface, camera)

    



        # Boss draw
    if boss.alive():  # Check if boss hasn't been killed
        boss_rect_on_screen = boss.rect.move(-camera.x, -camera.y)
        zoom_surface.blit(boss.image, boss_rect_on_screen)
        if not boss.is_dead:
            boss.draw_health_bar(zoom_surface, camera)



        # Final game drawing
    zoomed_view = pygame.transform.scale(zoom_surface, screen.get_size())
    screen.blit(zoomed_view, (0, 0))

    sprite_to_draw = attack_sprite if attack_sprite else current_sprite
    scaled_sprite = scale_sprite(sprite_to_draw, character_scale)
    sprite_x = screen.get_width() // 2 - scaled_sprite.get_width() // 2
    sprite_y = screen.get_height() // 2 - scaled_sprite.get_height() // 2
    screen.blit(scaled_sprite, (sprite_x, sprite_y))
    player_instance.draw_health_bar(screen)

    # Minimap
    minimap_surface = pygame.Surface((minimap_radius * 2, minimap_radius * 2), pygame.SRCALPHA)
    mini_camera_size = minimap_radius * 2 / minimap_zoom_factor
    mini_camera = pygame.Rect(0, 0, mini_camera_size, mini_camera_size)
    mini_camera.center = player_position
    mini_camera.clamp_ip(map_image.get_rect())
    mini_view = map_image.subsurface(mini_camera).copy()
    scaled_mini_view = pygame.transform.scale(mini_view, (minimap_radius * 2, minimap_radius * 2))
    minimap_surface.blit(scaled_mini_view, (0, 0))
    masked_minimap = minimap_surface.copy()
    masked_minimap.blit(minimap_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    pygame.draw.circle(masked_minimap, player_minimap_color, (minimap_radius, minimap_radius), 3)
    pygame.draw.circle(masked_minimap, minimap_border_color, (minimap_radius, minimap_radius), minimap_radius, minimap_border_width)
    screen.blit(masked_minimap, (minimap_pos[0] - minimap_radius, minimap_pos[1] - minimap_radius))

    # Day-night cycle (NEW day 66% night 33%)    
    cycle_duration = 60  # full cycle in seconds
    day_duration = cycle_duration * 0.66  # ~39.6s
    night_duration = cycle_duration * 0.34  # ~20.4s

    time_counter += dt
    cycle_time = time_counter % cycle_duration
    if cycle_time < day_duration:
        alpha = 0  # Full daylight (no fade)
        pond.update_time_of_day(is_daytime=True)  # Set to day for fishing sprite
    else:
        # Night fade-in (0 to 180 alpha) during night duration
        night_progress = (cycle_time - day_duration) / night_duration
        alpha = int(night_progress * 180)
        pond.update_time_of_day(is_daytime=False)  # Set to night for fishing sprite

    overlay.fill((0, 0, 50, alpha))
    screen.blit(overlay, (0, 0))

    pos_text = f"X: {int(player_position.x)}  Y: {int(player_position.y)}"
    text_surface = font.render(pos_text, True, (255, 255, 255))
    screen.blit(text_surface, (10, screen.get_height() - 30))

    icon = player_instance.weapon_icons[player_instance.current_weapon]
    icon_scaled = pygame.transform.scale(icon, (60, 60))

    # Draw a box (bottom-left for example)
    weapon_box = pygame.Rect(screen.get_width() - 100, screen.get_height() - 100, 80, 80)
    pygame.draw.rect(screen, (30, 30, 30), weapon_box)  # Dark box
    pygame.draw.rect(screen, (255, 255, 255), weapon_box, 2)  # White border
    screen.blit(icon_scaled, (weapon_box.x + 10, weapon_box.y + 10))
    
    #Draw pond
    pond.draw(screen, player_position, font, reward_font)


    #Draw inventory
    inventory.draw(screen)
                

    # ========== DRAW SETTINGS MENU WHEN ACTIVE ==========
    if game_state == "settings":
        screen.fill((10, 10, 10))  # Optional: dim background
        settings_menu.draw(screen)

    #Abandoned house
    if inside_house:
        screen.blit(inside_house_image, (0, 0))
    else:
        # World view rendering
        zoom_surface.fill((0, 0, 0))
        zoom_surface.blit(map_image, (0, 0), camera)
        zoomed_view = pygame.transform.scale(zoom_surface, screen.get_size())
        screen.blit(zoomed_view, (0, 0))

        # Draw house
        house_on_screen = house_rect.move(-camera.left, -camera.top)
        screen.blit(house_image, house_on_screen.topleft)

        # Draw player
        pygame.draw.circle(screen, (255, 0, 0),
                        (screen.get_width() // 2, screen.get_height() // 2), 4)

        # Prompt to enter house
        player_screen_pos = pygame.Vector2(screen.get_width() // 2, screen.get_height() // 2)
        if house_on_screen.inflate(100, 100).collidepoint(player_screen_pos):
            text = font.render("Press J to enter house", True, (255, 255, 255))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 30))
            if keys[pygame.K_j]:
                inside_house = True

    pygame.display.update()
    pygame.display.flip()

    
pygame.quit()
sys.exit()