import { ref, reactive, Ref, ExtractPropTypes } from 'vue';
import { MapToken } from '@/composables/gridRenderable';

const tokenBorderBuffer = 3;

export function useGridTokens(
    canvasRef: Ref<HTMLCanvasElement | null>,
    tokens: Ref<Array<MapToken>>,
    cellSize: number
) {

    function drawTokens() {
        const ctx = canvasRef.value?.getContext('2d');
        if (!ctx || !canvasRef.value) return;
        const context = ctx;

        tokens.value.forEach(token => {
            token.draw(context, cellSize);
        });
    }

    return {
        drawTokens
    }
}