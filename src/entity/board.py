import numpy as np
import pygame
import random


class Board:
    BLACK = (0, 0, 0)
    GRAY = (150, 150, 150)
    RED = (255, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    
    (
        EMP_SHIP,
        HIT_WATER,
        SHIP,
        HIT_SHIP,
        HIT_SUNK,
        HIT_WATER_TMP,
        SHIP_TMP,
        HIT_SUNK_TMP,
    ) = (
        ' ',
        'A',
        'X',
        'T',
        'H',
        'a',
        'x',
        'h',
    )

    NO_DIRECTION = (-1, -1)
    NO_SHOT = (-1, -1)
    NEW_SHOT = (-99, -99)
    ORIENTATIONS = ['horizontal', 'vertical']


     
    def __init__(
        self,
        screen,
        rows,
        columns,
        ships,
        cell_size,
        offset_weight,
        offset_height,
        player
    ):
        
        self._letters = None
        self._cell_size = 0
        self._screen = None
        self._game_lost = 0
        self._last_shots = []
        self._shots = 0
        self._board = []
        self.screen = screen
        self.cols = columns
        self.rows = rows
        self._ships = ships
        self._generate_ships()
        self.letters = [chr(65 + i) for i in range(columns)]
        self._cell_size = cell_size
        self.offset_weight = offset_weight
        self.offset_height = offset_height
        self._player = player
        self.generate_new_board(False)
        

        
    def _generate_matrix(self, rows, columns):
        matrix = [[self.HIT_WATER_TMP for _ in range(columns)] for _ in range(rows)]
        for j in range(1, columns - 1):
            matrix[1][j] = self.SHIP_TMP
        return matrix

    def show_game_zone(self, x_offset, color, visible_ships=False):
        # Draw the letters on the header
        for i in range(self.cols):
            font = pygame.font.Font(None, 36)
            text = font.render(self.letters[i], True, color)
            self.screen.blit(
                text,
                (x_offset + (i + 1) * self._cell_size , 5 + self.offset_weight),
            )

        for i in range(self.rows):
            for j in range(self.cols):
                cell_x = x_offset + (j + 1) * self._cell_size - 5
                cell_y = (i + 1) * self._cell_size + 40

                pygame.draw.rect(
                    self.screen,
                    color,
                    (cell_x, cell_y, self._cell_size, self._cell_size),
                    2,
                )

                if self._board[i][j] == self.HIT_WATER:
                    pygame.draw.rect(
                        self.screen,
                        self.GRAY,
                        (cell_x, cell_y, self._cell_size, self._cell_size),
                    )
                if self._board[i][j] == self.HIT_SHIP:
                    pygame.draw.rect(
                        self.screen,
                        self.GREEN,
                        (cell_x, cell_y, self._cell_size, self._cell_size),
                    )

                elif visible_ships and self._board[i][j] == self.SHIP:
                    pygame.draw.line(
                        self.screen,
                        self.RED,
                        (cell_x, cell_y),
                        (cell_x + self._cell_size, cell_y + self._cell_size),
                        2,
                    )
                    pygame.draw.line(
                        self.screen,
                        self.RED,
                        (cell_x + self._cell_size, cell_y),
                        (cell_x, cell_y + self._cell_size),
                        2,
                    )

        # Draw the numbers to the left of the grid.
        for i in range(self.rows):
            font = pygame.font.Font(None, 36)
            text = font.render(str((i + 1) % 10), True, color)
            self.screen.blit(
                text, (x_offset, i * self._cell_size + 45 + self.offset_height)
            )

    def put_water(self, shot):
        row, column = shot
        if self._board[row][column] not in (self.HIT_SHIP, self.HIT_SUNK):
            return False
        ok = True
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            new_row, new_column = row + dx, column + dy
            if 0 <= new_row < self.rows and 0 <= new_column < self.cols:
                if self._board[new_row][new_column] == self.EMP_SHIP:
                    self._board[new_row][new_column] = self.HIT_WATER_TMP
                elif self._board[new_row][new_column] not in (self.HIT_WATER,self.HIT_WATER_TMP):
                    ok = False
                    break
        if ok:
            matrix = [
                [self.HIT_WATER if cell == self.HIT_WATER_TMP else cell for cell in row]
                for row in self._board
            ]
        else:
            board = [
                [self.EMP_SHIP if cell == self.HIT_WATER_TMP else cell for cell in row]
                for row in self._board
            ]
        return ok

    def _seek(self, shot, direction):
        row, column = shot
        dx, dy = direction
        new_row, new_column = row + dx, column + dy
        while 0 <= new_row < self.rows and 0 <= new_column < self.cols:
            if self._board[new_row][new_column] in (self.EMP_SHIP, self.HIT_WATER):
                break
            elif self._board[new_row][new_column] in (self.SHIP):
                return -99, -99
            new_row, new_column = new_row + dx, new_column + dy
        return new_row, new_column

    def _fill_board(self, start, end, old_value, new_value):
        x1, y1 = start
        x2, y2 = end
        for row in range(x1, x2 + 1):
            for col in range(y1, y2 + 1):
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    # print( f'{(row,col)},({self._board[row][col]})')
                    if self._board[row][col] == old_value:
                        self._board[row][col] = new_value

    def check_if_sunk(self, shot):
        # row, column = shot
        sunk = None
        # ship_value = self._board[row][column]
        left_row, left_column = self._seek(shot, (-1, 0))
        right_row, right_column = self._seek(shot, (1, 0))
        top_row, top_column = self._seek(shot, (0, -1))
        bottom_row, bottom_column = self._seek(shot, (0, 1))
        if -99 in (left_row, right_row, top_column, bottom_column):
            return sunk

        difCol = bottom_column - top_column
        difRow = right_row - left_row

        if difCol == 2:
            dif = difRow
        else:
            dif = difCol
        #print(len(self._ships['ships']),dif ,len(self._ships['ships']) - 1 - (dif - 2 ))
        sunk = self._ships['ships'][len(self._ships['ships']) - 1 - (dif - 2)]['ship']
        self._fill_board(
            (left_row, top_column),
            (right_row, bottom_column),
            self.EMP_SHIP,
            self.HIT_WATER,
        )

        if self.no_hits_ship() == 0:
            self._game_lost += 1
        return sunk

    def get_game_lost(self):
        return self._game_lost

    def set_last_shot(self, shot, last_direction):
        if len(last_direction) != 2:
            last_direction = self.NO_DIRECTION
        self._last_shots.append((shot, last_direction))

    def get_last_shot(self):
        last = self.NO_SHOT
        last_direction = self.NO_DIRECTION
        if len(self._last_shots) > 0:
            last, last_direction = self._last_shots.pop()
        return last, last_direction

    
    def new_shot(self, shot, last_direction):

        if shot in (self.NO_SHOT, self.NEW_SHOT):
            return self.shot_computer()

        yy, xx = shot

        if self.no_hits_ship() == 0:
            return -1, -1, -1

        # Define directions to search (up, down, left, right)
        if last_direction == self.NO_DIRECTION:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
        else:
            directions = [last_direction]

        for direction in directions:
            dy, dx = direction
            new_yy, new_xx = yy + dy, xx + dx
            laps = 0
            while (
                0 <= new_yy < len(self._board)
                and 0 <= new_xx < len(self._board[0])
                and laps < 10
            ):
                laps += 1
                current_value = self._board[new_yy][new_xx]

                if current_value == Board.HIT_SHIP:
                    new_yy += dy
                    new_xx += dx
                elif current_value == Board.HIT_WATER:
                    dy, dx = -dy, -dx
                    new_yy += dy
                    new_xx += dx

                else:
                    return new_yy, new_xx, (dy, dx)

        return -1, -1, -1 

    def shot_computer(self):
        laps = 0
        while laps < 1000:
            laps += 1
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)

            if (
                self._board[row][col] != Board.HIT_WATER
                and self._board[row][col] != Board.HIT_SHIP
            ):
                return row, col, self.NO_DIRECTION

        for row in range(len(self._board)):
            for col in range(len(self._board[0])):
                if self._board[row][col] in (Board.EMP_SHIP, Board.SHIP):
                    return row, col, self.NO_DIRECTION

        return -1, -1, self.NO_DIRECTION


    def plus_shot(self):
        self._shots += 1

    def get_shots(self):
        return self._shots

    def get_player(self, clean = False):
        if clean:
            temp=self._player
            return temp.replace('.','')
        return self._player

    def set_player(self,player):
        self._player=player
        if len(self._player) > 8:
           self._player=self._player[:8]
        self._player=self._player.ljust(8, '.')


    def get_status(self, row, col):
        if 0 <=row < len(self._board) and 0<=col < len(self._board[0]):
            return self._board[row][col]
        else:
            return self.NO_SHOT

    def set_status(self, row, col, value):
        self._board[row][col] = value

    def generate_new_board(self, auto):
        self._last_shots = []
        self._shots=0
        self._board = np.full((self.rows, self.cols), self.EMP_SHIP, dtype=str)
        if auto:
            self._generate_board()
        
    def is_valid_placement(self, orientation, ship, row, col):
        if (
            orientation == self.ORIENTATIONS[0]
            and -1 <= col + len(ship[0]) <= self.cols + 1
            and -1 <= row + len(ship) <= self.rows + 1
        ):
            for j in range(len(ship)):
                for i in range(len(ship[0])):
                    if (
                        0 <= row + j < self.rows
                        and 0 <= col + i < self.cols
                        and self._board[row + j][col + i] == self.SHIP
                    ):
                        # print(row + j, col + i, orientation)
                        # self.show_board()
                        return False
            return True
        elif (
            orientation == self.ORIENTATIONS[1]
            and -1 <= row + len(ship[0]) <= self.rows + 1
            and -1 <= col + len(ship) <= self.cols + 1
        ):
            for i in range(len(ship[0])):
                for j in range(len(ship)):
                    if (
                        0 <= row + i < self.rows
                        and 0 <= col + j < self.cols
                        and self._board[row + i][col + j] == self.SHIP
                    ):
                        # print(row + i, col + j, orientation)
                        # self.show_board()
                        return False
            return True
        else:
            return False

    def place_ships_automatic(self, ship):
        repeat = True
        while repeat:
            follow = True
            while follow:
                row = random.randint(-1, self.rows)
                col = random.randint(-1, self.cols)
                follow = False
                if (
                    0 <= row < self.rows
                    and 0 <= col < self.cols
                    and self._board[row][col] == self.SHIP
                ):
                    follow = True
            orientations =self.ORIENTATIONS.copy()
            random.shuffle(orientations)
            for orientation in orientations:
                repeat = not self._place_ship(ship, row, col, orientation)
                if not repeat:
                    break
        return True

    def place_ship_user(self, iterate, colLetter, rowNumber,  orientation):
        row = 9 if int(rowNumber) == 0 else int(rowNumber) - 1
        col = ord(colLetter.upper()) - 65
        ship=self.get_ship(iterate)
        row-=1
        col-=1
        return self._place_ship(ship, row, col, self.ORIENTATIONS[ 0 if orientation.upper() == self.ORIENTATIONS[0][0].upper() else 1])

    def _place_ship(self, ship, row, col, orientation):
        placed = False
        if orientation == self.ORIENTATIONS[0] and self.is_valid_placement(
            orientation, ship, row, col
        ):
            placed = True
            for j in range(len(ship)):
                for i in range(len(ship[0])):
                    if 0 <= row + j < self.rows and 0 <= col + i < self.cols:
                        if self._board[row + j][col + i] != self.SHIP:
                            self._board[row + j][col + i] = ship[j][i]
                        else:
                            placed = False
                            break
        elif orientation == self.ORIENTATIONS[1] and self.is_valid_placement(
            orientation, ship, row, col
        ):
            # print(row, col, orientation)
            placed = True
            for i in range(len(ship[0])):
                for j in range(len(ship)):
                    if 0 <= row + i < self.rows and 0 <= col + j < self.cols:
                        if self._board[row + i][col + j] != self.SHIP:
                            self._board[row + i][col + j] = ship[j][i]
                        else:
                            placed = False
                            break
        if placed:
            self._board = [
                [self.EMP_SHIP if cell == self.HIT_WATER_TMP else cell for cell in row]
                for row in self._board
            ]
            self._board = [
                [self.SHIP if cell == self.SHIP_TMP else cell for cell in row]
                for row in self._board
            ]
        else:
            self._board = [
                [self.EMP_SHIP if cell == self.HIT_WATER_TMP else cell for cell in row]
                for row in self._board
            ]
            self._board = [
                [self.EMP_SHIP if cell == self.SHIP_TMP else cell for cell in row]
                for row in self._board
            ]

        return placed


    def _generate_ships(self):
        matrix_ships = []
        for ship in self._ships['ships']:
            length = ship['length']
            ship_generated = self._generate_matrix(3, length + 2)
            for x in range(ship['quantity']):
                matrix_ships.append(ship_generated)
        self._ships_work = matrix_ships

    def get_ship(self, index):
        if index < self.length():
            return self._ships_work[index]
        else:
            return None

    def length(self):
        return len(self._ships_work)

    def get_ships_work(self):
        return self._ships_work

    def get_ship_name(self, length):
        for ship_info in self._ships['ships']:
            if ship_info['length'] == length:
                return ship_info['ship']
        return None

    def quantity_ships(self, iterate):
        if not self._ships['ships'] or not isinstance(iterate, int):
            return None  # Handling invalid cases

        total_length = 0
        for index, ship_info in enumerate(self._ships['ships']):
            total_length += ship_info.get('quantity', 0)

            if iterate < total_length:
                break  # Stop the addition when it reaches the indicated position.

        return index

    def _generate_board(self):
        for ship in self._ships_work:
            placed = False
            while not placed:
                placed = self.place_ships_automatic(ship)
        self.num_shoots = sum(
            1 for row in self._board for cell in row if cell == self.SHIP
        )

    def show_board(self):
        print('*' * 20)
        print(' ', end=' ')
        for i in range(0, 10):
            print(i % 10, end=' ')
        print()
        i = 0
        for row in self._board:
            print(i % 10, ' '.join(row))
            i += 1
        print('*' * 20)

    def _count_cells(self, target_value):
        return sum(1 for row in self._board for cell in row if cell == target_value)

    def hits_ship(self):
        return self._count_cells(self.HIT_SHIP)

    def hits_water(self):
        return self._count_cells(self.HIT_WATER)

    def no_hits_ship(self):
        return self._count_cells(self.SHIP)
