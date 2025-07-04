import { ref, reactive, Ref, ExtractPropTypes } from 'vue';

// Color Palette
const colors = {
  background: '#f0f0f0',
  borderLine: '#222222',
  gridBackground: '#ffffff',
  gridLine: '#999999'
}

export function useGridMap(
    canvasRef: Ref<HTMLCanvasElement> | null,
    width: Ref<number>,
    height: Ref<number>,
    cellSize: number,
    panOffset: { x: number; y: number },
    zoomLevel: Ref<number>,
    highlightRegions: Ref<Record<string, { x: number; y: number, width: number, height: number, border: string, fill: string }>>,
) {
    function drawGrid() {
        const ctx = canvasRef.value?.getContext('2d');
        if (!ctx || !canvasRef.value) return;
        const context = ctx;

        context.save();
        canvasRef.value.width = canvasRef.value.clientWidth;
        canvasRef.value.height = canvasRef.value.clientHeight;
        context.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

        // Fill Background
        context.fillStyle = colors.background;
        context.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height);

        // Offset Pan & Zoom
        context.translate(panOffset.x, panOffset.y);
        context.scale(zoomLevel.value, zoomLevel.value);

        context.fillStyle = colors.gridBackground;
        context.strokeStyle = colors.gridLine;
        context.lineWidth = 1;
        for (let x = 0; x < width.value; x++) {
            for (let y = 0; y < height.value; y++) {
            context.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            context.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }

        context.strokeStyle = colors.borderLine;
        context.lineWidth = 3;
        context.strokeRect(0, 0, width.value * cellSize, height.value * cellSize);

        // Drop Shadow
        const dropShadowDistance = 8;
        const dropShadowWidth = 12;
        const cornerPoints = [
            { x: width.value * cellSize, y: dropShadowDistance },
            { x: width.value * cellSize, y: height.value * cellSize },
            { x: dropShadowDistance, y: height.value * cellSize },
            { x: dropShadowDistance, y: height.value * cellSize + dropShadowWidth },
            { x: width.value * cellSize + dropShadowWidth, y: height.value * cellSize + dropShadowWidth },
            { x: width.value * cellSize + dropShadowWidth, y: dropShadowDistance }
        ];
        context.fillStyle = 'rgba(0, 0, 0, 0.2)';
        context.beginPath();

        context.moveTo(cornerPoints[0].x, cornerPoints[0].y);
        for (let i = 1; i < cornerPoints.length; i++) {
            const point = cornerPoints[i];
            context.lineTo(point.x, point.y);
        }
        context.closePath();
        context.fill();

        context.restore();
    }

    return {
        drawGrid
    }
}