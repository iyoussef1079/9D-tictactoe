<script lang="ts">
  import { onMount } from 'svelte';
  import { gameState } from '../api/store';
  import { get } from 'svelte/store';
  import { type IGameState } from '../api/game_api';

  export let threeDSceneRef: any;

  const rows = 3;
  const cols = 3;

  function isNextBoard(boardRow: number, boardCol: number, nextBoard: Array<number> | null): boolean {
    return nextBoard !== null && nextBoard !== undefined && nextBoard[0] === boardRow && nextBoard[1] === boardCol;
  }

  function handleBoardClick(boardRow: number, boardCol: number) {
    console.log(`Focus on board: [${boardRow}, ${boardCol}]`);
    if (threeDSceneRef) {
      threeDSceneRef.focus_on_board([boardRow, boardCol]);
    }
  }

  function handleKeyPress(event: KeyboardEvent, boardRow: number, boardCol: number) {
    if (event.key === 'Enter' || event.key === ' ') {
      handleBoardClick(boardRow, boardCol);
    }
  }

  function getCellValue(boardRow: number, boardCol: number, cellRow: number, cellCol: number, state: IGameState): string {
    return state.boards[boardRow][boardCol][cellRow][cellCol] || '';
  }

  // Reactive declaration to subscribe to the gameState store
  $: state = $gameState;
</script>

<style>
  .ultimate-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 10px;
    width: 100%;
    max-width: 300px;
    height: auto;
    aspect-ratio: 1;
    border: 2px solid black;
  }
  .mini-board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 2px;
    width: 100%;
    height: 100%;
    border: 2px solid #333;
    cursor: pointer;
  }
  .mini-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    aspect-ratio: 1;
    border: 1px solid #ccc;
  }
  .highlight {
    background-color: yellow;
  }
</style>

<div class="ultimate-board">
  {#each Array(rows) as _, boardRow}
    {#each Array(cols) as _, boardCol}
      <div
        class="mini-board {isNextBoard(boardRow, boardCol, state.next_board) ? 'highlight' : ''}"
        on:click={() => handleBoardClick(boardRow, boardCol)}
        role="button"
        tabindex="0"
        on:keypress={(event) => handleKeyPress(event, boardRow, boardCol)}
      >
        {#each Array(rows) as _, cellRow}
          {#each Array(cols) as _, cellCol}
            <div class="mini-cell">
              {getCellValue(boardRow, boardCol, cellRow, cellCol, state)}
            </div>
          {/each}
        {/each}
      </div>
    {/each}
  {/each}
</div>
