import unittest
from assertpy import assert_that

from src.entity.board import Board
from src.utils.constants import SHIPS


class TestGenerateBoarad(unittest.TestCase):
    
    GRID_SIZE = 10
    CELL_SIZE = 30
    SEPARATION = 300
    WIDTH, HEIGHT = (
        CELL_SIZE * 2 + GRID_SIZE * CELL_SIZE * 2 + SEPARATION,
        GRID_SIZE * CELL_SIZE + 40,
    )
    OFFSET_WIDTH, OFFSET_HEIGHT = (CELL_SIZE, CELL_SIZE)

    def base(ships):
        common_params = (
            None,
            TestGenerateBoarad.GRID_SIZE,
            TestGenerateBoarad.GRID_SIZE,
            ships,
            TestGenerateBoarad.CELL_SIZE,
            TestGenerateBoarad.OFFSET_WIDTH,
            TestGenerateBoarad.OFFSET_HEIGHT,
            True,
        )
        return common_params
        
        
    def test_generate_board(self):
        try: 
            board = Board(*TestGenerateBoarad.base(SHIPS), "Computer 1")

            assert_that(board.hits_ship() == 0)
            assert_that(board.hits_water() == 0)
            assert_that(board.no_hits_ship() == 0)
        except Exception as ex:
            print (ex)
            assert_that(False)

    def test_generate_new_board_clean(self):
        try: 
            board = Board(*TestGenerateBoarad.base(SHIPS), "Computer 1")
            board.generate_new_board(False)
            assert_that(board.hits_ship() == 0)
            assert_that(board.hits_water() == 0)
            assert_that(board.no_hits_ship() == 0)
        except Exception as ex:
            print (ex)
            assert_that(False)

    def test_generate_new_board_with_ships(self):
        try: 
            board = Board(*TestGenerateBoarad.base(SHIPS), "Computer 1")
            board.generate_new_board(True)
            board.show_board()
            assert_that(board.hits_ship() == 0)
            assert_that(board.hits_water() == 0)
            assert_that(board.no_hits_ship() == 0)
        except Exception as ex:
            print (ex)
            assert_that(False)


    def test_board(self):
        try: 
            m=10
            n=10
            board = Board(m,n,SHIPS)
            boardShips= board.getBoard()
            board.show_board()
            assert_that(True)
        except Exception as ex:
            print (ex)
            assert_that(False)
    
    def test_generate_ships (self):
        SHIPS2 = [
         [["a", "a", "a", "a", "a","a"],
          ["a", "x", "x", "x","x", "a"],
          ["a", "a", "a", "a", "a","a"]],
         [["a", "a", "a", "a","a"],
          ["a", "x", "x","x", "a"],
          ["a", "a", "a", "a","a"]],
         [["a", "a", "a", "a","a"],
          ["a", "x", "x","x", "a"],
          ["a", "a", "a", "a","a"]],
         [["a", "a", "a","a"],
          ["a", "x", "x", "a"],
          ["a", "a", "a","a"]],          
         [["a", "a", "a","a"],
          ["a", "x", "x", "a"],
          ["a", "a", "a","a"]],          
         [["a", "a", "a","a"],
          ["a", "x", "x", "a"],
          ["a", "a", "a","a"]],          
         [["a", "a", "a"],
          ["a", "x", "a"],
          ["a", "a", "a"]],
         [["a", "a", "a"],
          ["a", "x", "a"],
          ["a", "a", "a"]],
         [["a", "a", "a"],
          ["a", "x", "a"],
          ["a", "a", "a"]],
         [["a", "a", "a"],
          ["a", "x", "a"],
          ["a", "a", "a"]]                  
        ]

