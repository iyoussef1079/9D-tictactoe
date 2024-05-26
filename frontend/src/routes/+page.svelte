<script lang="ts">
  import ThreeDScene from '../components/3DScene.svelte';
  import { startGame, connectWebSocket, gameState, type IGameState } from '../api/game_api';
  import { onMount } from 'svelte';
  import { isWebSocketConnected } from '../api/store';
  import { writable } from 'svelte/store';

  let gameStarted = false;
  let errorMessage = '';
  let loading = false;
  let threeDSceneRef: ThreeDScene | null = null;
  const isConnected = writable(false);

  // Subscribe to WebSocket connection state
  $: isWebSocketConnected.subscribe(value => isConnected.set(value));

  // Function to handle starting the game
  function handleStartGame() {
    if (!$isConnected) {
      errorMessage = 'WebSocket is not connected. Please try again.';
      return;
    }
    loading = true;
    startGame((newState: IGameState) => {
      if (threeDSceneRef) {
        threeDSceneRef.updateScene(newState);
        gameStarted = true;
        loading = false;
        errorMessage = '';
      } else {
        errorMessage = '3D Scene is not yet initialized. Please wait.';
        loading = false;
      }
    }).catch(error => {
      errorMessage = 'Failed to start the game. Please try again.';
      loading = false;
    });
  }

  // Establish WebSocket connection on component mount
  onMount(() => {
    connectWebSocket((newState: IGameState) => {
      if (threeDSceneRef) {
        console.log('Updating 3D scene with new state:', JSON.stringify(newState));
        threeDSceneRef.updateScene(newState);
      }
    });
  });
</script>

<div class="container h-full mx-auto flex justify-center items-center relative">
  <div class="absolute top-0 left-0 m-4">
    <button 
      on:click={handleStartGame} 
      class="bg-blue-500 text-white py-2 px-4 rounded"
      disabled={!$isConnected}
    >
      Start Game
    </button>
    {#if errorMessage}
      <p class="text-red-500">{errorMessage}</p>
    {/if}
    {#if loading}
      <p>Loading...</p>
    {/if}
  </div>
  <ThreeDScene bind:this={threeDSceneRef} {gameState} />
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
