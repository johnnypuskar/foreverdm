import { ref } from "vue";
import { CanvasLayer } from "./CanvasLayer";
import { GridMapHighlightLayer, RectHighlightRegion } from "./GridMapHighlightLayer";
import { GridMapMouseStateDefault } from "../states/GridMapMouseStates";

export class GridMapLayer extends CanvasLayer {

    public static readonly ZOOM_MIN = 0.6;
    public static readonly ZOOM_MAX = 2.0;

    public static readonly CELL_SIZE = 50;
    public static readonly COLORS = {
        background: '#f0f0f0',
        borderLine: '#555555',
        wallLine: '#0f0f0f',
        wallShadow: '#808080',
        gridBackground: '#fdfdfd',
        gridLine: '#999999'
    } // TODO: Move colors elsewhere

    private mapWidth = 0;
    private mapHeight = 0;

    public initialize(): void {
        this.registerSignal('updateMapData', this.updateMapData);
    }

    public render(): void {
        const ctx = this.getContext();
        if (!ctx ) return;

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

    public getMapSize(): { width: number; height: number } {
        return { width: this.mapWidth, height: this.mapHeight };
    }

    public updateMapData(width: number, height: number): void {
        this.mapWidth = width;
        this.mapHeight = height;

        this.canvasRender();
    }

    public getCellAtScreenPos(x: number, y: number): { x: number; y: number } | null {
        const cellX = Math.floor((x - this.canvasPanZoom.x) / this.canvasPanZoom.zoom / GridMapLayer.CELL_SIZE);
        const cellY = Math.floor((y - this.canvasPanZoom.y) / this.canvasPanZoom.zoom / GridMapLayer.CELL_SIZE);
        if (cellX < 0 || cellX >= this.mapWidth || cellY < 0 || cellY >= this.mapHeight) {
            return null;
        }
        return { x: cellX, y: cellY };
    }
}