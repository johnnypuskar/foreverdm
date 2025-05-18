import { ref, reactive, Ref } from 'vue';

export function useGridHighlights(
    canvasRef: Ref<HTMLCanvasElement | null>,
    cellSize: number,
    highlightCellRegions: Ref<Record<string, { x: number; y: number, width: number, height: number, border: string, fill: string }>>,
    highlightCircleRegions: Ref<Record<string, { x: number; y: number, size: number, border: string, fill: string }>>
) {
    function drawHighlights() {
        const ctx = canvasRef.value?.getContext('2d');
        if (!ctx || !canvasRef.value) return;
        const context = ctx;

        context.save();

        // Draw cell region highlights
        for (const highlightRegionKey in highlightCellRegions.value) {
            const region = highlightCellRegions.value[highlightRegionKey];
            context.fillStyle = region.fill;
            context.strokeStyle = region.border;
            context.lineWidth = 4;
            context.fillRect(region.x * cellSize, region.y * cellSize, region.width * cellSize, region.height * cellSize);
            context.strokeRect(region.x * cellSize, region.y * cellSize, region.width * cellSize, region.height * cellSize);
        }

        // Draw circular region highlights
        for (const highlightRegionKey in highlightCircleRegions.value) {
            const region = highlightCircleRegions.value[highlightRegionKey];
            context.fillStyle = region.fill;
            context.strokeStyle = region.border;
            context.lineWidth = 4;
            context.beginPath();
            context.arc(region.x * cellSize + cellSize / 2.0, region.y * cellSize + cellSize / 2.0, region.size * cellSize / 2, 0, Math.PI * 2);
            context.fill();
            context.stroke();
        }

        context.restore();
    }

    return {
        drawHighlights
    }
}