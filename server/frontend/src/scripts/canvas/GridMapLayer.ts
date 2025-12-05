import { ref } from "vue";
import { CanvasLayer } from "./CanvasLayer";
import { GridMapHighlightLayer, RectHighlightRegion } from "./GridMapHighlightLayer";

export class GridMapLayer extends CanvasLayer {

    private static readonly ZOOM_MIN = 0.6;
    private static readonly ZOOM_MAX = 2.0;

    private static readonly CELL_SIZE = 50;
    private static readonly COLORS = {
        background: '#f0f0f0',
        borderLine: '#555555',
        wallLine: '#0f0f0f',
        wallShadow: '#808080',
        gridBackground: '#fdfdfd',
        gridLine: '#999999'
    }

    private mapWidth = 7;
    private mapHeight = 5;

    private selectedCell = { x: -1, y: -1 };

    public initialize(): void {
        this.registerSignal('updateMapData', this.updateMapData);
    }

    public prerender(): void {
        if (this.selectedCell.x >= 0 && this.selectedCell.y >= 0 && this.selectedCell.x < this.mapWidth && this.selectedCell.y < this.mapHeight) {
            this.emitSignal(GridMapHighlightLayer.SIGNAL_HIGHLIGHT_REGION, new RectHighlightRegion(
                this.selectedCell.x * GridMapLayer.CELL_SIZE,
                this.selectedCell.y * GridMapLayer.CELL_SIZE,
                GridMapHighlightLayer.COLOR_DARK,
                GridMapHighlightLayer.COLOR_LIGHT,
                GridMapLayer.CELL_SIZE,
                GridMapLayer.CELL_SIZE
            ));
            this.getCanvas()?.style.setProperty('cursor', 'pointer');
        }
        else {
            this.getCanvas()?.style.setProperty('cursor', 'default');
        }
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

    public updateMapData(mapData: object): void {
        this.mapWidth = mapData['width'];
        this.mapHeight = mapData['height'];

        this.canvasRender();
    }

    public onMouseMove(event: MouseEvent): void {
        this.selectedCell.x = Math.floor((event.clientX - this.canvasPanZoom.x) / this.canvasPanZoom.zoom / GridMapLayer.CELL_SIZE);
        this.selectedCell.y = Math.floor((event.clientY - this.canvasPanZoom.y) / this.canvasPanZoom.zoom / GridMapLayer.CELL_SIZE);
    }

    public onMouseWheel(event: WheelEvent): void {
        const rect = this.getCanvas()?.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const oldWorldX = (mouseX - this.canvasPanZoom.x) / this.canvasPanZoom.zoom;
        const oldWorldY = (mouseY - this.canvasPanZoom.y) / this.canvasPanZoom.zoom;

        const oldZoomLevel = this.canvasPanZoom.zoom;
        let newZoomLevel = oldZoomLevel;

        if (event.deltaY < 0) {
            // Zoom In
            if (oldZoomLevel >= GridMapLayer.ZOOM_MAX) return;
            newZoomLevel *= 1.2;
        }
        else if (event.deltaY > 0) {
            // Zoom Out
            if (oldZoomLevel <= GridMapLayer.ZOOM_MIN) return;
            newZoomLevel *= 0.8;
        }

        newZoomLevel = Math.max(GridMapLayer.ZOOM_MIN, Math.min(GridMapLayer.ZOOM_MAX, newZoomLevel));
        if (Math.abs(1.0 - newZoomLevel) < 0.05) { newZoomLevel = 1.0; }

        if (newZoomLevel === oldZoomLevel) return;

        this.canvasPanZoom.zoom = newZoomLevel;

        this.canvasPanZoom.x = mouseX - oldWorldX * this.canvasPanZoom.zoom;
        this.canvasPanZoom.y = mouseY - oldWorldY * this.canvasPanZoom.zoom;
    }
}