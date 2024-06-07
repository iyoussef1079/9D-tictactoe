import { get, writable } from 'svelte/store';
import { isWebSocketConnected, gameState } from './store';

export interface IGameState {
  gameStarted: boolean;
  game_id: string;
  boards: Array<Array<Array<Array<string | null>>>>;
  current_player?: string;
  next_board?: Array<number>;
  game_over?: boolean;
  won_board?: { [key: string]: Array<Array<number>> }; // New attribute
}

let socket: WebSocket | null = null;
let isSocketConnected = false;

export function connectWebSocket(gameId: string, updateGameStateCallback: (newState: any) => void) {
  socket = new WebSocket(`ws://127.0.0.1:8000/ws/${gameId}`);

  socket.onopen = () => {
    console.log('WebSocket connection established');
    isSocketConnected = true;
    isWebSocketConnected.set(true);
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'game_state') {
      gameState.update(state => ({ ...state, ...data.state, game_id: gameId }));
      updateGameStateCallback(get(gameState));
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

export async function startGame(updateGameStateCallback: (newState: any) => void): Promise<void> {
  try {
    const response = await fetch('http://127.0.0.1:8000/start_game/');
    const data = await response.json();
    gameState.update(state => ({
      ...state,
      game_id: data.state.game_id,
      boards: data.state.boards,
      won_board: data.state.won_board,
      gameStarted: true,
      current_player: data.state.current_player,
    }));
    updateGameStateCallback(get(gameState));
    connectWebSocket(data.state.game_id, updateGameStateCallback);
  } catch (error: any) {
    handleError(error.message);
  }
}

export async function getBoard(gameId: string, updateGameStateCallback: (newState: any) => void): Promise<void> {
  try {
    const response = await fetch(`http://127.0.0.1:8000/get_board/${gameId}`);
    const data = await response.json();
    gameState.update(state => ({
      ...state,
      boards: data.boards,
      won_board: data.won_board,  // Include won_board in the state
      game_id: gameId
    }));
    updateGameStateCallback(get(gameState));
  } catch (error: any) {
    handleError(error.message);
  }
}

export function sendMove(boardRow: number, boardCol: number, cellRow: number, cellCol: number) {
  if (socket && get(gameState).game_id) {
    const move = {
      type: 'make_move',
      move: {
        game_id: get(gameState).game_id,
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
