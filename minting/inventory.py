import pygame

class TutorialPage:
    def __init__(self, title, text, image_path, frame_count, frame_width, frame_height):
        self.title = title
        self.text = text
        self.frames = self._load_frames(image_path, frame_count, frame_width, frame_height)
        self.frame_index = 0
        self.frame_timer = 0

    def _load_frames(self, path, count, w, h):
        sheet = pygame.image.load(path).convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * w, 0, w, h)) for i in range(count)]

    def update(self):
        self.frame_timer += 1
        if self.frame_timer >= 5:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.frame_timer = 0

    def draw(self, surface, font, x, y, w, h):
        # Draw background
        pygame.draw.rect(surface, (30, 30, 30), (x, y, w, h))
        pygame.draw.rect(surface, (200, 200, 200), (x, y, w, h), 2)

        # Draw title and text
        title_surf = font.render(self.title, True, (255, 255, 255))
        text_surf = font.render(self.text, True, (255, 255, 255))
        surface.blit(title_surf, (x + 20, y + 20))
        surface.blit(text_surf, (x + 20, y + 60))

        # Draw animation
        frame = self.frames[self.frame_index]
        frame = pygame.transform.scale(frame, (200, 200))
        surface.blit(frame, (x + w - 220, y + h // 2 - 100))

class TutorialManager:
    def __init__(self, font, tutorial_pages, pos=(100, 100), size=(600, 400)):
        self.font = font
        self.pages = tutorial_pages  # list of TutorialPage
        self.pos = pos
        self.size = size
        self.show = False
        self.page_index = 0

    def toggle(self):
        self.show = not self.show
        self.pages[self.page_index].frame_index = 0
        self.pages[self.page_index].frame_timer = 0

    def next_page(self):
        self.page_index = (self.page_index + 1) % len(self.pages)

    def prev_page(self):
        self.page_index = (self.page_index - 1) % len(self.pages)

    def update(self):
        if self.show:
            self.pages[self.page_index].update()

    def draw(self, surface):
        if self.show:
            x, y = self.pos
            w, h = self.size
            self.pages[self.page_index].draw(surface, self.font, x, y, w, h)
font = pygame.font.SysFont(None, 24)

tutorial_pages = [
    TutorialPage("Movement", "Use W A S D to move.", "testmove.png", 24, 64, 64),
    #TutorialPage("Chop Trees", "Press SPACE near tree to chop.", "tutorial_chop.png", 18, 64, 64),
    #TutorialPage("Switch Weapon", "Press 1/2/3 to switch.", "tutorial_switch.png", 12, 64, 64)
]

tutorial = TutorialManager(font, tutorial_pages)
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                tutorial.toggle()
            elif tutorial.show:
                if event.key == pygame.K_RIGHT:
                    tutorial.next_page()
                elif event.key == pygame.K_LEFT:
                    tutorial.prev_page()

    tutorial.update()
    tutorial.draw(screen)