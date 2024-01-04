import pygame

from utils.constants import WHITE


class Messages:
    max_messages = 0
    messages = []
    x, y = 0, 0
    fontMessages = None
    color = None
    screen = None

    def __init__(
        self, screen, max_messages=10, fontMessages=None, color=WHITE, x=0, y=0
    ):
        self.max_messages = max_messages
        self.x = x
        self.y = y
        self.fontMessages = fontMessages
        self.color = color
        self.screen = screen

    def draw_messages(self):
        # Elimina mensajes antiguos si superan el límite
        while len(self.messages) > self.max_messages:
            self.messages.pop(0)

        # Inicializa la posición y
        y_position = self.y

        # Renderiza cada mensaje
        for i, message in enumerate(self.messages):
            # Renderiza el texto y obtén su rectángulo
            text = self.fontMessages.render(message, True, self.color)
            text_rect = text.get_rect(topleft=(self.x, y_position))
            # Aumenta la posición y para el próximo mensaje
            y_position += text_rect.height  # Ajusta según tus necesidades de espaciado
            # Dibuja el texto en la pantalla
            self.screen.blit(text, text_rect)
        pygame.display.flip()

    def add_message(self, message):
        self.messages.append(message)

    def update_message(self, pos, message):
        if pos > len(self.messages)-1:
            pos = len(self.messages) - 1
        self.messages[pos] = message
        
    def length(self):
        return len(self.messages)
    
    def clear(self):
        self.messages.clear()

    def draw_text(self, font, text, width, height, bold=True, color=(255, 255, 255)):
        text_rendered = font.render(text, bold, color)
        rect_text = text_rendered.get_rect(center=(width, height))
        self.screen.blit(text_rendered, rect_text.topleft)
        return rect_text

    def draw_elements(self, elements):
        rect_text = None
        for text, font, width, height, bold, color in elements:
            rect_text = self.draw_text(font, text, width, height, bold, color)
        
