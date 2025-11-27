<script lang="ts">

export interface mapTileWallStructure {
  wall_stats: Array<{
    cover: number,
    passable: boolean,
    movement_penalty: number,
    climb_dc: number
  }>
}

export interface mapTileStructure {
  x: number,
  y: number,
  height: number,
  max_depth: number,
  swimmable: boolean,
  terrain_difficulty: number,
  walls: {
    top: mapTileWallStructure,
    left: mapTileWallStructure,
    bottom: mapTileWallStructure | null,
    right: mapTileWallStructure | null
  }
}

export interface mapTokenStructure {
  id: string,
  x: number,
  y: number,
  height: number,
  name: string | null,
  diameter: number,
}

export interface mapDataStructure {
  width: number,
  height: number,
  max_height: number,
  tiles: Array<mapTileStructure>,
  tokens: Array<mapTokenStructure>
}

export const colors = {
  highlightDark: 'rgba(105, 125, 245, 1.0)',
  highlightLight: 'rgba(0, 55, 255, 0.1)'
}
</script>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive, watchEffect, watch } from 'vue';
import { useGridMap } from '@/composables/gridMap';
import { useGridTokens } from '@/composables/gridTokens';
import { useGridHighlights } from '@/composables/gridHighlights';
import { ScreenRenderable, GridRenderable, MapToken, useGridRenderable } from '@/composables/gridRenderable';
import { DefaultState } from '@/composables/state/defaultState';
import { DragState } from '@/composables/state/dragState';
import { MoveState } from '@/composables/state/moveState';

import { crosshash } from 'crosshash';

const props = defineProps({
    data: {
        type: Object,
        required: true
    }
});

const emit = defineEmits([
  'sendCommand',
  'refreshView'
])

const canvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);
const cellSize = 50;

const mapData = reactive<mapDataStructure>({
  width: 0,
  height: 0,
  max_height: 0,
  tiles: [],
  tokens: []
});
const mapHash = ref<string | null>(null);

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

const mousePos = reactive({x: 0.0, y: 0.0});

const screenRenderables = ref<Array<ScreenRenderable>>([]);
const mousePickedRenderable = ref<GridRenderable | null>(null);

const panOffset = reactive({x: 0, y: 0});

const zoomLevel = ref(1);
const zoomMin = 0.6;
const zoomMax = 2.0;

const renderHeight = ref(0);
const tokens = ref<MapToken[]>([]);

// Set up grid rendering functions
const { drawGrid, drawWalls } = useGridMap(
  canvasRef,
  mapData,
  cellSize,
  panOffset,
  zoomLevel,
  renderHeight,
  highlightCellRegions
);

// Set up token rendering functions
const { drawTokens } = useGridTokens(
  canvasRef,
  tokens,
  cellSize
);

// Set up renderable drawing functions
const { drawRenderables } = useGridRenderable(
  canvasRef,
  cellSize,
  panOffset,
  zoomLevel,
  screenRenderables
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
  [DefaultState.id]: new DefaultState(canvasRef, convertMousePosToCellPos, mousePickedRenderable, screenRenderables, tokenClickable, propClickable, cellClickable, tokens, highlightCellRegions, highlightCircleRegions),
  [DragState.id]: new DragState(canvasRef, panOffset),
  [MoveState.id]: new MoveState(canvasRef, emit, cellSize, panOffset, convertMousePosToCellPos, mousePickedRenderable, tokens, screenRenderables, highlightCircleRegions)
}

function convertMousePosToCellPos(mouseX: number, mouseY: number) {
    const cellX = Math.floor((mouseX - panOffset.x) / zoomLevel.value / cellSize);
    const cellY = Math.floor((mouseY - panOffset.y) / zoomLevel.value / cellSize);
    const inbounds = cellX >= 0 && cellY >= 0 && cellX < mapData['width'] && cellY < mapData['height'];
    return { x: cellX, y: cellY, inbounds: inbounds };
}

function checkMapHash() {
  const liveHash = crosshash(mapData);
  if (liveHash !== mapHash.value) {
    emit('refreshView');
  }
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

  mousePos.x = event.clientX;
  mousePos.y = event.clientY;

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

  panOffset.x = (canvasRef.value.clientWidth / 2) - ((cellSize * mapData['width']) / 2);
  panOffset.y = (canvasRef.value.clientHeight / 2) - ((cellSize * mapData['height']) / 2);

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

function render() {
  drawGrid();
  drawWalls()
  drawTokens();
  drawHighlights();
  drawRenderables();
}

watchEffect(() => {
  render();
});

// Handle data changes and command responses
function handleCommandResponse(newData: any) {
  for (const update of newData.data.updates) {
    var root = mapData;
    while (update['path'].length > 1) {
      root = root[update['path'].shift()];
    }
    root[update['path'][0]] = update['value'];
  }
  mapHash.value = newData.data.hash;
  checkMapHash();
}

watch(() => props.data, (newData) => {
  Object.keys(newData.map).forEach(key => { mapData[key] = newData.map[key]; });
  tokens.value = newData.map.tokens.map(t => new MapToken(t.x, t.y, t.id, "#00FF00", t.diameter));
  mapHash.value = newData.hash;
  render();
}, { immediate: true, deep: true });


defineExpose({
  handleCommandResponse
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
  position: relative;
}

.combat-grid-canvas {
  display: block;
  width: 100%;
  height: 100%;
}
</style>