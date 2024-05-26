<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
  import { sendMove, type IGameState } from '../api/game_api';

  export let gameState: IGameState;

  let container: HTMLDivElement;
  let hoveredObject: any = null;
  let interactiveObjects: THREE.Mesh[] = [];
  const cellMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });

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

  function updateCell(
    boardRow: number,
    boardCol: number,
    cellRow: number,
    cellCol: number,
    value: string | null
  ) {
    const cellName = `Cell_${boardRow}_${boardCol}_${cellRow}_${cellCol}`;
    const cell = interactiveObjects.find(obj => obj.name === cellName);
    if (cell) {
      if (value === 'X') {
        cell.material = new THREE.MeshBasicMaterial({ color: 0x0000ff });
      } else if (value === 'O') {
        cell.material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
      } else {
        cell.material = cellMaterial;
      }
    }
  }

  export function updateScene(newState: IGameState) {
    alert('Updating 3D scene with new state: ' + JSON.stringify(newState));
    newState.boards.forEach((boardRow, boardRowIndex) => {
      boardRow.forEach((board, boardColIndex) => {
        board.forEach((cellRow, cellRowIndex) => {
          cellRow.forEach((cell, cellColIndex) => {
            updateCell(boardRowIndex, boardColIndex, cellRowIndex, cellColIndex, cell);
          });
        });
      });
    });
  }

  onMount(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();

    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let needsUpdate = false;

    const hoverMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });

    const materials = [
      new THREE.MeshMatcapMaterial({ color: 0xffffff }), // right side
      new THREE.MeshMatcapMaterial({ color: 0xffffff }), // left side
      new THREE.MeshBasicMaterial({ color: 0xffffff }), // top side
      new THREE.MeshBasicMaterial({ color: 0xffffff }), // bottom side
      new THREE.MeshMatcapMaterial({ color: 0xff00ff }), // front side
      new THREE.MeshMatcapMaterial({ color: 0xff0000 })  // back side
    ];

    camera.position.z = 3;
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.rotateSpeed = 0.15;

    const geometry = new THREE.BoxGeometry(0.7, 0.7, 0.05);
    const cellGeometry = new THREE.BoxGeometry(0.2, 0.2, 0.02);

    let boardIndex = 0;
    points.forEach(point => {
      const boardGroup = new THREE.Group();
      boardGroup.position.copy(point);
      boardGroup.lookAt(new THREE.Vector3());

      const boardRow = Math.floor(boardIndex / 3);
      const boardCol = boardIndex % 3;
      boardGroup.name = `Board_${boardRow}_${boardCol}`;

      const squareOutside = new THREE.Mesh(geometry, materials);
      boardGroup.add(squareOutside);

      const gridHelper = new THREE.GridHelper(0.7, 3, 0xffffff, 0xffffff);
      gridHelper.position.set(0, 0, -0.03);
      gridHelper.geometry.rotateX(Math.PI / 2);
      gridHelper.lookAt(new THREE.Vector3());
      boardGroup.add(gridHelper);

      for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
          const cell = new THREE.Mesh(cellGeometry, cellMaterial);
          const xOffset = (1 - j) * 0.25;
          const yOffset = (1 - i) * 0.25; // Adjust to make (0,0) at top-left
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
</script>

<div bind:this={container} class="container"></div>

<style>
  .container {
    width: 100vh;
    height: 80vh;
  }
</style>
