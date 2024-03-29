import pygame
import sys
import random
import re


from utils.constants import (
    GREEN,
    SHIPS,
    BLACK,
    WHITE,
    RED,
    GRAY,
    WIDTH,
    HEIGHT,
    TITTLE,
    OFFSET_WIDTH,
    OFFSET_HEIGHT,
    GRID_SIZE,
    CELL_SIZE,
    SEPARATION,
)
from entity.board import Board
from entity.messages import Messages


class Game:
    # Configuration

    GAME_OVER_COLOR = RED
    GAME_WINNER_COLOR = RED
    GAME_BACKGROUND_WINNER_BACKGROUND = WHITE
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

    def __init__(self):
        pygame.font.init()
        display_size = (WIDTH + OFFSET_WIDTH * 2, HEIGHT + OFFSET_HEIGHT * 2)
        screen = pygame.display.set_mode(display_size)
        pygame.display.set_caption(TITTLE)
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
        self._last_status = ""
        self.war_ships[self.USER].generate_new_board(False)
        self.war_ships[self.COMPUTER].generate_new_board(False)

    @property
    def last_status(self):
        return self._last_status

    @last_status.setter
    def last_status(self, old_status):
        self._last_status = old_status

    @last_status.deleter
    def game_lost(self):
        self._last_status = ""

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

    #### initialize

    def initialize_war_ships(self):
        common_params = (
            self.screen,
            GRID_SIZE,
            GRID_SIZE,
            SHIPS,
            CELL_SIZE,
            OFFSET_WIDTH,
            OFFSET_HEIGHT,
        )
        self.war_ships.append(Board(*common_params, "Computer 1"))
        self.war_ships.append(Board(*common_params, "Computer 2"))

    ### show screens
    def show_scores(self):
        if len(self.war_ships) < 2:
            return

        if self.players != -1:
            font_score = pygame.font.Font(None, 28)
            total = sum(ship.game_lost for ship in self.war_ships)

            elements = []
            for i in range(len(self.war_ships)):
                if i == 0:
                    x_position = OFFSET_WIDTH + CELL_SIZE + (GRID_SIZE * CELL_SIZE) // 2
                else:
                    x_position = (
                        x_position + (GRID_SIZE * CELL_SIZE) + SEPARATION + CELL_SIZE
                    )

                message = f"{self.war_ships[i].get_player(True)} Wins: {self.war_ships[1-i].game_lost} {self.calculate_percentage(self.war_ships[1-i].game_lost, total)} Shots: {self.war_ships[i].get_shots()} "

                element = (
                    message,
                    font_score,
                    x_position,
                    CELL_SIZE // 2,
                    True,
                    self.SHOW_SCORE_COLOR,
                    (-1, -1, -1),
                )
                elements.append(element)
            self.messages.draw_elements(elements)
        return True

    def show_game_zone(self, visible_ships=[False, False]):
        # clear screen
        self.screen.fill(BLACK)

        # Draw the two grids with spacing, numbers and header.
        for i, self.war_ship in enumerate(self.war_ships):
            x_position = OFFSET_WIDTH + i * (
                CELL_SIZE + GRID_SIZE * CELL_SIZE + SEPARATION
            )
            self.war_ship.show_game_zone(x_position, GRAY, visible_ships[i])

        # Draw the box in the buffer zone
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

    def show_game_over(self, winner):
        font_game_over = pygame.font.Font(None, 32)
        font_instructions = pygame.font.Font(None, 24)
        font_winner = pygame.font.Font(None, 64)
        width = CELL_SIZE * 2 + GRID_SIZE * CELL_SIZE + SEPARATION // 2

        elements = [
            (
                self.GAME_OVER,
                font_game_over,
                width,
                CELL_SIZE,
                True,
                self.GAME_OVER_COLOR,
                (-1, -1, -1),
            ),
            (
                self.PRESS_ANY_KEY,
                font_instructions,
                width,
                CELL_SIZE * 2,
                True,
                self.PRESS_ANY_KEY_COLOR,
                (-1, -1, -1),
            ),
            (
                winner,
                font_winner,
                width,
                HEIGHT // 2,
                True,
                self.GAME_WINNER_COLOR,
                self.GAME_BACKGROUND_WINNER_BACKGROUND,
            ),
        ]

        self.messages.draw_elements(elements)

    def change_turn(self, turn):
        return self.COMPUTER if turn == self.USER else self.USER

    ## read keyboard

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

    def show_screen(self, winner, visible_ships=[False, False], game_over=False):
        if game_over:
            visible_ships = [True, True]
        self.show_game_zone(visible_ships)
        # write messages
        self.messages.draw_messages()
        self.show_scores()
        if game_over:
            self.show_game_over(winner)
        # Refresh the screen
        pygame.display.flip()

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
        _winner = ""

        while running:
            time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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

            if game_mode == "game over":
                elapsed_time = (time - start_time) / 1000  # Convert to seconds
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    running = False
                elif self.players == 0 and elapsed_time >= 5:
                    pygame.time.delay(1)
                    game_mode = "game new"
                elif keys[pygame.K_SPACE] or elapsed_time >= 20:
                    game_mode = "start page"

            elif game_mode == "players":
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
                            "question": "Ships automatic? Y/N:",
                            "length": 1,
                            "regex": "([YNS])",
                            "iterate": 1,
                            "time": 20,
                            "default": "Y",
                        },
                        {
                            "key": "position",
                            "question": "Position Ship %1:",
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
                elif questions["key"] == "position":
                    # length = self.war_ships[self.USER].length()
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
                    elif questions["key"] == "position":
                        if self.war_ships[self.USER].place_ship_user(
                            iterate, text[0], text[1], text[2]
                        ):
                            text = ""
                            iterate += 1
                            if iterate >= self.war_ships[self.USER].length():
                                game_mode = "game new"

            elif game_mode == "game new":
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
                    last, last_direction, last_status = self.war_ships[
                        turn
                    ].get_last_shot()
                    yy, xx, direction = self.war_ships[last_turn].new_shot(
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
                        grid = "Out of Grids and separations"
                        letter = "N/A"
                        number = "N/A"
                    elif x < OFFSET_WIDTH + CELL_SIZE + GRID_SIZE * CELL_SIZE:
                        grid = "First Grid"
                        x -= OFFSET_WIDTH
                        letter = chr(65 + x // CELL_SIZE - 1)
                        number = (y - OFFSET_HEIGHT - CELL_SIZE) // CELL_SIZE + 1

                    elif (
                        x >= OFFSET_WIDTH + CELL_SIZE + GRID_SIZE * CELL_SIZE
                        and x
                        < OFFSET_WIDTH + CELL_SIZE + GRID_SIZE * CELL_SIZE + SEPARATION
                    ):
                        grid = "Inside the separation"
                        letter = "N/A"
                        number = "N/A"
                    elif (
                        x
                        < OFFSET_WIDTH
                        + CELL_SIZE
                        + GRID_SIZE * CELL_SIZE
                        + SEPARATION
                        + CELL_SIZE
                        + GRID_SIZE * CELL_SIZE
                    ):
                        grid = "Second Grid"
                        x -= (
                            OFFSET_WIDTH
                            + SEPARATION
                            + (GRID_SIZE * CELL_SIZE)
                            + OFFSET_WIDTH
                        )
                        xx = x // CELL_SIZE - 1
                        yy = (y - 40 - CELL_SIZE) // CELL_SIZE
                        number = yy + 1
                        letter = chr(65 + xx)
                    else:
                        grid = "Off the Grids"
                        letter = "N/A"
                        number = "N/A"

                    print(
                        f"({y},{x}  {yy}, {xx}   Click en {grid}: Letter {letter}, Number {number}"
                    )

                if (yy, xx) != Board.NO_SHOT:
                    self.war_ships[turn].plus_shot()
                    coordinates = chr(65 + xx) + f"{(yy+1) % 10}"
                    player = self.war_ships[turn].get_player()
                    status = ""
                    if self.war_ships[last_turn].get_status_grid(yy, xx) == Board.SHIP:
                        status = "hit"
                        self.war_ships[last_turn].set_status_grid(
                            yy, xx, Board.HIT_SHIP
                        )
                        self.show_game_zone(
                            [
                                self.players == 0 or game_mode == "players",
                                self.players == 0,
                            ]
                        )
                        self.war_ships[last_turn].put_water((yy, xx))
                        sunk = self.war_ships[last_turn].check_if_sunk((yy, xx))
                        if sunk is not None:
                            status = f"sunk {sunk}"
                        elif self.players == 0 or turn == self.COMPUTER:
                            shot = (yy, xx)

                            if (
                                last_status == "hit"
                                and last != Board.NO_SHOT
                                and (abs(yy - last[0]) > 1 or abs(xx - last[1]) > 1)
                            ):
                                self.war_ships[turn].set_last_shot(
                                    last, last_direction, last_status
                                )

                            self.war_ships[turn].set_last_shot(shot, direction, status)
                            self.war_ships[turn].set_last_shot(
                                Board.NEW_SHOT, Board.NO_DIRECTION, Board.NO_STATUS
                            )
                        anotherShot = True

                    elif (
                        self.war_ships[last_turn].get_status_grid(yy, xx)
                        == Board.EMP_SHIP
                    ):
                        if last_status == "hit" and last != Board.NO_SHOT:
                            self.war_ships[turn].set_last_shot(
                                last, Board.NO_DIRECTION, last_status
                            )

                        status = "water"
                        self.war_ships[last_turn].set_status_grid(
                            yy, xx, Board.HIT_WATER
                        )
                    elif (
                        self.war_ships[last_turn].get_status_grid(yy, xx)
                        == Board.HIT_WATER
                    ):
                        status = "water again"
                    else:
                        self.war_ships[last_turn].show_board()
                        status = "error"

                    self.war_ships[turn].last_status = status

                    not_sunk = self.war_ships[last_turn].no_hits_ship()

                    last_coordinates = Board.NO_SHOT
                    if last not in (Board.NO_SHOT, Board.NEW_SHOT):
                        yy, xx = last
                        last_coordinates = chr(65 + xx) + f"{(yy+1) % 10}"

                    message = "["
                    for turns in (turn, last_turn):
                        ship = self.war_ships[turns]
                        if len(message) > 1:
                            message += "] ["
                        message += f"{ship.get_player()} {ship.get_shots()} {ship.hits_ship()} {ship.no_hits_ship()} "
                    message += f"] [{coordinates} {status} last {last_coordinates}]"

                    print(f"{message}")
                    self.messages.add_message(f"{player} {coordinates} {status}")

                    # Check if everything is sunk
                    if not_sunk == 0:
                        _winner = player + " win."
                        self.messages.add_message(_winner)
                        start_time = pygame.time.get_ticks()
                        game_mode = "game over"
                    else:
                        turn = self.change_turn(turn)
                        last_turn = self.change_turn(turn)

                    (yy, xx) = Board.NO_SHOT

            self.show_screen(
                    _winner,
                    [self.players == 0 or game_mode == "players", self.players == 0],
                    game_mode == "game over",
                )

            self.clock.tick(self.FPS)
            self.prev_time = time + 0
        pygame.quit()
