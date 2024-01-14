import unittest
from assertpy import assert_that

from src.entity.board import Board
from src.utils.constants import SHIPS


class TestGenerateBoard(unittest.TestCase):
    GRID_SIZE = 10
    CELL_SIZE = 30
    SEPARATION = 300
    WIDTH, HEIGHT = (
        CELL_SIZE * 2 + GRID_SIZE * CELL_SIZE * 2 + SEPARATION,
        GRID_SIZE * CELL_SIZE + 40,
    )
    OFFSET_WIDTH, OFFSET_HEIGHT = (CELL_SIZE, CELL_SIZE)

    SHIPS_ERROR = {"ships": [{"shipa": "Barco 1", "length": 1, "quantity": 1}]}

    SHIPS1 = {"ships": [{"ship": "Submarine", "length": 1, "quantity": 1}]}

    SHIPS2 = {
        "ships": [
            {"ship": "Submarine", "length": 1, "quantity": 1},
            {"ship": "Battleship", "length": 3, "quantity": 2},
        ]
    }

    SHIPS4 = {
        "ships": [
            {"ship": "Aircraft", "length": 4, "quantity": 1},
            {"ship": "Battleship", "length": 3, "quantity": 2},
            {"ship": "Destroyer", "length": 2, "quantity": 3},
            {"ship": "Submarine", "length": 1, "quantity": 4},
        ]
    }

    def base(ships):
        common_params = (
            None,
            TestGenerateBoard.GRID_SIZE,
            TestGenerateBoard.GRID_SIZE,
            ships,
            TestGenerateBoard.CELL_SIZE,
            TestGenerateBoard.OFFSET_WIDTH,
            TestGenerateBoard.OFFSET_HEIGHT,
        )
        return common_params

    def validate_ship(ship):
        required_fields = ["ship", "length", "quantity"]
        for field in required_fields:
            if field not in ship:
                return False
            return True

    def validate_ships(ships):
        for ship in ships:
            if not TestGenerateBoard.validate_ship(ship):
                return False
        return True

    def _count_cells(board, target_value):
        return sum(
            inner_list.count(target_value)
            for outer_list in board
            for inner_list in outer_list
        )

    def test_validate_ships(self):
        assert_that(
            TestGenerateBoard.validate_ships(TestGenerateBoard.SHIPS_ERROR["ships"])
        ).is_false()

        assert_that(
            TestGenerateBoard.validate_ships(TestGenerateBoard.SHIPS1["ships"])
        ).is_true()
        assert_that(
            TestGenerateBoard.validate_ships(TestGenerateBoard.SHIPS2["ships"])
        ).is_true()
        assert_that(TestGenerateBoard.validate_ships(SHIPS["ships"])).is_true()

    def get_data_ships(ships):
        sum = 0
        total_a = 0
        total_x = 0
        total_quantity = 0
        for ship in ships["ships"]:
            length = ship["length"]
            quantity = ship["quantity"]
            total_quantity += quantity
            length_ships = (length + 2) * quantity
            total = length_ships * 3
            total_x += length * quantity
            total_a += total - (length * quantity)
            sum += total

        return total_quantity, 3, sum, total_a, total_x

    def get_data_ships_work(ships):
        a = TestGenerateBoard._count_cells(ships, Board.HIT_WATER_TMP)
        x = TestGenerateBoard._count_cells(ships, Board.SHIP_TMP)
        space = TestGenerateBoard._count_cells(ships, Board.EMP_SHIP)

        return len(ships), len(ships[0]), (a + x + space), a, x

    def validate_ships_with_ships_work(ships):
        board = Board(*TestGenerateBoard.base(ships), "Computer 1")
        work = board.get_ships_work()
        ship = TestGenerateBoard.get_data_ships(ships)
        work = TestGenerateBoard.get_data_ships_work(work)
        return ship == work

    def test_validate_ships_work(self):
        assert_that(
            TestGenerateBoard.validate_ships_with_ships_work(TestGenerateBoard.SHIPS1)
        ).is_true()
        assert_that(
            TestGenerateBoard.validate_ships_with_ships_work(TestGenerateBoard.SHIPS2)
        ).is_true()
        assert_that(
            TestGenerateBoard.validate_ships_with_ships_work(TestGenerateBoard.SHIPS4)
        ).is_true()

    def test_validate_board(self):
        board = Board(*TestGenerateBoard.base(SHIPS), "Computer 1")
        assert_that(board.length() >= 0).is_true()

    def test_generate_board(self):
        board = Board(*TestGenerateBoard.base(SHIPS), "Computer 1")

        assert_that(board.hits_ship()).is_equal_to(0)
        assert_that(board.hits_water()).is_equal_to(0)
        assert_that(board.no_hits_ship()).is_equal_to(0)

    def test_generate_new_board_clean(self):
        board = Board(*TestGenerateBoard.base(SHIPS), "Computer 1")
        board.generate_new_board(False)
        assert_that(board.hits_ship()).is_equal_to(0)
        assert_that(board.hits_water()).is_equal_to(0)
        assert_that(board.no_hits_ship()).is_equal_to(0)

    def test_generate_new_board_with_ships(self):
        board = Board(*TestGenerateBoard.base(SHIPS), "Computer 1")
        board.generate_new_board(True)
        print(board.hits_ship(), board.hits_water(), board.no_hits_ship())
        assert_that(board.hits_ship()).is_equal_to(0)
        assert_that(board.hits_water()).is_equal_to(0)
        total_length = sum(ship["length"] * ship["quantity"] for ship in SHIPS["ships"])
        assert_that(board.no_hits_ship()).is_equal_to(total_length)

    def test_player(self):
        name_player = "Computer 1"
        board = Board(*TestGenerateBoard.base(SHIPS), name_player)
        player = board.get_player(True)
        assert_that(name_player == player).is_true()
        name_player = "Computer 1...."
        board.set_player(name_player)
        player = board.get_player()
        assert_that(name_player == player).is_false()
        player = board.get_player(True)
        assert_that(name_player == player).is_false()

        board = Board(*TestGenerateBoard.base(SHIPS), "Computer 1")
        yy, xx, last_direction = board.new_shot(Board.NO_SHOT, Board.NEW_SHOT)
        if board.get_status_grid(yy, xx) == Board.SHIP:
            status = "hit"
            sunk = board.check_if_sunk((yy, xx))
            if sunk is not None:
                status = f"sunk {sunk}"
        elif board.get_status_grid(yy, xx) == Board.EMP_SHIP:
            status = "water"
        elif status.get_status_grid(yy, xx) == Board.HIT_WATER:
            status = "water again"
        else:
            status = "error"

        board.set_last_shot((yy, xx), last_direction, status)
        board.set_last_shot(Board.NEW_SHOT, Board.NO_DIRECTION, Board.NO_STATUS)
        shot, last_direction, last_status = board.get_last_shot()
        assert_that(
            (shot, last_direction, last_status)
            == (Board.NEW_SHOT, Board.NO_DIRECTION, Board.NO_STATUS)
        ).is_true()

        shot, last_direction, last_status = board.get_last_shot()
        print(shot, last_direction, last_status)
        assert_that(
            (shot, last_direction, last_status)
            == ((yy, xx), Board.NO_DIRECTION, status)
        ).is_true()

    def test_plus_shot(self):
        board = Board(*TestGenerateBoard.base(SHIPS), "Computer 1")
        last_shots = board.get_shots()
        board.plus_shot()
        assert_that(board.get_shots() == last_shots + 1).is_true()

    def test_get_ship_name(self):
        board = Board(*TestGenerateBoard.base(SHIPS), "Computer 1")
        for ship in SHIPS["ships"]:
            name = ship["ship"]
            length = ship["length"]
            assert_that(board.get_ship_name(length) == name).is_true()

    def test_quantity_ships(self):
        board = Board(*TestGenerateBoard.base(TestGenerateBoard.SHIPS1), "Computer 1")
        assert_that(board.quantity_ships(0) == 0).is_true()
        assert_that(board.quantity_ships(1) == 0).is_true()

        board = Board(*TestGenerateBoard.base(TestGenerateBoard.SHIPS2), "Computer 1")

        assert_that(board.quantity_ships(0) == 0).is_true()
        assert_that(board.quantity_ships(1) == 1).is_true()
        assert_that(board.quantity_ships(2) == 1).is_true()

        board = Board(*TestGenerateBoard.base(TestGenerateBoard.SHIPS4), "Computer 1")
        assert_that(board.quantity_ships(0) == 0).is_true()

        assert_that(board.quantity_ships(1) == 1).is_true()
        assert_that(board.quantity_ships(2) == 1).is_true()

        assert_that(board.quantity_ships(3) == 2).is_true()
        assert_that(board.quantity_ships(4) == 2).is_true()
        assert_that(board.quantity_ships(5) == 2).is_true()

        assert_that(board.quantity_ships(6) == 3).is_true()
        assert_that(board.quantity_ships(7) == 3).is_true()
        assert_that(board.quantity_ships(8) == 3).is_true()
        assert_that(board.quantity_ships(9) == 3).is_true()

    def test_generate_new_board(self):
        ships = TestGenerateBoard.SHIPS4
        for x in range(0, 1000):
            board = Board(*TestGenerateBoard.base(ships), "Computer 1")
            board.generate_new_board(True)
            ok = True
            rows = TestGenerateBoard.GRID_SIZE
            cols = TestGenerateBoard.GRID_SIZE
            for row in range(0, rows):
                for column in range(0, cols):
                    if board.get_status_grid(row, column) == Board.SHIP:
                        board.set_status_grid(row, column, Board.HIT_SHIP)
                        ok = board.put_water((row, column))
                        if not ok:
                            print(row, column)
                            break
            if not ok:
                board.show_board()
            assert_that(ok).is_true()
