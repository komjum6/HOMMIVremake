import pygame

class Button:
    def __init__(self, x, y, width, height, text, font_size, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (70, 70, 70)
        self.text = text
        self.font_size = font_size
        self.callback = callback
        self.font = pygame.font.Font(None, self.font_size)
        self.text_surf = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()