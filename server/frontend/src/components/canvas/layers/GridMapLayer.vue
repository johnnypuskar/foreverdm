<script setup lang="ts">
import { inject, onMounted } from 'vue';
import { CanvasLayer } from '@/scripts/canvas/CanvasLayer';

const renderCanvas = inject('renderCanvas') as any;
const props = defineProps({
    zIndex: { type: Number, default: 0 }
});

class GridMapLayer extends CanvasLayer {
    public render(): void {

    }
}

onMounted(() => {
    let layer = new GridMapLayer(props.zIndex);
    renderCanvas.insertLayer(layer);
});

</script>