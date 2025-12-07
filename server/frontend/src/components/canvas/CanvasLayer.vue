<script setup lang="ts">
import { inject, onMounted, Reactive, ref } from 'vue';
import { CanvasLayer } from '@/scripts/canvas/CanvasLayer';
import type { RenderCanvasData } from '@/components/canvas/RenderCanvas.vue';

const renderCanvas = inject('renderCanvas') as RenderCanvasData;
const props = withDefaults(defineProps<{
    layer: new (renderCanvas: RenderCanvasData, zIndex: number) => CanvasLayer;
    zIndex?: number;
}>(), {
    zIndex: 0
});
const layer = ref<CanvasLayer | null>(null);

onMounted(() => {
    layer.value = new props.layer(renderCanvas, props.zIndex);
    renderCanvas.insertLayer(layer.value as CanvasLayer);
});

defineExpose({
    layer
});
</script>

<template>

</template>