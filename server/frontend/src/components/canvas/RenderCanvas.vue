<script setup lang="ts">
import { ref, onMounted, provide, reactive, watchEffect, onUnmounted } from 'vue';
import { CanvasLayer } from '@/scripts/canvas/CanvasLayer';

const props = withDefaults(defineProps<{
    allowPan?: boolean;
    allowZoom?: boolean;
}>(), {
    allowPan: true,
    allowZoom: true
});

// Pan and zoom values
const MIN_ZOOM = 0.6;
const MAX_ZOOM = 2.0;
const panZoomLevels = reactive({x: 0, y: 0, zoom: 1.0});

// HTML canvas values and layers
const canvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);
const layers = ref<CanvasLayer[]>([]);

// RenderCanvas data interface for passing to layers
export interface RenderCanvasData {
    getCanvas: () => HTMLCanvasElement | null;
    getContext: () => CanvasRenderingContext2D | null;
    panZoomLevels: { x: number, y: number, zoom: number };
    insertLayer: (layer: CanvasLayer) => void;
    emitSignal: (signalName: string, ...args: any[]) => void;
    render: () => void;
}
const renderCanvas: RenderCanvasData = {
    getCanvas: () => canvasRef.value,
    getContext: () => ctx.value,
    panZoomLevels: panZoomLevels,
    insertLayer: (layer: CanvasLayer) => {
        layers.value.push(layer);
        layers.value.sort((a, b) => a.zIndex - b.zIndex);
    },
    emitSignal: emitSignal,
    render: render
}
provide('renderCanvas', renderCanvas);

defineExpose({
    renderCanvas
});

function render() {
    if(!ctx.value || !canvasRef.value) { return; }

    const dpr = window.devicePixelRatio || 1;
    canvasRef.value.width = canvasRef.value.clientWidth * dpr;
    canvasRef.value.height = canvasRef.value.clientHeight * dpr;

    ctx.value.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    ctx.value.save();

    ctx.value.translate(panZoomLevels.x, panZoomLevels.y);
    ctx.value.scale(panZoomLevels.zoom, panZoomLevels.zoom);

    layers.value.forEach(layer => layer.render());

    ctx.value.restore();
}

function emitSignal(signalName: string, ...args: any[]) {
    layers.value.forEach(layer => layer.receiveSignal(signalName, ...args));
}

onMounted(() => {
    ctx.value = canvasRef.value?.getContext('2d') || null;
    window.addEventListener('resize', render);

    // Disable context menu on right-click
    canvasRef.value.addEventListener('contextmenu', (e) => e.preventDefault());
});

onUnmounted(() => {
    window.removeEventListener('resize', render);
});
</script>

<template>
    <div class="w-full h-full overflow-hidden position-relative">
        <canvas ref="canvasRef" class="w-full h-full display-block"></canvas>
        <slot></slot>
    </div>
</template>