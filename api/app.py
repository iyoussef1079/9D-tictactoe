from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Assuming GameController, GameChecker9D, Board_9D are defined appropriately
from core.game_controller import GameController
from core.board_9D import Board_9D
from core.game_checker_9d import GameChecker9D
from core.rule import StandardUltimateTicTacToeRule

app = FastAPI()

# Game storage - simple dictionary to hold game instances by game ID
games = {}

class Move(BaseModel):
    game_id: str
    board_position: tuple
    cell_position: tuple

@app.post("/start_game/")
async def start_game():
    game_id = str(len(games) + 1)  # simple unique ID generation
    board = Board_9D()
    game_checker = GameChecker9D()
    rule = StandardUltimateTicTacToeRule()
    game_controller = GameController(board, game_checker, rule)
    games[game_id] = game_controller
    return {"message": "Game started", "game_id": game_id}

@app.post("/make_move/")
async def make_move(move: Move):
    game = games.get(move.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    try:
        game_over = game.play_move(move.board_position, move.cell_position)
        return {"message": "Move successful", "game_over": game_over}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_board/{game_id}")
async def get_board(game_id: str):
    game: GameController = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return game.board.to_serializable()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
