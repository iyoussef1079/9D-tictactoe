// game_api.ts
export let gameState = {
  boards: Array(3).fill(null).map(() =>
    Array(3).fill(null).map(() =>
      Array(3).fill(null).map(() => Array(3).fill(null))
    )
  )
};

let socket: WebSocket | null = null;

export function connectWebSocket(updateGameStateCallback: (newState: any) => void) {
  socket = new WebSocket('ws://your_server/ws/game');

  socket.onopen = () => {
    console.log('WebSocket connection established');
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'game_state') {
      gameState = data.state;
      updateGameStateCallback(gameState);
    } else if (data.type === 'error') {
      handleError(data.message);
    }
  };

  socket.onclose = () => {
    console.log('WebSocket connection closed');
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
}

export async function startGame(updateGameStateCallback: (newState: any) => void) {
  const response = await fetch('/api/start_game');
  const initialState = await response.json();
  gameState = initialState;
  updateGameStateCallback(gameState);
}

export function sendMove(boardRow: number, boardCol: number, cellRow: number, cellCol: number) {
  const move = { type: 'make_move', boardRow, boardCol, cellRow, cellCol };
  if (socket) {
    socket.send(JSON.stringify(move));
  }
}

function handleError(message: string) {
  alert(message);
}
