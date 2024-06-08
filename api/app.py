import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import List, Dict, Any
import traceback

# Assuming GameController, GameChecker9D, Board_9D are defined appropriately
from core.ai_player import RandomAIPlayer
from core.alpha_zero_player import AlphaZeroAIPlayer
from core.game_controller import GameController
from core.board_9D import Board_9D
from core.game_checker_9d import GameChecker9D
from core.min_max_player import MinimaxAIPlayer
from core.rule import StandardUltimateTicTacToeRule

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Game storage - simple dictionary to hold game instances by game ID
games: Dict[str, GameController] = {}
clients: Dict[str, List[WebSocket]] = {}

class Move(BaseModel):
    game_id: str
    board_position: List[int]
    cell_position: List[int]

model_path = "ml/GoodUltimate2019-03-03 21_06_38+MCTS600+cpuct4.h5"

@app.get("/start_game/")
async def start_game(ai: bool = False):
    game_id = str(len(games) + 1)
    board = Board_9D()
    game_checker = GameChecker9D()
    rule = StandardUltimateTicTacToeRule()
    ai_player = MinimaxAIPlayer("AI", 'O', max_depth=4) if ai else None
    game_controller = GameController(game_id, board, game_checker, rule, ai_player)
    games[game_id] = game_controller
    return {"type": "game_state", "state": game_controller.get_state()}

@app.get("/start_game_with_ai/")
async def start_game_with_ai():
    print("Starting game with AI")
    return await start_game(ai=True)


@app.get("/get_board/{game_id}")
async def get_board(game_id: str):
    game: GameController = games.get(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    return game.get_state()

@app.post("/make_move/")
async def make_move(move: Move):
    game: GameController = games.get(move.game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    try:
        game.play_move(move.board_position, move.cell_position)
        state = game.get_state()
        return state
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    if game_id not in clients:
        clients[game_id] = []
    clients[game_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['type'] == 'make_move':
                move = Move(**message['move'])
                game: GameController = games.get(move.game_id)
                if not game:
                    await websocket.send_text(json.dumps({"type": "error", "message": "Game not found"}))
                    continue
                try:
                    # User play move
                    game.play_move(move.board_position, move.cell_position)
                    state = game.get_state()
                    print(f"Sending game state for game: {move.game_id}")
                    response = json.dumps({"type": "game_state", "state": state.to_dict()})
                    for client in clients[move.game_id]:
                        await client.send_text(response)

                    await asyncio.sleep(2)

                    # AI move (if applicable)
                    if game.ai_player and game.current_player.symbol == game.ai_player.symbol:
                        game.play_ai_move()
                        state = game.get_state()
                        print(f"Type of next_board: {type(state.next_board)}")
                        response = json.dumps({"type": "game_state", "state": state.to_dict()})
                        for client in clients[move.game_id]:
                            await client.send_text(response)
                except Exception as e:
                    tb_str = traceback.format_exception(e)
                    print(tb_str)
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    except WebSocketDisconnect:
        clients[game_id].remove(websocket)
        if not clients[game_id]:
            del clients[game_id]
        print(f"Client {websocket.client} disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
