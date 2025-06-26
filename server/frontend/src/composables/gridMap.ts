import { ref, reactive, Ref, ExtractPropTypes, Reactive, render } from 'vue';
import { mapDataStructure } from '@/components/CombatGrid.vue';

// Color Palette
const colors = {
  background: '#f0f0f0',
  borderLine: '#555555',
  wallLine: '#0f0f0f',
  wallShadow: '#808080',
  gridBackground: '#fdfdfd',
  gridLine: '#999999'
}

export function useGridMap(
    canvasRef: Ref<HTMLCanvasElement> | null,
    mapData: Reactive<mapDataStructure>,
    cellSize: number,
    panOffset: { x: number; y: number },
    zoomLevel: Ref<number>,
    renderHeight: Ref<number>,
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

        context.lineWidth = 1;
        context.shadowBlur = 0;
        context.shadowOffsetX = 12 * zoomLevel.value;
        context.shadowOffsetY = 12 * zoomLevel.value;
        for (let x = 0; x < mapData['width']; x++) {
            for (let y = 0; y < mapData['height']; y++) {
                // Tile Shadow
                context.fillStyle = 'black';
                context.strokeStyle = 'transparent';
                context.shadowColor = 'rgba(0, 0, 0, 0.2)';
                context.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);

                // Tile Cell
                context.fillStyle = colors.gridBackground;
                context.strokeStyle = colors.gridLine;
                context.shadowColor = 'transparent';
                context.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
                context.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }
        }
        
        for (let x = mapData['width'] - 1; x >= 0; x--) {
            for (let y = mapData['height'] - 1; y >= 0; y--) {
            }
        }

        context.strokeStyle = colors.borderLine;
        context.lineWidth = 3;
        context.strokeRect(0, 0, mapData['width'] * cellSize, mapData['height'] * cellSize);

        context.restore();
    }

    function drawWalls() {
        const ctx = canvasRef.value?.getContext('2d');
        if (!ctx || !canvasRef.value) return;
        const context = ctx;

        context.save();

        console.log(mapData["tiles"][0].y);
        context.beginPath();
        console.log(mapData['tiles']);
        for (const tile of mapData['tiles']) {
            const x = tile.x * cellSize;
            const y = tile.y * cellSize;
            const walls = tile['walls'] || {};

            const positionOffsets = {
                top: { x: 0, y: 0 },
                left: { x: 0, y: 0 },
                bottom: { x: 0, y: cellSize },
                right: { x: cellSize, y: 0 }
            }
            const drawingOffsets = {
                top: { x: cellSize, y: 0 },
                left: { x: 0, y: cellSize },
                bottom: { x: cellSize, y: cellSize },
                right: { x: cellSize, y: cellSize }
            }

            for (const side of ['top', 'left', 'bottom', 'right']) {
                if (walls[side] === undefined) { continue; }
                const wallStats = walls[side]['wall_stats'];
                if (!wallStats[renderHeight.value].passable) {
                    context.moveTo(x + positionOffsets[side].x, y + positionOffsets[side].y);
                    context.lineTo(x + drawingOffsets[side].x, y + drawingOffsets[side].y);
                }
            }
        }
        context.shadowColor = colors.wallShadow;
        context.shadowBlur = 4;
        context.shadowOffsetX = 2 * zoomLevel.value;
        context.shadowOffsetY = 2 * zoomLevel.value;
        context.strokeStyle = colors.wallLine;
        context.lineCap = 'square';
        context.lineWidth = 6;
        context.stroke();
        context.closePath();

        context.restore();
    }

    return {
        drawGrid,
        drawWalls
    }
}