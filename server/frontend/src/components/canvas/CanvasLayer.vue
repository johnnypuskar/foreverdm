<script setup lang="ts">
import { inject, onMounted, Reactive } from 'vue';
import { CanvasLayer } from '@/scripts/canvas/CanvasLayer';
import type { RenderCanvas } from '@/components/canvas/RenderCanvas.vue';

const renderCanvas = inject('renderCanvas') as RenderCanvas;
const props = withDefaults(defineProps<{
    layer: new (renderCanvas: RenderCanvas, zIndex: number) => CanvasLayer;
    zIndex?: number;
}>(), {
    zIndex: 0
});

onMounted(() => {
    let layer = new props.layer(renderCanvas, props.zIndex);
    renderCanvas.insertLayer(layer);
});

</script>

<template>

</template>