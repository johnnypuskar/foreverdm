import { ref } from "vue";
import { CanvasLayer } from "./CanvasLayer";

export class GridMapLayer extends CanvasLayer {

    private static readonly CELL_SIZE = 50;
    private static readonly COLORS = {
        background: '#f0f0f0',
        borderLine: '#555555',
        wallLine: '#0f0f0f',
        wallShadow: '#808080',
        gridBackground: '#fdfdfd',
        gridLine: '#999999'
    }

    private mapWidth = 0;
    private mapHeight = 0;

    public initialize(): void {
        this.registerSignal('updateMapData', this.updateMapData);
    }

    public render(): void {
        const ctx = this.getContext();
        const canvas = this.getCanvas();
        if (!ctx || !canvas) return;

        // Drawing Tile Cells
        ctx.lineWidth = 1;
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 8 * this.canvasPanZoom.zoom;
        ctx.shadowOffsetY = 8 * this.canvasPanZoom.zoom;

        for (let x = 0; x < this.mapWidth; x++) {
            for (let y = 0; y < this.mapHeight; y++) {
                // Tile Shadow
                ctx.fillStyle = 'black';
                ctx.strokeStyle = 'transparent';
                ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
                ctx.fillRect(x * GridMapLayer.CELL_SIZE, y * GridMapLayer.CELL_SIZE, GridMapLayer.CELL_SIZE, GridMapLayer.CELL_SIZE);

                // Tile Cell
                ctx.fillStyle = GridMapLayer.COLORS.gridBackground;
                ctx.strokeStyle = GridMapLayer.COLORS.gridLine;
                ctx.shadowColor = 'transparent';
                ctx.fillRect(x * GridMapLayer.CELL_SIZE, y * GridMapLayer.CELL_SIZE, GridMapLayer.CELL_SIZE, GridMapLayer.CELL_SIZE);
                ctx.strokeRect(x * GridMapLayer.CELL_SIZE, y * GridMapLayer.CELL_SIZE, GridMapLayer.CELL_SIZE, GridMapLayer.CELL_SIZE);
            }
        }

        // Draw Border
        ctx.strokeStyle = GridMapLayer.COLORS.borderLine;
        ctx.lineWidth = 3;
        ctx.strokeRect(0, 0, this.mapWidth * GridMapLayer.CELL_SIZE, this.mapHeight * GridMapLayer.CELL_SIZE);
    }

    public updateMapData(mapData: object): void {
        this.mapWidth = mapData['width'];
        this.mapHeight = mapData['height'];
        this.canvasRender();
    }

    public onMouseClick(event: MouseEvent): void {
        this.updateMapData({ width: 7, height: 5 });
    }
}