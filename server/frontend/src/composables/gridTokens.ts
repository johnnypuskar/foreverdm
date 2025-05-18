import { ref, reactive, Ref, ExtractPropTypes } from 'vue';
import { combatGridPropsDefinition } from '@/components/CombatGrid.vue';

export interface Token {
  x: number;
  y: number;
  highlighted: boolean;
}

type PropsType = ExtractPropTypes<typeof combatGridPropsDefinition>;

const tokenBorderBuffer = 3;

export function useGridTokens(
    canvasRef: Ref<HTMLCanvasElement | null>,
    tokens: Ref<Array<Token>>,
    cellSize: number
) {
    function drawTokenAtGridPosition(context: CanvasRenderingContext2D, x: number, y: number) {
        context.save();

        context.fillStyle = "#aaaaff";
        context.beginPath()
        context.arc(x * cellSize + cellSize / 2.0, y * cellSize + cellSize / 2.0, cellSize / 2.0 - tokenBorderBuffer, 0, Math.PI * 2);
        context.fill();
        context.strokeStyle = "#000000";
        context.lineWidth = 2;
        context.stroke();
        context.closePath();

        context.restore();
    }

    function drawTokens() {
        const ctx = canvasRef.value?.getContext('2d');
        if (!ctx || !canvasRef.value) return;
        const context = ctx;

        tokens.value.forEach(token => {
            drawTokenAtGridPosition(context, token.x, token.y);
        });
    }

    return {
        drawTokens
    }
}