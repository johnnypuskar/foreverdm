<script setup lang="ts">
import { onMounted, reactive, ref, watch, watchEffect, } from 'vue';
import RenderCanvas, { RenderCanvasData } from '@/components/canvas/RenderCanvas.vue';
import CanvasLayer from '@/components/canvas/CanvasLayer.vue';
import { GridMapLayer } from '@/scripts/canvas/GridMapLayer';
import { GridMapHighlightLayer, RectHighlightRegion } from '@/scripts/canvas/GridMapHighlightLayer';
import { GridMapTokenLayer } from '@/scripts/canvas/GridMapTokenLayer';
import { GridMapMouseState, GridMapMouseStateDefault } from '@/scripts/states/GridMapMouseStates';

const mapData = reactive({ width: 7, height: 7 });

const renderCanvas = ref<InstanceType<typeof RenderCanvas> | null>(null);
const gridMapLayer = ref<InstanceType<typeof CanvasLayer> | null>(null);
const gridMapTokenLayer = ref<InstanceType<typeof CanvasLayer> | null>(null);
const gridMapHighlightLayer = ref<InstanceType<typeof CanvasLayer> | null>(null);

const mouseState = ref<GridMapMouseState | null>(null);

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
    gridMapComponents.renderCanvas = renderCanvas.value.renderCanvas;
    gridMapComponents.gridMapLayer = gridMapLayer.value.layer as GridMapLayer;
    gridMapComponents.gridMapTokenLayer = gridMapTokenLayer.value.layer as GridMapTokenLayer;
    gridMapComponents.gridMapHighlightLayer = gridMapHighlightLayer.value.layer as GridMapHighlightLayer;

    mouseState.value = new GridMapMouseStateDefault(gridMapComponents as GridMapComponents);

    // Attach event listeners to delegate to current mouse state
    gridMapComponents.renderCanvas.getCanvas().addEventListener('mousemove', (e) => { mouseState.value?.onMouseMove(e); });
    gridMapComponents.renderCanvas.getCanvas().addEventListener('wheel', (e) => { mouseState.value?.onMouseWheel(e); });
    gridMapComponents.renderCanvas.getCanvas().addEventListener('mousedown', (e) => { mouseState.value?.onMouseDown(e); });
    gridMapComponents.renderCanvas.getCanvas().addEventListener('mouseup', (e) => { mouseState.value?.onMouseUp(e); });
    window.addEventListener('keydown', (e) => { mouseState.value?.onKeyDown(e); });

    gridMapComponents.gridMapLayer.updateMapData(
        mapData.width,
        mapData.height
    );
    gridMapComponents.renderCanvas.render();

});

watchEffect(() => {
    // Highlight Selected Cell
    const mousePos = mouseState.value?.mousePosition;
    const selectedCell = gridMapComponents.gridMapLayer?.getCellAtScreenPos(mousePos?.x || -1, mousePos?.y || -1);
    if (selectedCell) {
        gridMapComponents.gridMapHighlightLayer?.addHighlightRegion(new RectHighlightRegion(
            selectedCell.x * GridMapLayer.CELL_SIZE,
            selectedCell.y * GridMapLayer.CELL_SIZE,
            GridMapHighlightLayer.COLOR_DARK,
            GridMapHighlightLayer.COLOR_LIGHT,
            GridMapLayer.CELL_SIZE,
            GridMapLayer.CELL_SIZE
        ));
    }
    
    gridMapComponents.renderCanvas?.render();
});

</script>

<template>
    <RenderCanvas ref="renderCanvas">
        <CanvasLayer ref="gridMapLayer" :layer="GridMapLayer" />
        <CanvasLayer ref="gridMapTokenLayer" :layer="GridMapTokenLayer" :z-index="1"/>
        <CanvasLayer ref="gridMapHighlightLayer" :layer="GridMapHighlightLayer" :z-index="2"/>
    </RenderCanvas>
</template>