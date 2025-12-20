<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue';
import RenderCanvas, { RenderCanvasData } from '@/components/canvas/RenderCanvas.vue';
import CanvasLayer from '@/components/canvas/CanvasLayer.vue';
import { GridMapLayer } from '@/scripts/canvas/GridMapLayer';
import { GridMapHighlightLayer } from '@/scripts/canvas/GridMapHighlightLayer';
import { GridMapTokenLayer } from '@/scripts/canvas/GridMapTokenLayer';
import { GridMapMouseState, GridMapMouseStateDefault } from '@/scripts/states/GridMapMouseStates';

const props = defineProps({
    cellSize: { type: Number, default: 50 }
});

const mapData = reactive({ width: 7, height: 7, tokens: [
    { name: 'test', x: 2, y: 3, diameter: 1, color: 'red' }
] });

const renderCanvas = ref<InstanceType<typeof RenderCanvas> | null>(null);
const gridMapLayer = ref<InstanceType<typeof CanvasLayer> | null>(null);
const gridMapTokenLayer = ref<InstanceType<typeof CanvasLayer> | null>(null);
const gridMapHighlightLayer = ref<InstanceType<typeof CanvasLayer> | null>(null);

const mouseState = ref<GridMapMouseState | null>(null);

// Define interface used for passing GridMap layers to GridMapMouseState
export interface GridMapComponents {
    renderCanvas: RenderCanvasData;
    gridMapLayer: GridMapLayer | null;
    gridMapTokenLayer: GridMapTokenLayer | null;
    gridMapHighlightLayer: GridMapHighlightLayer | null;
    setMouseState: (state: GridMapMouseState) => void;
}
const gridMapComponents = reactive<GridMapComponents>({
    renderCanvas: null as RenderCanvasData,
    gridMapLayer: null as GridMapLayer,
    gridMapTokenLayer: null as GridMapTokenLayer,
    gridMapHighlightLayer: null as GridMapHighlightLayer,
    setMouseState: (state: GridMapMouseState) => {
        mouseState.value = state;
    }
});

onMounted(() => {
    // Populate component interface values
    gridMapComponents.renderCanvas = renderCanvas.value.renderCanvas;
    gridMapComponents.gridMapLayer = gridMapLayer.value.layer as GridMapLayer;
    gridMapComponents.gridMapTokenLayer = gridMapTokenLayer.value.layer as GridMapTokenLayer;
    gridMapComponents.gridMapHighlightLayer = gridMapHighlightLayer.value.layer as GridMapHighlightLayer;

    // Initialize mouse state to default
    mouseState.value = new GridMapMouseStateDefault(gridMapComponents as GridMapComponents);

    // Attach event listeners to delegate to current mouse state
    gridMapComponents.renderCanvas.getCanvas().addEventListener('mousemove', (e) => { mouseState.value?.onMouseMove(e); });
    gridMapComponents.renderCanvas.getCanvas().addEventListener('wheel', (e) => { mouseState.value?.onMouseWheel(e); });
    gridMapComponents.renderCanvas.getCanvas().addEventListener('mousedown', (e) => { mouseState.value?.onMouseDown(e); });
    gridMapComponents.renderCanvas.getCanvas().addEventListener('mouseup', (e) => { mouseState.value?.onMouseUp(e); });
    window.addEventListener('keydown', (e) => { mouseState.value?.onKeyDown(e); });

    // Initialize grid map layer with map and initial display data
    gridMapComponents.gridMapLayer.cellSize = props.cellSize;
    gridMapComponents.gridMapLayer.updateMapData(
        mapData.width,
        mapData.height
    );
    gridMapComponents.gridMapLayer.centerOnScreen(); /* Triggers initial render */
});

// Define component values to reactively render to any value updates
watch(
    [
        () => gridMapComponents.renderCanvas?.panZoomLevels,
        () => gridMapComponents.gridMapHighlightLayer?.highlightIndex,
        () => gridMapComponents.gridMapTokenLayer?.tokens,
        () => mouseState.value?.reactiveProperties
    ],
    () => {
        gridMapComponents.renderCanvas?.render();
    },
    { deep: true, immediate: true }
);
</script>

<template>
    <RenderCanvas ref="renderCanvas">
        <CanvasLayer ref="gridMapLayer" :layer="GridMapLayer" />
        <CanvasLayer ref="gridMapTokenLayer" :layer="GridMapTokenLayer" :z-index="1"/>
        <CanvasLayer ref="gridMapHighlightLayer" :layer="GridMapHighlightLayer" :z-index="2"/>
    </RenderCanvas>
</template>