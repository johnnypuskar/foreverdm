<script lang="ts">
import { Token } from '@/composables/gridTokens';
// Props Definition
export const combatGridPropsDefinition = {
  width: { type: Number, default: 0 },
  height: { type: Number, default: 0 }
}

export const colors = {
  highlightDark: 'rgba(105, 125, 245, 1.0)',
  highlightLight: 'rgba(0, 55, 255, 0.1)'
}
</script>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, watchEffect, defineProps } from 'vue';
import { useGridMap } from '@/composables/gridMap';
import { useGridTokens } from '@/composables/gridTokens';
import { useGridHighlights } from '@/composables/gridHighlights';

const props = defineProps(combatGridPropsDefinition);

const canvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);
const cellSize = 50;

const highlightCellRegions = ref<Record<string, {
  x: number,
  y: number,
  width: number,
  height: number,
  border: string,
  fill: string
}>>({});

const highlightCircleRegions = ref<Record<string, {
  x: number,
  y: number,
  size: number,
  border: string,
  fill: string
}>>({});

const tokenClickable = ref(true);
const propClickable = ref(false);
const tileClickable = ref(true);
const mouseCellPos = reactive({x: null, y: null});

const panStart = reactive({x: 0, y: 0});
const panOffset = reactive({x: 0, y: 0});
const isPanning = ref(false);

const zoomLevel = ref(1);
const zoomMin = 0.1;
const zoomMax = 2.0;

const tokens = ref<Token[]>([]);

// Set up grid rendering functions
const { drawGrid } = useGridMap(
  canvasRef,
  props,
  cellSize,
  panOffset,
  zoomLevel,
  highlightCellRegions
);

// Set up token rendering functions
const { drawTokens } = useGridTokens(
  canvasRef,
  tokens,
  cellSize
);

// Set up highlight selection functions
const { drawHighlights } = useGridHighlights(
  canvasRef,
  cellSize,
  highlightCellRegions,
  highlightCircleRegions
);

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
    case 0: // Left Mouse
      break;
    case 1: // Middle Mouse
      canvasRef.value.style.cursor = 'grabbing';
      isPanning.value = true;
      panStart.x = event.clientX - panOffset.x;
      panStart.y = event.clientY - panOffset.y;
      break;
    case 2: // Right Mouse
      console.log('Right Mouse Button Clicked');
      tokens.value.push(
        {
          x: 0,
          y: 0,
          highlighted: false
        }
      )
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
  else {
    mouseCellPos.x = Math.floor((event.clientX - panOffset.x) / zoomLevel.value / cellSize);
    mouseCellPos.y = Math.floor((event.clientY - panOffset.y) / zoomLevel.value / cellSize);

    canvasRef.value.style.cursor = 'default';
    if (mouseCellPos.x < 0 || mouseCellPos.y < 0 || mouseCellPos.x > props.width - 1 || mouseCellPos.y > props.height - 1) {
      if (highlightCellRegions.value.hasOwnProperty('mouseCellHighlight')) {
        delete highlightCellRegions.value['mouseCellHighlight'];
      }
      if (highlightCircleRegions.value.hasOwnProperty('mouseTokenHighlight')) {
        delete highlightCircleRegions.value['mouseTokenHighlight'];
      }
    }
    else {
      if(tokenClickable.value && tokens.value.some(token => token.x === mouseCellPos.x && token.y === mouseCellPos.y)) {
        if (highlightCellRegions.value.hasOwnProperty('mouseCellHighlight')) {
          delete highlightCellRegions.value['mouseCellHighlight'];
        }

        canvasRef.value.style.cursor = 'grab';
        
        highlightCircleRegions.value['mouseTokenHighlight'] = {
          x: mouseCellPos.x,
          y: mouseCellPos.y,
          size: 1,
          border: colors.highlightDark,
          fill: colors.highlightLight
        }
      }
      else if(tileClickable.value) {
        if (highlightCircleRegions.value.hasOwnProperty('mouseTokenHighlight')) {
          delete highlightCircleRegions.value['mouseTokenHighlight'];
        }

        highlightCellRegions.value['mouseCellHighlight'] = {
          x: mouseCellPos.x,
          y: mouseCellPos.y,
          width: 1,
          height: 1,
          border: colors.highlightDark,
          fill: colors.highlightLight
        }
      }
    }
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

  const rect = canvasRef.value.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  const oldWorldX = (mouseX - panOffset.x) / zoomLevel.value;
  const oldWorldY = (mouseY - panOffset.y) / zoomLevel.value;

  const oldZoomLevel = zoomLevel.value;
  let newZoomLevel = oldZoomLevel;

  if (event.deltaY < 0) {
    // Zoom In
    if (oldZoomLevel >= zoomMax) return;
    newZoomLevel *= 1.2;
  }
  else if (event.deltaY > 0) {
    // Zoom Out
    if (oldZoomLevel <= zoomMin) return;
    newZoomLevel *= 0.8;
  }

  newZoomLevel = Math.max(zoomMin, Math.min(zoomMax, newZoomLevel));
  if (Math.abs(1.0 - newZoomLevel) < 0.05) { newZoomLevel = 1.0; }

  if (newZoomLevel === oldZoomLevel) return;

  zoomLevel.value = newZoomLevel;

  panOffset.x = mouseX - oldWorldX * zoomLevel.value;
  panOffset.y = mouseY - oldWorldY * zoomLevel.value;
}

function handleClick(event: MouseEvent) {

}

onMounted(() => {
  canvasRef.value = document.querySelector('.combat-grid-canvas') as HTMLCanvasElement;
  ctx.value = canvasRef.value.getContext('2d');

  if (!ctx.value) return;

  panOffset.x = (canvasRef.value.clientWidth / 2) - ((cellSize * props.width) / 2);
  panOffset.y = (canvasRef.value.clientHeight / 2) - ((cellSize * props.height) / 2);

  canvasRef.value.addEventListener('mouseup', handleMouseUp);
  canvasRef.value.addEventListener('mousedown', handleMouseDown);
  canvasRef.value.addEventListener('mousemove', handleMouseMove);
  canvasRef.value.addEventListener('wheel', handleWheel);
  canvasRef.value.addEventListener('contextmenu', handleContextMenu);

  window.addEventListener('resize', drawGrid);
  window.addEventListener('resize', drawTokens);
  window.addEventListener('resize', drawHighlights);
});

onUnmounted(() => {
  
});

watchEffect(() => {
  drawGrid();
  drawTokens();
  drawHighlights();
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