<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
  import { sendMove, type IGameState } from '../api/game_api';
  import { gameState } from '../api/store';
  import { get } from 'svelte/store';
  import { Font, FontLoader } from 'three/addons/loaders/FontLoader.js';
  import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
  import * as TWEEN from '@tweenjs/tween.js';

  export let blur = false;

  let container: HTMLDivElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let controls: OrbitControls;
  let renderer: THREE.WebGLRenderer;
  let hoveredObject: any = null;
  let interactiveObjects: THREE.Mesh[] = [];

  let currentTurn: string | null;  // Initialize with default player, change as needed

  // Define variables for colors, materials, and sizes
  const boardColors = {
    right: 0xf0f0f0,
    left: 0xf0f0f0,
    top: 0xf0f0f0,
    bottom: 0xf0f0f0,
    front: 0x333333,
    back: 0x333333
  };

  const cellColor = 0x87cefa; // Light Blue
  const hoverColor = 0xffa500; // Orange
  const xColor = 0x1e90ff; // Dodger Blue
  const oColor = 0xff4500; // Orange Red
  const highlightColor = 0xffff00; // Yellow color for highlight

  const cellSize = { width: 0.2, height: 0.2, depth: 0.02 };
  const boardSize = { width: 0.7, height: 0.7, depth: 0.05 };
  const textSize = 0.2;
  const textHeight = 0.05;

  const cellMaterial = new THREE.MeshBasicMaterial({ color: cellColor });
  const hoverMaterial = new THREE.MeshBasicMaterial({ color: hoverColor });
  const highlightMaterial = new THREE.MeshBasicMaterial({ color: highlightColor });

  // Create materials for each side of the board
  const boardMaterials = [
    new THREE.MeshBasicMaterial({ color: boardColors.right }),  // Right side
    new THREE.MeshBasicMaterial({ color: boardColors.left }),   // Left side
    new THREE.MeshBasicMaterial({ color: boardColors.top }),    // Top side
    new THREE.MeshBasicMaterial({ color: boardColors.bottom }), // Bottom side
    new THREE.MeshBasicMaterial({ color: boardColors.front }),  // Front side
    new THREE.MeshBasicMaterial({ color: boardColors.back })    // Back side
  ];

  const points: Array<THREE.Vector3> = [
    new THREE.Vector3(-0.523903403218816, 0.0593068624413402, -0.8497104919695334),
    new THREE.Vector3(0.5134369135699347, -0.6085150750705706, -0.605055319120192),
    new THREE.Vector3(0.052043229126838716, 0.922412539428712, -0.3826834323650898),
    new THREE.Vector3(-0.7146947070750591, -0.6755077200605489, -0.1813857652008411),
    new THREE.Vector3(1.0, 0.0, 0.0),
    new THREE.Vector3(-0.7146947070750591, 0.6755077200605489, 0.1813857652008411),
    new THREE.Vector3(0.052043229126838716, -0.922412539428712, 0.3826834323650898),
    new THREE.Vector3(0.5134369135699347, 0.6085150750705706, 0.605055319120192),
    new THREE.Vector3(-0.523903403218816, -0.0593068624413402, 0.8497104919695334)
  ];

  const fontLoader = new FontLoader();
  let font: Font;

  fontLoader.load('/fonts/helvetiker_bold.typeface.json', loadedFont => {
    font = loadedFont;
  });

  function createTextGeometry(text: string) {
    return new TextGeometry(text, {
      font: font,
      size: textSize,
      height: textHeight
    });
  }

  function centerGeometry(geometry: THREE.BufferGeometry) {
    geometry.computeBoundingBox();
    const boundingBox = geometry.boundingBox;
    if (!boundingBox) return;
    const centerX = (boundingBox.max.x - boundingBox.min.x) / 2;
    const centerY = (boundingBox.max.y - boundingBox.min.y) / 2;
    geometry.translate(-centerX, -centerY, 0);
  }

  function updateCell(
    boardRow: number, boardCol: number,
    cellRow: number, cellCol: number,
    value: string | null
  ) {
    const cellName = `Cell_${boardRow}_${boardCol}_${cellRow}_${cellCol}`;
    const cell = interactiveObjects.find(obj => obj.name === cellName);

    if (cell) {
      // Replace the cell's geometry with text geometry if X or O
      if (value === 'X' || value === 'O') {
        const textGeometry = createTextGeometry(value);
        centerGeometry(textGeometry);
        cell.geometry.dispose(); // Dispose of the old geometry
        cell.geometry = textGeometry; // Replace the geometry with the new text geometry
        (cell.material as THREE.MeshBasicMaterial).color.set(value === 'X' ? xColor : oColor); // Update the color
        cell.userData.originalColor = value === 'X' ? xColor : oColor; // Save original color
      } else {
        // Restore the original geometry and color if value is null
        const cellGeometry = new THREE.BoxGeometry(cellSize.width, cellSize.height, cellSize.depth);
        cell.geometry.dispose(); // Dispose of the old geometry
        cell.geometry = cellGeometry; // Replace the geometry with the new box geometry
        (cell.material as THREE.MeshBasicMaterial).color.set(cellColor); // Update the color
        cell.userData.originalColor = cellColor; // Save original color
      }
    }
  }

  function calculateCameraPosition(boardPosition: THREE.Vector3, distance: number) {
    const direction = boardPosition.clone().normalize();
    const targetPosition = boardPosition.clone().add(direction.multiplyScalar(distance));
    return targetPosition;
  }

  function focus_on_board(board_index: Array<number>) {
    const boardRow: number = board_index[0];
    const boardCol: number = board_index[1];

    const boardName = `Board_${boardRow}_${boardCol}`;
    const board = scene.getObjectByName(boardName) as THREE.Mesh;

    if (board === undefined) {
      console.error(`Board ${boardRow}, ${boardCol} not found.`);
      return;
    }

    const targetPosition = board.parent ? calculateCameraPosition(board.parent.position, 1) : new THREE.Vector3();

    new TWEEN.Tween(camera.position)
      .to({ x: targetPosition.x, y: targetPosition.y, z: targetPosition.z }, 1000)
      .easing(TWEEN.Easing.Quadratic.Out)
      .start();
    new TWEEN.Tween(controls.target)
      .to({ x: board.position.x, y: board.position.y, z: board.position.z }, 1000)
      .easing(TWEEN.Easing.Quadratic.Out)
      .start();
  }

  function drawWinningSymbol(boardRow: number, boardCol: number, symbol: string) {
    const boardName = `Board_${boardRow}_${boardCol}`;
    const board = scene.getObjectByName(boardName) as THREE.Mesh;

    if (board) {
      const board_parent = board.parent as THREE.Group;
      const textGeometry = createTextGeometry(symbol);
      centerGeometry(textGeometry);

      const material = new THREE.MeshBasicMaterial({ color: symbol === 'X' ? xColor : oColor });
      const textMesh = new THREE.Mesh(textGeometry, material);

      // Position the text mesh to match the board parent's position and rotation
      textMesh.position.copy(board_parent.position);
      textMesh.rotation.copy(board_parent.rotation);

      textMesh.scale.set(3, 3, 3); // Scale up the symbol

      scene.add(textMesh);
    }
  }


  function highlightNextBoard(next_board: Array<number> | null | undefined) {
    scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.name.startsWith('Board_')) {
        object.material = boardMaterials;
      }
    });

    if (!next_board) {
      return;
    }

    const boardRow: number = next_board[0];
    const boardCol: number = next_board[1];

    const boardName = `Board_${boardRow}_${boardCol}`;
    const board = scene.getObjectByName(boardName) as THREE.Mesh;

    if (board) {
      board.material = new THREE.MeshBasicMaterial({ color: highlightColor });
      focus_on_board(next_board);
    }
  }

  export function updateScene(newState: IGameState) {
    if (!newState.gameStarted) {
      console.log('Game not started yet.');
      return;
    }

    newState.boards.forEach((boardRow, boardRowIndex) => {
      boardRow.forEach((board, boardColIndex) => {
        board.forEach((cellRow, cellRowIndex) => {
          cellRow.forEach((cell, cellColIndex) => {
            updateCell(boardRowIndex, boardColIndex, cellRowIndex, cellColIndex, cell);
          });
        });
      });
    });

    if (newState.won_board) {
      for (const [player, boards] of Object.entries(newState.won_board)) {
        boards.forEach(([boardRow, boardCol]) => {
          drawWinningSymbol(boardRow, boardCol, player);
        });
      }
    }

    highlightNextBoard(newState.next_board);
    
    currentTurn = newState.current_player; // Update the current turn
  }

  onMount(() => {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    controls = new OrbitControls(camera, renderer.domElement);

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let needsUpdate = false;

    camera.position.z = 3;
    
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.rotateSpeed = 0.15;

    const geometry = new THREE.BoxGeometry(boardSize.width, boardSize.height, boardSize.depth);
    const cellGeometry = new THREE.BoxGeometry(cellSize.width, cellSize.height, cellSize.depth);

    let boardIndex = 0;
    points.forEach(point => {
      const boardGroup = new THREE.Group();
      boardGroup.position.copy(point);
      boardGroup.lookAt(new THREE.Vector3());

      const boardRow = Math.floor(boardIndex / 3);
      const boardCol = boardIndex % 3;
      boardGroup.name = `Board_Group_${boardRow}_${boardCol}`;

      const squareOutside = new THREE.Mesh(geometry, boardMaterials);
      squareOutside.name = `Board_${boardRow}_${boardCol}`;
      boardGroup.add(squareOutside);

      const gridHelper = new THREE.GridHelper(boardSize.width, 3, cellColor, cellColor);
      gridHelper.position.set(0, 0, -0.03);
      gridHelper.geometry.rotateX(Math.PI / 2);
      gridHelper.lookAt(new THREE.Vector3());
      boardGroup.add(gridHelper);

      for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
          const cell = new THREE.Mesh(cellGeometry, cellMaterial.clone());
          const xOffset = (1 - j) * 0.25;
          const yOffset = (1 - i) * 0.25;
          cell.position.set(xOffset, yOffset, -0.06);
          cell.name = `Cell_${boardRow}_${boardCol}_${i}_${j}`;
          cell.userData.originalColor = cellColor; // Save original color
          boardGroup.add(cell);
          interactiveObjects.push(cell);
        }
      }

      scene.add(boardGroup);
      boardIndex++;
    });

    const animate = () => {
      requestAnimationFrame(animate);
      controls.update(); // only required if damping is enabled
      TWEEN.update();

      if (needsUpdate) {
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveObjects);

        if (intersects.length > 0) {
          if (hoveredObject !== intersects[0].object) {
            if (hoveredObject) {
              hoveredObject.material = new THREE.MeshBasicMaterial({ color: hoveredObject.userData.originalColor });
            }
            hoveredObject = intersects[0].object;
            hoveredObject.material = hoverMaterial.clone();
          }
        } else if (hoveredObject) {
          hoveredObject.material = new THREE.MeshBasicMaterial({ color: hoveredObject.userData.originalColor });
          hoveredObject = null;
        }

        needsUpdate = false;
      }

      renderer.render(scene, camera);
    };
    animate();

    function onMouseMove(event: MouseEvent) {
      const rect = container.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      needsUpdate = true;
    }

    function onMouseClick(event: MouseEvent) {
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(interactiveObjects);

      if (intersects.length > 0) {
        const clickedObject = intersects[0].object;
        const indices = clickedObject.name.split('_').slice(1).map(Number);
        const [boardRow, boardCol, cellRow, cellCol] = indices;

        const state = get(gameState);
        if (!state.gameStarted) {
          alert('Game not started yet.');
          return;
        }

        sendMove(boardRow, boardCol, cellRow, cellCol);
      }
    }

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('click', onMouseClick);

    window.addEventListener('resize', () => {
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    });

    return () => {
      window.removeEventListener('resize', () => {});
      container.removeChild(renderer.domElement);
    };
  });

  $: {
    const state = get(gameState);
    if (state.gameStarted) {
      updateScene(state);
    }
  }
</script>

<div bind:this={container} class="container" class:blur={blur}></div>
{#if currentTurn}
<div class="player-turn">{currentTurn}'s Turn</div>
{/if}

<style>
  .container {
    width: 100vh;
    height: 80vh;
  }

  .blur {
    filter: blur(10px);
  }

  .player-turn {
    position: absolute;
    top: 10px;
    left: 10px;
    font-size: 24px;
    font-weight: bold;
    color: white;
    background-color: black;
    padding: 10px;
    border-radius: 5px;
  }
</style>
