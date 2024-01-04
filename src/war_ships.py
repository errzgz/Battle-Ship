import pygame
import sys
import random  # Importar el módulo random
import time
import numpy as np
import re


from utils.constants import *
from entity.board import Board
from entity.messages import Messages


# Configuración
GRID_SIZE = 10
CELL_SIZE = 30
SEPARATION = 300
WIDTH, HEIGHT = (
    CELL_SIZE * 2 + GRID_SIZE * CELL_SIZE * 2 + SEPARATION,
    GRID_SIZE * CELL_SIZE + 40,
)
OFFSET_WIDTH, OFFSET_HEIGHT = (CELL_SIZE, CELL_SIZE)


############### Functions


class Game:
    GAME_OVER_COLOR = RED
    PRESS_ANY_KEY_COLOR = WHITE
    SHOW_SCORE_COLOR = WHITE

    USER = 0
    COMPUTER = 1
    MAX_MESSAGES = 17
    GAME_OVER = "Game Over"
    PRESS_ANY_KEY = "Press SPACE to start"
    FPS = 60
    war_ships = []
    latest_hs_keys = []

    def __init__(self, screen):
        self.screen = screen
        self.prev_time = pygame.time.get_ticks()
        self.clock = pygame.time.Clock()
        fontMessages = pygame.font.Font(None, 24)
        self.messages = Messages(
            self.screen,
            self.MAX_MESSAGES,
            fontMessages,
            WHITE,
            OFFSET_WIDTH + CELL_SIZE + GRID_SIZE * CELL_SIZE + CELL_SIZE + 5,
            OFFSET_HEIGHT + 40 + 5,
        )

        self.players = 0
        self.initialize_war_ships()
        self.players = -1
        self.war_ships[self.USER].generate_new_board(False)
        self.war_ships[self.COMPUTER].generate_new_board(False)


    def calculate_percentage(self, number1, number2):
        # Ensure the numbers are of float type for accurate calculation
        number1 = float(number1)
        number2 = float(number2)

        # Calculate the percentage
        result = 00
        if number2 != 0:
            result = (number1 / number2) * 100

        # Round the result to two decimal places and add the percentage sign
        formatted_result = "{:.2f}%".format(result)

        return formatted_result

    #### Iniciazlze

    def initialize_war_ships(self):
        common_params = (
            self.screen,
            GRID_SIZE,
            GRID_SIZE,
            SHIPS,
            CELL_SIZE,
            OFFSET_WIDTH,
            OFFSET_HEIGHT,
            True,
        )
        self.war_ships.append(Board(*common_params, "Computer 1"))
        self.war_ships.append(Board(*common_params, "Computer 2"))

    ### show screens
    def show_scores(self):
        if len(self.war_ships) < 2:
            return

        if self.players != -1:
            font_score = pygame.font.Font(None, 28)
            total = sum(ship.get_perdidos() for ship in self.war_ships)

            elements = []
            for i in range(len(self.war_ships)):
                if i == 0:
                    x_position = OFFSET_WIDTH + CELL_SIZE + (GRID_SIZE * CELL_SIZE) // 2
                else:
                    x_position = (
                        x_position + (GRID_SIZE * CELL_SIZE) + SEPARATION + CELL_SIZE
                    )

                message = f"{self.war_ships[i].get_player(True)} Wins: {self.war_ships[1-i].get_perdidos()} {self.calculate_percentage(self.war_ships[1-i].get_perdidos(), total)} Shots: {self.war_ships[1-i].get_shots()} "

                element = (
                    message,
                    font_score,
                    x_position,
                    CELL_SIZE // 2,
                    True,
                    self.SHOW_SCORE_COLOR,
                )
                elements.append(element)
            self.messages.draw_elements(elements)
        return True

    def show_game_zone(self, visible_ships=[False, False]):
        # Limpiar la pantalla
        self.screen.fill(BLACK)

        # Dibujar las dos cuadrículas con separación, números y cabecera
        for i, self.war_ship in enumerate(self.war_ships):
            x_position = OFFSET_WIDTH + i * (
                CELL_SIZE + GRID_SIZE * CELL_SIZE + SEPARATION
            )
            self.war_ship.show_game_zone(x_position, GRAY, visible_ships[i])

        # Dibujar el cuadro en la zona de separación
        pygame.draw.rect(
            self.screen,
            WHITE,
            (
                OFFSET_WIDTH + CELL_SIZE + GRID_SIZE * CELL_SIZE + CELL_SIZE,
                OFFSET_HEIGHT + 40,
                SEPARATION - CELL_SIZE * 2,
                GRID_SIZE * CELL_SIZE,
            ),
            2,
        )

    def show_game_over(self):
        font_game_over = pygame.font.Font(None, 32)
        font_instructions = pygame.font.Font(None, 24)
        width = CELL_SIZE * 2 + GRID_SIZE * CELL_SIZE + SEPARATION // 2

        self.show_game_zone([True, True])
        self.show_scores()
        self.messages.draw_messages()

        elements = [
            (
                self.GAME_OVER,
                font_game_over,
                width,
                CELL_SIZE,
                True,
                self.GAME_OVER_COLOR,
            ),
            (
                self.PRESS_ANY_KEY,
                font_instructions,
                width,
                CELL_SIZE * 2,
                True,
                self.PRESS_ANY_KEY_COLOR,
            ),
        ]

        self.messages.draw_elements(elements)

    def change_turn(self,turn):
        return  self.COMPUTER if turn == self.USER else self.USER


    ## read keuboard

    def read_keyboard(self, time, pos, prompt, text, length):
        # process key presses and build a name

        end = False
        underscore = ""
        while len(self.latest_hs_keys) > 0:
            key, unicode = self.latest_hs_keys.pop(0)
            if key == pygame.K_RETURN:
                self.latest_hs_keys.clear()
                end = True
            elif key == pygame.K_BACKSPACE:
                if len(text) > 0:
                    # remove last character
                    text = text[:-1]
            elif (
                (unicode >= "A" and unicode <= "Z")
                or (unicode >= "a" and unicode <= "z")
                or (unicode >= "0" and unicode <= "9")
                or unicode in "åäöÅÄÖ-_§!#$%&/()=+?\*.:<>|"
            ) and len(text) < length:
                text = text + unicode
        if time % 1000 > 500 and not end:
            underscore = "_"
        else:
            underscore = " "
        if pos > self.messages.length() - 1:
            self.messages.add_message(prompt + text + underscore)
        else:
            self.messages.update_message(pos, prompt + text + underscore)

        return text, end

    ## Control game

    def run(self):
        number_question = -1
        iterate = -1
        text = ""
        game_mode = "start page"
        anotherShot = False
        turn = -1
        last_turn = -1
        last_direction = Board.NO_DIRECTION
        running = True

        while running:
            time = pygame.time.get_ticks()
            self.show_game_zone(
                [self.players == 0 or game_mode == "players", self.players == 0]
            )

            for event in pygame.event.get():
                if  event.type == pygame.QUIT:
                    running = False
                if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                    game_mode == "start page"
            if game_mode == "start page":
                start_time = pygame.time.get_ticks()
                iterate = 0
                number_question = 0
                text = ""
                game_mode = "players"
                self.messages.clear()
            elif game_mode in ("players", "load ship"):
                if event.type == pygame.TEXTINPUT:
                    unicode = event.text
                    key = ord(unicode)
                    self.latest_hs_keys.append((key, unicode))
                if event.type == pygame.KEYDOWN:
                    # get special keys
                    key = event.key
                    if key in (pygame.K_RETURN, pygame.K_BACKSPACE):
                        self.latest_hs_keys.append((key, ""))
                        # pygame.key.stop_text_input()

            if game_mode == "players":
                QUESTIONS = {
                    "questions": [
                        {
                            "key": "players",
                            "question": "Number players 0/1:",
                            "length": 1,
                            "regex": "([01])",
                            "iterate": 1,
                            "time": 5,
                            "default": "0",
                        },
                        {
                            "key": "ships",
                            "question": "Ships autommatic? Y/N:",
                            "length": 1,
                            "regex": "([YNS])",
                            "iterate": 1,
                            "time": 20,
                            "default": "Y",
                        },
                        {
                            "key": "postion",
                            "question": "Positon Ship %1:",
                            "length": 3,
                            "regex": "([A-J][0-9][HV])",
                            "iterate": 10,
                            "time": 0,
                            "default": None,
                        },
                    ]
                }

                questions = QUESTIONS["questions"][number_question]
                question = questions["question"]
                wait = questions["time"]
                default = questions["default"]
                elapsed_time = (time - start_time) / 1000  # Convert to seconds
                if wait and elapsed_time > wait:
                    text, end = self.read_keyboard(
                        time,
                        number_question + iterate,
                        question,
                        default,
                        questions["length"],
                    )
                    start_time = pygame.time.get_ticks()
                    end = True
                elif questions["key"] == "postion":
                    length = self.war_ships[self.USER].length()
                    index = self.war_ships[self.USER].quantity_ships(iterate)
                    name = self.war_ships[self.USER].get_ship_name(
                        SHIPS["ships"][index]["length"]
                    )
                    question = question.replace("%1", name)

                if wait == 0 or elapsed_time <= wait:
                    text, end = self.read_keyboard(
                        time,
                        number_question + iterate,
                        question,
                        text,
                        questions["length"],
                    )
                    pattern = re.compile(questions["regex"])

                if end and pattern.match(text.upper()):
                    if questions["key"] == "players":
                        self.players = int(text)
                        text = ""
                        if self.players == 0:
                            pygame.key.stop_text_input()
                            player_data = {
                                self.USER: "Player 1",
                                self.COMPUTER: "Player 2",
                            }
                            for player, player_name in player_data.items():
                                self.war_ships[player].generate_new_board(True)
                            game_mode = "game new"
                        else:
                            player_data = {self.USER: "User", self.COMPUTER: "Computer"}
                            self.war_ships[self.COMPUTER].generate_new_board(True)
                            number_question += 1
                            iterate = 0

                        for player, player_name in player_data.items():
                            self.war_ships[player].set_player(player_name)

                    elif questions["key"] == "ships":
                        if text.upper() == "N":
                            number_question += 1
                            iterate = 0
                            text = ""
                            self.war_ships[self.USER].generate_new_board(False)
                            self.war_ships[self.COMPUTER].generate_new_board(True)
                        else:
                            self.war_ships[self.USER].generate_new_board(True)
                            self.war_ships[self.COMPUTER].generate_new_board(True)
                            game_mode = "game new"
                    elif questions["key"] == "postion":
                        if self.war_ships[self.USER].place_ship_user(
                            iterate, text[0], text[1], text[2]
                        ):
                            text = ""
                            iterate += 1
                            if iterate >= self.war_ships[self.USER].length():
                                game_mode = "game new"

            elif game_mode == "game over":
                self.show_game_over()
                elapsed_time = (time - start_time) / 1000  # Convert to seconds
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    running = False
                elif self.players == 0 and elapsed_time >= 5:
                    pygame.time.delay(1)
                    game_mode = "game new"
                elif keys[pygame.K_SPACE] or elapsed_time >= 20:
                    game_mode = "start page"

            elif game_mode== "game new":
                self.messages.clear()
                pygame.key.start_text_input()
                turn = random.choice([self.USER, self.COMPUTER])
                last_turn = self.change_turn(turn)
                anotherShot = False
                if self.players == 0:
                    self.war_ships[self.USER].generate_new_board(True)
                self.war_ships[self.COMPUTER].generate_new_board(True)
                game_mode = "game start"
            elif game_mode == "game start":
                yy, xx = Board.NO_SHOT
                if anotherShot:
                    turn = self.change_turn(turn)
                    last_turn = self.change_turn(turn)
                    anotherShot = False

                if turn == self.COMPUTER or self.players == 0:
                    last, last_direction = self.war_ships[turn].get_last_shot()
                    yy, xx, last_direction = self.war_ships[last_turn].new_shot(
                        last, last_direction
                    )

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if (
                        y < 5 + OFFSET_HEIGHT
                        or y > GRID_SIZE * CELL_SIZE + 45 + OFFSET_HEIGHT
                    ):
                        cuadricula = "Fuera de las Cuadrículas y separcion"
                        letra = "N/A"
                        numero = "N/A"
                    elif x < OFFSET_WIDTH + CELL_SIZE + GRID_SIZE * CELL_SIZE:
                        cuadricula = "Primera Cuadrícula"
                        x -= OFFSET_WIDTH
                        letra = chr(65 + x // CELL_SIZE - 1)
                        numero = (y - OFFSET_HEIGHT - CELL_SIZE) // CELL_SIZE + 1

                    elif (
                        x >= OFFSET_WIDTH + CELL_SIZE + GRID_SIZE * CELL_SIZE
                        and x
                        < OFFSET_WIDTH
                        + CELL_SIZE
                        + GRID_SIZE * CELL_SIZE
                        + SEPARATION
                    ):
                        cuadricula = "Dentro de la separacion"
                        letra = "N/A"
                        numero = "N/A"
                    elif (
                        x
                        < OFFSET_WIDTH
                        + CELL_SIZE
                        + GRID_SIZE * CELL_SIZE
                        + SEPARATION
                        + CELL_SIZE
                        + GRID_SIZE * CELL_SIZE
                    ):
                        cuadricula = "Segunda Cuadrícula"
                        x -= (
                            OFFSET_WIDTH
                            + SEPARATION
                            + (GRID_SIZE * CELL_SIZE)
                            + OFFSET_WIDTH
                        )
                        xx = x // CELL_SIZE - 1
                        yy = (y - 40 - CELL_SIZE) // CELL_SIZE
                        numero = yy + 1
                        letra = letra = chr(65 + xx)
                    else:
                        cuadricula = "Fuera de las Cuadrículas"
                        letra = "N/A"
                        numero = "N/A"

                    print(
                        f"({y},{x}  {yy}, {xx}   Clic en {cuadricula}: Letra {letra}, Número {numero}"
                    )

                if (yy, xx) != Board.NO_SHOT:
                    self.war_ships[turn].plus_shot()
                    disparo = chr(65 + xx) + f"{(yy+1) % 10}"
                    player = self.war_ships[turn].get_player()
                    estado = ""
                    if self.war_ships[last_turn].get_status(yy, xx) == Board.SHIP:
                        estado = "hit"
                        self.war_ships[last_turn].set_status(yy, xx, Board.HIT_SHIP)
                        self.show_game_zone(
                            [
                                self.players == 0 or game_mode == "players",
                                self.players == 0,
                            ]
                        )
                        self.war_ships[last_turn].put_water((yy, xx))
                        pygame.display.flip()
                        sunk = self.war_ships[last_turn].check_if_sunk((yy, xx))
                        if sunk is not None:
                            estado = f"sunk {sunk}"
                        elif self.players == 0 or turn == self.COMPUTER:
                            shot = (yy, xx)
                            self.war_ships[turn].set_last_shot(shot, last_direction)
                            self.war_ships[turn].set_last_shot(
                                Board.NEW_SHOT, last_direction
                            )
                        anotherShot = True

                    elif self.war_ships[last_turn].get_status(yy, xx) == Board.EMP_SHIP:
                        estado = "water"
                        self.war_ships[last_turn].set_status(yy, xx, Board.HIT_WATER)
                    elif (
                        self.war_ships[last_turn].get_status(yy, xx) == Board.HIT_WATER
                    ):
                        estado = "water"
                    else:
                        estado = "error"

                    not_sunk2 = self.war_ships[turn].no_hits_ship()
                    not_sunk = self.war_ships[last_turn].no_hits_ship()
                    tocados = self.war_ships[last_turn].hits_ship()

                    print(
                        f"{player} {disparo} {estado} last_turn ---> {last_turn} {not_sunk} {not_sunk + tocados} turn {turn} {not_sunk2}"
                    )
                    self.messages.add_message(f"{player} {disparo} {estado}")

                    # Verificar si todo está hundido
                    if not_sunk == 0:
                        self.messages.add_message(player + " win.")
                        start_time = pygame.time.get_ticks()
                        game_mode = "game over"
                    else:
                        turn = self.change_turn(turn)
                        last_turn = self.change_turn(turn)

                    (yy, xx) = Board.NO_SHOT

            # escribir mensajes
            self.messages.draw_messages()
            self.show_scores()
            self.clock.tick(self.FPS)
            # Actualizar la pantalla
            pygame.display.flip()
            prev_time = time + 0


### Main Program
if __name__ == "__main__":
    # Inicializar Pygame
    pygame.display.init()
    pygame.font.init()

    disp_size = (WIDTH + OFFSET_WIDTH * 2, HEIGHT + OFFSET_HEIGHT * 2)

    # Crear la pantalla
    screen = pygame.display.set_mode(disp_size)
    pygame.display.set_caption("War ships")
    Game(screen).run()

    # Fin del programa
    pygame.quit()
    exit()
