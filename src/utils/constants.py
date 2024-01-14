TITTLE = "War ships"
SHIPS = {
    "ships": [
        {"ship": "Aircraft", "length": 4, "quantity": 1},
        {"ship": "Battleship", "length": 3, "quantity": 2},
        {"ship": "Destroyer", "length": 2, "quantity": 3},
        {"ship": "Submarine", "length": 1, "quantity": 4},
    ]
}
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Configuration
GRID_SIZE = 10
CELL_SIZE = 30
SEPARATION = 300
WIDTH, HEIGHT = (
    CELL_SIZE * 2 + GRID_SIZE * CELL_SIZE * 2 + SEPARATION,
    GRID_SIZE * CELL_SIZE + 40,
)
OFFSET_WIDTH, OFFSET_HEIGHT = (CELL_SIZE, CELL_SIZE)
