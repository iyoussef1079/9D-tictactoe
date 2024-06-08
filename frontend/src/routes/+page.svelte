<script lang="ts">
  import ThreeDScene from '../components/3DScene.svelte';
  import MiniMap from '../components/MiniMap.svelte';
  import { startGame, startGameVsAi, connectWebSocket, type IGameState } from '../api/game_api';
  import { onMount } from 'svelte';
  import { writable, get } from 'svelte/store';
  import { gameState } from '../api/store';

  let gameStarted = false;
  let errorMessage = '';
  let loading = false;
  let threeDSceneRef: ThreeDScene | null = null;

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

  async function handleStartGameVsAi() {
  loading = true;
  try {
    await startGameVsAi((newState: IGameState) => {
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
    errorMessage = 'Failed to start the game against AI. Please try again.';
    loading = false;
  }
}


  onMount(() => {
    const state = get(gameState);
    if (state.game_id) {
      connectWebSocket(state.game_id, (newState: IGameState) => {
        if (threeDSceneRef) {
          threeDSceneRef.updateScene(newState);
        }
      });
    }
  });
</script>

<div class="container mx-auto flex flex-col items-center justify-center min-h-screen bg-dark text-white p-4 relative">
  <div class="controls mb-4">
    <button
      on:click={handleStartGame}
      class="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded"
    >
      {#if loading && !gameStarted}Starting...{/if}
      {#if !loading || gameStarted}Start Game{/if}
    </button>
    <button
      on:click={handleStartGameVsAi}
      class="bg-green-500 hover:bg-green-700 text-white py-2 px-4 rounded mt-2"
    >
      {#if loading && !gameStarted}Starting...{/if}
      {#if !loading || gameStarted}Play Against AI{/if}
    </button>
    {#if errorMessage}
      <p class="text-red-500 mt-2">{errorMessage}</p>
    {/if}
  </div>
  <div class="flex flex-col lg:flex-row lg:space-x-8 w-full items-center lg:items-start">
    <div class="scene-container flex-grow lg:flex-shrink-0 p-4 bg-dark-secondary rounded-lg mb-4 lg:mb-0 w-full lg:w-auto relative">
      <ThreeDScene bind:this={threeDSceneRef} blur={!gameStarted} />
    </div>
    <div class="minimap-container flex-grow lg:flex-shrink-0 p-4 bg-dark-secondary rounded-lg w-full lg:w-auto">
      <MiniMap {threeDSceneRef} />
    </div>
  </div>
</div>


<style>
  :global(body) {
    margin: 0;
    font-family: Arial, sans-serif;
    background-color: #121212;
    color: #ffffff;
  }
  .container {
    max-width: 1200px;
  }
  .controls {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .scene-container, .minimap-container {
    display: flex;
    justify-content: center;
    align-items: center;
    border: 2px solid #333;
  }
  .scene-container {
    max-width: 100%;
  }
  .minimap-container {
    max-width: 100%;
  }
  .bg-dark {
    background-color: #121212;
  }
  .bg-dark-secondary {
    background-color: #1e1e1e;
  }
  .player-turn {
    position: absolute;
    top: 10px;
    left: 10px;
    font-size: 24px;
    font-weight: bold;
    color: black;
    background-color: rgb(0, 192, 251);
    padding: 10px;
    border-radius: 5px;
  }
  button:disabled {
    background-color: gray;
    cursor: not-allowed;
  }
</style>
