import { isWebSocketConnected } from './store';

export interface IGameState {
    game_id: string;
    boards: Array<Array<Array<Array<string | null>>>>
}

export let gameState: IGameState = {
  game_id: '',
  boards: Array(3).fill(null).map(() =>
    Array(3).fill(null).map(() =>
      Array(3).fill(null).map(() => Array(3).fill(null))
    )
  )
};

let socket: WebSocket | null = null;
let isSocketConnected = false;

export function connectWebSocket(updateGameStateCallback: (newState: any) => void) {
  socket = new WebSocket('ws://127.0.0.1:8000/ws/game');

  socket.onopen = () => {
    console.log('WebSocket connection established');
    isSocketConnected = true;
    isWebSocketConnected.set(true);
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'game_state' || data.type === 'game_started') {
      gameState = { game_id: data.game_id, ...data.state };
      updateGameStateCallback(gameState);
    } else if (data.type === 'error') {
      handleError(data.message);
    }
  };

  socket.onclose = () => {
    console.log('WebSocket connection closed');
    isSocketConnected = false;
    isWebSocketConnected.set(false);
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
}

function waitForSocketConnection(callback: () => void) {
  setTimeout(() => {
    if (isSocketConnected) {
      callback();
    } else {
      waitForSocketConnection(callback);
    }
  }, 100);
}

export function startGame(updateGameStateCallback: (newState: any) => void): Promise<void> {
  return new Promise((resolve, reject) => {
    if (socket) {
      const message = { type: 'start_game' };
      waitForSocketConnection(() => {
        console.log('Sending start game message', message);
        socket!.send(JSON.stringify(message));
        socket!.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('Received message:', data);
          if (data.type === 'game_started') {
            gameState = { game_id: data.game_id, ...data.state };
            updateGameStateCallback(gameState);
            resolve();
          } else if (data.type === 'error') {
            handleError(data.message);
            reject(data.message);
          }
        };
      });
    } else {
      reject('WebSocket is not connected');
    }
  });
}

export function sendMove(boardRow: number, boardCol: number, cellRow: number, cellCol: number) {
  if (socket && gameState.game_id) {
    const move = {
      type: 'make_move',
      move: {
        game_id: gameState.game_id,
        board_position: [boardRow, boardCol],
        cell_position: [cellRow, cellCol]
      }
    };
    console.log('Sending move:', JSON.stringify(move));
    waitForSocketConnection(() => {
      socket!.send(JSON.stringify(move));
    });
  }
}

function handleError(message: string) {
  alert(message);
}
