import pygame

class Inventory:
    def __init__(self, max_slots=20):
        self.max_slots = max_slots
        self.slots = [None] * max_slots  # Initial empty slots
        self.slot_rects = []
        self.font = pygame.font.SysFont("Arial", 20)
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
            pygame.draw.rect(surface, (200, 200, 200), rect)  # Draw slot box (gray)
            item = self.slots[i]
            if item:
                name, count = item
                text = self.font.render(f"{name} x{count}", True, (0, 0, 0))
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)

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
                    text = self.font.render(f"{name} x{count}", True, (0, 0, 0))
                    text_rect = text.get_rect(center=rect.center)
                    surface.blit(text, text_rect)

    def add_item(self, name, count):
        """Add an item to the inventory"""
        for i in range(self.max_slots):
            if self.slots[i] is None:
                self.slots[i] = (name, count)
                return True
        return False

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Create the inventory
inventory = Inventory()

# Main game loop
running = True
while running:
    screen.fill((0, 0, 0))  # Clear screen with black (game background)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:  # Press 'B' to toggle inventory
                inventory.toggle_inventory()

    # Draw the inventory
    inventory.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
