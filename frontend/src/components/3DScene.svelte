<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
  import { sendMove, type IGameState } from '../api/game_api';
  import { gameState } from '../api/store';
  import { get } from 'svelte/store';
  import { Font, FontLoader } from 'three/addons/loaders/FontLoader.js';
  import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

  export let blur = false;

  let container: HTMLDivElement;
  let scene: THREE.Scene;
  let camera: THREE.PerspectiveCamera;
  let renderer: THREE.WebGLRenderer;
  let hoveredObject: any = null;
  let interactiveObjects: THREE.Mesh[] = [];

  // Define variables for colors, materials, and sizes
  const boardColors = {
    right: 0xffffff,
    left: 0xffffff,
    top: 0xffffff,
    bottom: 0xffffff,
    front: 0xff00ff,
    back: 0xff0000
  };

  const cellColor = 0xffffff;
  const hoverColor = 0xff0000;

  const cellSize = { width: 0.2, height: 0.2, depth: 0.02 };
  const boardSize = { width: 0.7, height: 0.7, depth: 0.05 };
  const textSize = 0.2;
  const textHeight = 0.05;

  const cellMaterial = new THREE.MeshBasicMaterial({ color: cellColor });
  const hoverMaterial = new THREE.MeshBasicMaterial({ color: hoverColor });

  // Create materials for each side of the board
  const boardMaterials = [
    new THREE.MeshBasicMaterial({ color: boardColors.right }),  // Right side
    new THREE.MeshBasicMaterial({ color: boardColors.left }),   // Left side
    new THREE.MeshBasicMaterial({ color: boardColors.top }),    // Top side
    new THREE.MeshBasicMaterial({ color: boardColors.bottom }), // Bottom side
    new THREE.MeshBasicMaterial({ color: boardColors.front }),  // Front side
    new THREE.MeshBasicMaterial({ color: boardColors.back })    // Back side
  ];

  const xColor = 0x0000ff;
  const oColor = 0xff0000;

  const highlightColor = 0xffff00; // Yellow color for highlight
  const highlightMaterial = new THREE.MeshBasicMaterial({ color: highlightColor });

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

  function updateCell(
    boardRow: number, boardCol: number,
    cellRow: number, cellCol: number,
    value: string | null
  ) {
    const cellName = `Cell_${boardRow}_${boardCol}_${cellRow}_${cellCol}`;
    const cell = interactiveObjects.find(obj => obj.name === cellName);

    if (cell) {
      // Remove existing text if any
      if (cell.userData.textMesh) {
        scene.remove(cell.userData.textMesh);
        cell.userData.textMesh.geometry.dispose();
        cell.userData.textMesh.material.dispose();
        delete cell.userData.textMesh;
      }

      if (value === 'X' || value === 'O') {
        const textGeometry = createTextGeometry(value);
        cell.geometry.dispose(); // Dispose of the old geometry
        cell.geometry = textGeometry; // Replace the geometry with the new text geometry
        cell.geometry.translate(-0.075, -0.12, 0);
        (cell.material as THREE.MeshBasicMaterial).color.set(value === 'X' ? xColor : oColor); // Update the color
      } else {
        delete cell.userData.textMesh;
        cell.visible = true;
        cell.material = cellMaterial;
      }
    }
  }

  function highlightNextBoard(boardRow: number, boardCol: number) {
    scene.traverse((object) => {
      if (object instanceof THREE.Mesh && object.name.startsWith('Board_')) {
        object.material = boardMaterials;
      }
    });

    const boardName = `Board_${boardRow}_${boardCol}`;
    const board = scene.getObjectByName(boardName) as THREE.Mesh;

    if (board) {
      board.material = new THREE.MeshBasicMaterial({ color: highlightColor });
      console.log(board.name);
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

    if (newState.next_board) {
      highlightNextBoard(newState.next_board[0], newState.next_board[1]);
    }
  }

  onMount(() => {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer();

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let needsUpdate = false;

    camera.position.z = 3;
    const controls = new OrbitControls(camera, renderer.domElement);
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
          const cell = new THREE.Mesh(cellGeometry, cellMaterial);
          const xOffset = (1 - j) * 0.25;
          const yOffset = (1 - i) * 0.25;
          cell.position.set(xOffset, yOffset, -0.06);
          cell.name = `Cell_${boardRow}_${boardCol}_${i}_${j}`;
          boardGroup.add(cell);
          interactiveObjects.push(cell);
        }
      }

      scene.add(boardGroup);
      boardIndex++;
    });

    const animate = () => {
      requestAnimationFrame(animate);

      if (needsUpdate) {
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveObjects);

        if (intersects.length > 0) {
          if (hoveredObject !== intersects[0].object) {
            if (hoveredObject) {
              hoveredObject.material = cellMaterial;
            }
            hoveredObject = intersects[0].object;
            hoveredObject.material = hoverMaterial;
          }
        } else if (hoveredObject) {
          hoveredObject.material = cellMaterial;
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

<style>
  .container {
    width: 100vh;
    height: 80vh;
  }

 .blur {
    filter: blur(10px);
  }
</style>
