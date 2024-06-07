import { writable } from 'svelte/store';
import type { IGameState } from './game_api';

export const isWebSocketConnected = writable(false);

export const gameState = writable<IGameState>({
    game_id: '',
    boards: Array(3).fill(null).map(() =>
        Array(3).fill(null).map(() =>
            Array(3).fill(null).map(() => Array(3).fill(null))
        )
    ),
    gameStarted: false,
    won_board: { 'X': [], 'O': [] } // Initialize won_board in the store
});