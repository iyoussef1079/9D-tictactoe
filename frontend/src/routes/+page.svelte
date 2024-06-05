<script lang="ts">
  import ThreeDScene from '../components/3DScene.svelte';
  import { startGame, connectWebSocket, type IGameState } from '../api/game_api';
  import { onMount } from 'svelte';
  import { isWebSocketConnected } from '../api/store';
  import { writable, get } from 'svelte/store';
  import { gameState } from '../api/store';

  let gameStarted = false;
  let errorMessage = '';
  let loading = false;
  let threeDSceneRef: ThreeDScene | null = null;

  // Subscribe to WebSocket connection state

  // Function to handle starting the game
  async function handleStartGame() {
    loading = true;
    try {
      await startGame((newState: IGameState) => {
        if (threeDSceneRef) {
          threeDSceneRef.updateScene(newState);
          gameStarted = true;
          loading = false;
          errorMessage = '';

          gameState.update(state => ({
            ...state,
            gameStarted: true,
            game_id: newState.game_id,
            boards: newState.boards,
            current_player: newState.current_player,
            next_board: newState.next_board,
            game_over: newState.game_over
          }));
        } else {
          errorMessage = '3D Scene is not yet initialized. Please wait.';
          loading = false;
        }
      });
      const state = get(gameState);
      connectWebSocket(state.game_id, (newState: IGameState) => {
        if (threeDSceneRef) {
          threeDSceneRef.updateScene(newState);
        }
      });
    } catch (error: any) {
      errorMessage = 'Failed to start the game. Please try again.';
      loading = false;
    }
  }

  // Establish WebSocket connection on component mount
  onMount(() => {
    const state = get(gameState);
    if (state.game_id) {
      connectWebSocket(state.game_id, (newState: IGameState) => {
        if (threeDSceneRef) {
          console.log('Updating 3D scene with new state:', JSON.stringify(newState));
          threeDSceneRef.updateScene(newState);
        }
      });
    }
  });
</script>

<div class="container h-full mx-auto flex justify-center items-center relative">
  <div class="relative top-0 left-0 m-4">
    <button
      on:click={handleStartGame} 
      class="bg-blue-500 text-white py-2 px-4 rounded"
    >
      {#if loading}Starting...{/if}
      {#if !loading}Start Game{/if}
    </button>
    {#if errorMessage}
      <p class="text-red-500">{errorMessage}</p>
    {/if}
  </div>
  <ThreeDScene bind:this={threeDSceneRef} blur={!gameStarted} />
</div>

<style>
  .container {
    width: 100vh;
    height: 80vh;
  }
  button:disabled {
    background-color: gray;
    cursor: not-allowed;
  }
  .relative {
    position: relative;
  }
  .absolute {
    position: absolute;
  }
</style>
