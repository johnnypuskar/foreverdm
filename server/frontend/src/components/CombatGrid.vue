<script lang="ts">
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
import { GridRenderable, MapToken } from '@/composables/gridRenderable';
import { DefaultState } from '@/composables/state/defaultState';
import { DragState } from '@/composables/state/dragState';

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
const cellClickable = ref(true);
var clickableItemOffset = ref(0);

const mouseCellPos = reactive({x: null, y: null});

const mousePos = reactive({x: 0, y: 0});

const mousePickedRenderable = ref<GridRenderable | null>(null);

const panOffset = reactive({x: 0, y: 0});

const zoomLevel = ref(1);
const zoomMin = 0.1;
const zoomMax = 2.0;

const tokens = ref<MapToken[]>([]);

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

// Setup mouse state machines
var mouseState = ref(DefaultState.id);
const mouseStates = {
  [DefaultState.id]: new DefaultState(canvasRef, convertMousePosToCellPos, mousePickedRenderable, tokenClickable, propClickable, cellClickable, tokens, highlightCellRegions, highlightCircleRegions),
  [DragState.id]: new DragState(canvasRef, panOffset)
}

function convertMousePosToCellPos(mouseX: number, mouseY: number) {
    const cellX = Math.floor((mouseX - panOffset.x) / zoomLevel.value / cellSize);
    const cellY = Math.floor((mouseY - panOffset.y) / zoomLevel.value / cellSize);
    const inbounds = cellX >= 0 && cellY >= 0 && cellX < props.width && cellY < props.height;
    return { x: cellX, y: cellY, inbounds: inbounds };
}

function handleContextMenu(event: MouseEvent) {
  // Prevent the default context menu from appearing when right-clicking
  event.preventDefault();
}

function handleMouseDown(event: MouseEvent) {
  event.preventDefault();

  const context = ctx.value;
  const canvas = canvasRef.value;
  if (!canvas || !context) return;

  let stateReturnValues = mouseStates[mouseState.value].handleMouseDown(event);
  if (stateReturnValues.state != mouseState.value) {
    mouseState.value = stateReturnValues.state;
    mouseStates[mouseState.value].updateDetails(stateReturnValues.details);
  }
}

function handleMouseMove(event: MouseEvent) {
  event.preventDefault();

  const context = ctx.value;
  const canvas = canvasRef.value;
  if (!canvas || !context) return;
  
  let stateReturnValues = mouseStates[mouseState.value].handleMouseMove(event);
  if (stateReturnValues.state != mouseState.value) {
    mouseState.value = stateReturnValues.state;
    mouseStates[mouseState.value].updateDetails(stateReturnValues.details);
  }
}

function handleMouseUp(event: MouseEvent) {
  event.preventDefault();

  const context = ctx.value;
  const canvas = canvasRef.value;
  if (!canvas || !context) return;

  let stateReturnValues = mouseStates[mouseState.value].handleMouseUp(event);
  if (stateReturnValues.state != mouseState.value) {
    mouseState.value = stateReturnValues.state;
    mouseStates[mouseState.value].updateDetails(stateReturnValues.details);
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
  event.preventDefault();
}

function handleKeyDown(event: KeyboardEvent) {
  if (event.repeat) return;

  const context = ctx.value;
  const canvas = canvasRef.value;
  if (!canvas || !context) return;

  let stateReturnValues = mouseStates[mouseState.value].handleKeyDown(event);
  if (stateReturnValues.state != mouseState.value) {
    mouseState.value = stateReturnValues.state;
    mouseStates[mouseState.value].updateDetails(stateReturnValues.details);
  }
}

onMounted(() => {
  canvasRef.value = document.querySelector('.combat-grid-canvas') as HTMLCanvasElement;
  ctx.value = canvasRef.value.getContext('2d');

  if (!ctx.value) return;

  panOffset.x = (canvasRef.value.clientWidth / 2) - ((cellSize * props.width) / 2);
  panOffset.y = (canvasRef.value.clientHeight / 2) - ((cellSize * props.height) / 2);

  canvasRef.value.addEventListener('click', handleClick);

  canvasRef.value.addEventListener('mouseup', handleMouseUp);
  canvasRef.value.addEventListener('mousedown', handleMouseDown);
  canvasRef.value.addEventListener('mousemove', handleMouseMove);
  canvasRef.value.addEventListener('wheel', handleWheel);
  canvasRef.value.addEventListener('contextmenu', handleContextMenu);

  window.addEventListener('resize', drawGrid);
  window.addEventListener('resize', drawTokens);
  window.addEventListener('resize', drawHighlights);

  window.addEventListener('keydown', handleKeyDown);
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