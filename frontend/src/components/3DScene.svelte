<script lang="ts">
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

  let container: HTMLDivElement;

  // Define points on the sphere
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

  onMount(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    // Create materials
    const materials = [
      new THREE.MeshMatcapMaterial({ color: 0xffffff }), // right side
      new THREE.MeshMatcapMaterial({ color: 0xffffff }), // left side
      new THREE.MeshBasicMaterial({ color: 0xffffff }), // top side
      new THREE.MeshBasicMaterial({ color: 0xffffff }), // bottom side
      new THREE.MeshMatcapMaterial({ color: 0xff00ff }), // front side
      new THREE.MeshMatcapMaterial({ color: 0xff0000 })  // back side
    ];

    // Set up camera position
    camera.position.z = 3;

    // Controls to enable camera rotation
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true; // Optional: this provides a smoother rotation feeling
    controls.dampingFactor = 0.1;
    controls.rotateSpeed = 0.07;

    // Define geometry of the square (board)
    const geometry = new THREE.BoxGeometry(0.7, 0.7, 0.05);

    // Define geometry of each cell
    const cellGeometry = new THREE.BoxGeometry(0.2, 0.2, 0.02); // Smaller geometry for each cell
    const cellMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });

    points.forEach(point => {
      const boardGroup = new THREE.Group(); // Group for the board
      boardGroup.position.copy(point);
      boardGroup.lookAt(new THREE.Vector3());

      // Outside square
      const squareOutside = new THREE.Mesh(geometry, materials);
      boardGroup.add(squareOutside);

      // Add grid helper to each square
      const gridHelper = new THREE.GridHelper(0.7, 3, 0xffffff, 0xffffff);
      gridHelper.position.set(0, 0, -0.03);
      gridHelper.geometry.rotateX(Math.PI / 2); // Rotate to match the square's orientation
      gridHelper.lookAt(new THREE.Vector3()); // Align grid with square
      boardGroup.add(gridHelper);

      // Create 9 cells per board
      for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
          const cell = new THREE.Mesh(cellGeometry, cellMaterial);
          cell.position.set(j * 0.25 - 0.25, i * 0.25 - 0.25, -0.06); // Offset cells above the main square
          boardGroup.add(cell);
        }
      }

      scene.add(boardGroup);
    });

    camera.position.z = 3;

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

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
