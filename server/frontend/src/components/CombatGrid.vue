<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, watchEffect } from 'vue';


// --- State ---
const canvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);

function drawGrid() {
  if (!ctx.value || !canvasRef.value) return;
  const context = ctx.value;

  context.save();
  context.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  context.fillStyle = '#ff0000';
  context.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  context.restore();
}

function handleContextMenu(event: MouseEvent) {
  event.preventDefault();
}

function handleMouseDown(event: MouseEvent) {
  event.preventDefault();

  const context = ctx.value;
  const canvas = canvasRef.value;
  if (!canvas || !context) return;

  console.log(event.button);

  switch (event.button) {
    case 0: // Left Click
      break;
    case 1: // Middle Click
      console.log('Mouse down at:', event.clientX, event.clientY);
      break;
    case 2: // Right Click
      break;
  }
}

function handleMouseMove(event: MouseEvent) {
  
}

function handleMouseUp(event: MouseEvent) {
  
}

function handleWheel(event: WheelEvent) {
  
}

function handleClick(event: MouseEvent) {

}

onMounted(() => {
  canvasRef.value = document.querySelector('.combat-grid-canvas') as HTMLCanvasElement;
  ctx.value = canvasRef.value.getContext('2d');

  if (!ctx.value) return;

  canvasRef.value.addEventListener('mousedown', handleMouseDown);
  canvasRef.value.addEventListener('contextmenu', handleContextMenu);
});

onUnmounted(() => {
  
});

watchEffect(() => {
  drawGrid();
});


</script>

<template>
  <div class="grid-container">
    <canvas ref="canvasRef" class="combat-grid-canvas"></canvas>
  </div>
</template>

<style scoped>
.grid-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative; /* Needed if you add absolutely positioned overlays */
}

.combat-grid-canvas {
  display: block;
  width: 100%;
  height: 100%;
  background-color: #f0f0f0; /* Basic background */
}
</style>