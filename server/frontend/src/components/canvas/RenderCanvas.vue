<script setup lang="ts">
import { ref, onMounted, provide, reactive } from 'vue';
import { CanvasLayer } from '@/scripts/canvas/CanvasLayer';

const MIN_ZOOM = 0.6;
const MAX_ZOOM = 2.0;
const zoomLevel = ref(1);
const panOffset = reactive({x: 0, y: 0});

const canvasRef = ref<HTMLCanvasElement | null>(null);
const ctx = ref<CanvasRenderingContext2D | null>(null);
const layers = ref<CanvasLayer[]>([]);

provide('renderCanvas', {
    getCanvas: () => canvasRef.value,
    getContext: () => ctx.value,
    insertLayer: (layer: CanvasLayer) => {
        layers.value.push(layer);
        layers.value.sort((a, b) => a.zIndex - b.zIndex);
    },
    render: () => render()
});

function render() {
    if(!ctx.value || !canvasRef.value) { return; }

    ctx.value.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

    ctx.value.translate(panOffset.x, panOffset.y);
    ctx.value.scale(zoomLevel.value, zoomLevel.value);

    layers.value.forEach(layer => layer.render());
}

onMounted(() => {
    ctx.value = canvasRef.value?.getContext('2d') || null;
});
</script>

<template>
<div class="w-full h-full overflow-hidden position-relative">
    <canvas ref="canvasRef" class="w-full h-full display-block"></canvas>
</div>
</template>