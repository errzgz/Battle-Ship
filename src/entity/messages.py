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
        #pygame.display.flip()

    def add_message(self, message):
        self.messages.append(message)

    def update_message(self, pos, message):
        if pos > len(self.messages) - 1:
            pos = len(self.messages) - 1
        self.messages[pos] = message

    def length(self):
        return len(self.messages)

    def clear(self):
        self.messages.clear()

    def draw_text(
        self,
        font,
        text,
        target_width,
        target_height,
        bold=True,
        text_color=(255, 255, 255),
        background_color=(-1, -1, -1),
    ):
        text_surface = font.render(text, bold, text_color)
        text_rect = text_surface.get_rect(center=(target_width, target_height))
        if background_color != (-1, -1, -1):
            try:
                r, g, b = background_color
                if all(
                    0 <= i <= 255 for i in (r, g, b)
                ):  # Check if all values are in range 0-255
                    self.screen.fill((0, 0, 0), text_rect)
                    self.screen.fill(background_color, text_rect)
                else:
                    print(
                        f"Invalid color argument: The values of R, G, and B must be in the range 0-255. {background_color}"
                    )
            except TypeError:
                print(
                    f"Invalid color argument: The background color must be a tuple of 3 integers. {background_color}"
                )

        # text_rect = text_surface.get_rect()
        # text_rect.topleft = (100, 100)

        self.screen.blit(text_surface, text_rect)

    def draw_elements(self, elements):
        for text, font, width, height, bold, color, color_background in elements:
            self.draw_text(font, text, width, height, bold, color, color_background)
