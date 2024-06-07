from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import List, Dict, Any

# Assuming GameController, GameChecker9D, Board_9D are defined appropriately
from core.game_controller import GameController
from core.board_9D import Board_9D
from core.game_checker_9d import GameChecker9D
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

@app.get("/start_game/")
async def start_game():
    game_id = str(len(games) + 1)  # simple unique ID generation
    board = Board_9D()
    game_checker = GameChecker9D()
    rule = StandardUltimateTicTacToeRule()
    game_controller = GameController(game_id, board, game_checker, rule)
    games[game_id] = game_controller
    return {"type": "game_state", "state": game_controller.get_state()}

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
                    game.play_move(move.board_position, move.cell_position)
                    state = game.get_state()
                    print(f"Sending game state: {state}")
                    response = json.dumps({"type": "game_state", "state": state.to_dict()})
                    for client in clients[move.game_id]:
                        await client.send_text(response)
                except Exception as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    except WebSocketDisconnect:
        clients[game_id].remove(websocket)
        if not clients[game_id]:
            del clients[game_id]
        print(f"Client {websocket.client} disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
