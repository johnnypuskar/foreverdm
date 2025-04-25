<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, watchEffect, defineProps } from 'vue';

// Color Palette
const colors = {
  background: '#f0f0f0'
}

// Props
const props = defineProps({
  levelData: {type: Object, required: false, default: null}
});

const canvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);
const cellSize = 50;

const panStart = reactive({x: 0, y: 0});
const panOffset = reactive({x: 0, y: 0});
const isPanning = ref(false);

const zoomLevel = ref(1);
const zoomMin = 0.1;
const zoomMax = 2.0;

function drawGrid() {
  if (!ctx.value || !canvasRef.value) return;
  const context = ctx.value;

  context.save();
  canvasRef.value.width = canvasRef.value.clientWidth;
  canvasRef.value.height = canvasRef.value.clientHeight;
  context.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  // Fill Background
  context.fillStyle = colors.background;
  context.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  // Offset Pan & Zoom
  context.translate(panOffset.x, panOffset.y);
  context.scale(zoomLevel.value, zoomLevel.value);

  context.fillStyle = "#0000ff";
  context.strokeStyle = "#000000";
  context.lineWidth = 1;

  context.fillRect(100, 150, 2000, 2000);

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

  if (isPanning.value) return;

  switch (event.button) {
    case 0: // Left Click
      break;
    case 1: // Middle Click
      canvasRef.value.style.cursor = 'grabbing';
      isPanning.value = true;
      panStart.x = event.clientX - panOffset.x;
      panStart.y = event.clientY - panOffset.y;
      break;
    case 2: // Right Click
      break;
  }
}

function handleMouseMove(event: MouseEvent) {
  event.preventDefault();
  if (isPanning.value) {
    if (!Boolean(event.buttons & 4)) {
      // Stop panning if the middle button is somehow released (i.e. cursor offscreen)
      isPanning.value = false;
      canvasRef.value.style.cursor = 'default';
      return;
    }
    panOffset.x = event.clientX - panStart.x;
    panOffset.y = event.clientY - panStart.y;
  }
}

function handleMouseUp(event: MouseEvent) {
  event.preventDefault();

  const context = ctx.value;
  const canvas = canvasRef.value;
  if (!canvas || !context) return;

  switch (event.button) {
    case 0: // Left Click
      break;
    case 1: // Middle Click
      isPanning.value = false;
      canvasRef.value.style.cursor = 'default';
      break;
    case 2: // Right Click
      break;
  }
}

function handleWheel(event: WheelEvent) {
  event.preventDefault();

  if (event.deltaY < 0) {
    // Zoom In
    if (zoomLevel.value >= zoomMax) return;
    zoomLevel.value *= 1.2;
    panOffset.x -= event.clientX * 0.2;
    panOffset.y -= event.clientY * 0.2;
  }
  else if (event.deltaY > 0) {
    // Zoom Out
    if (zoomLevel.value <= zoomMin) return;
    zoomLevel.value *= 0.8;
    panOffset.x += event.clientX * 0.2;
    panOffset.y += event.clientY * 0.2;
  }
  zoomLevel.value = Math.max(zoomMin, Math.min(zoomMax, (Math.round(zoomLevel.value * 100) / 100)));
  if (Math.abs(1.0 - zoomLevel.value) < 0.05) { zoomLevel.value = 1.0; }
  console.log(zoomLevel.value);
}

function handleClick(event: MouseEvent) {

}

onMounted(() => {
  canvasRef.value = document.querySelector('.combat-grid-canvas') as HTMLCanvasElement;
  ctx.value = canvasRef.value.getContext('2d');

  if (!ctx.value) return;

  canvasRef.value.addEventListener('mouseup', handleMouseUp);
  canvasRef.value.addEventListener('mousedown', handleMouseDown);
  canvasRef.value.addEventListener('mousemove', handleMouseMove);
  canvasRef.value.addEventListener('wheel', handleWheel);
  canvasRef.value.addEventListener('contextmenu', handleContextMenu);

  window.addEventListener('resize', drawGrid);
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
}
</style>