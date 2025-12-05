import { GridMapLayer } from "../canvas/GridMapLayer";

export abstract class GridMapMouseState {
    protected gridMapLayer: GridMapLayer;

    constructor(gridMapLayer: GridMapLayer) {
        this.gridMapLayer = gridMapLayer;
    }

    public onMouseMove(event: MouseEvent): void { }

    public onMouseWheel(event: WheelEvent): void { }

    public onMouseDown(event: MouseEvent): void {
        const MOUSE_DOWN_FUNCS = [this.onLeftMouseDown, this.onMiddleMouseDown, this.onRightMouseDown];
        const func = MOUSE_DOWN_FUNCS[event.button];
        if (func) { func.call(this, event); }
    }

    public onLeftMouseDown(event: MouseEvent): void { }

    public onRightMouseDown(event: MouseEvent): void { }

    public onMiddleMouseDown(event: MouseEvent): void { }

    public onMouseUp(event: MouseEvent): void {
        const MOUSE_UP_FUNCS = [this.onLeftMouseUp, this.onMiddleMouseUp, this.onRightMouseUp];
        const func = MOUSE_UP_FUNCS[event.button];
        if (func) { func.call(this, event); }
    }

    public onLeftMouseUp(event: MouseEvent): void { }

    public onRightMouseUp(event: MouseEvent): void { }

    public onMiddleMouseUp(event: MouseEvent): void { }

    public onKeyDown(event: KeyboardEvent): void { }
}

export class GridMapMouseStateDefault extends GridMapMouseState {
    public onMouseMove(event: MouseEvent): void {
        // Updates selected cell when mouse is moved
        this.gridMapLayer.selectedCell.x = Math.floor((event.clientX - this.gridMapLayer.canvasPanZoom.x) / this.gridMapLayer.canvasPanZoom.zoom / GridMapLayer.CELL_SIZE);
        this.gridMapLayer.selectedCell.y = Math.floor((event.clientY - this.gridMapLayer.canvasPanZoom.y) / this.gridMapLayer.canvasPanZoom.zoom / GridMapLayer.CELL_SIZE);

        if (this.gridMapLayer.selectedCell.x >= 0 && this.gridMapLayer.selectedCell.x < this.gridMapLayer.getMapSize().width && 
                this.gridMapLayer.selectedCell.y >= 0 && this.gridMapLayer.selectedCell.y < this.gridMapLayer.getMapSize().height) {
            this.gridMapLayer.getCanvas().style.cursor = 'pointer';
        }
        else {
            this.gridMapLayer.getCanvas().style.cursor = 'default';
        }
    }

    public onMouseWheel(event: WheelEvent): void {
        // TODO: See if this can be optimized any better
        const rect = this.gridMapLayer.getCanvas().getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const oldWorldX = (mouseX - this.gridMapLayer.canvasPanZoom.x) / this.gridMapLayer.canvasPanZoom.zoom;
        const oldWorldY = (mouseY - this.gridMapLayer.canvasPanZoom.y) / this.gridMapLayer.canvasPanZoom.zoom;

        const oldZoomLevel = this.gridMapLayer.canvasPanZoom.zoom;
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

        this.gridMapLayer.canvasPanZoom.zoom = newZoomLevel;

        this.gridMapLayer.canvasPanZoom.x = mouseX - oldWorldX * this.gridMapLayer.canvasPanZoom.zoom;
        this.gridMapLayer.canvasPanZoom.y = mouseY - oldWorldY * this.gridMapLayer.canvasPanZoom.zoom;
    }

    public onMiddleMouseDown(event: MouseEvent): void {
        this.gridMapLayer.selectedCell = { x: -1, y: -1 };
        this.gridMapLayer.getCanvas().style.cursor = 'grabbing';
        this.gridMapLayer.mouseState = new GridMapMouseStateDragging(this.gridMapLayer);
    }
}

export class GridMapMouseStateDragging extends GridMapMouseState {
    public onMouseMove(event: MouseEvent): void {
        if (!Boolean(event.buttons & 4)) { // Middle mouse button is no longer held
            this.exitDrag();
        }
        else {
            this.gridMapLayer.canvasPanZoom.x += event.movementX;
            this.gridMapLayer.canvasPanZoom.y += event.movementY;
        }

    }
    
    public onMiddleMouseUp(event: MouseEvent): void {
        this.exitDrag();
        this.gridMapLayer.onMouseMove(event);
    }

    private exitDrag(): void {
        this.gridMapLayer.getCanvas().style.cursor = 'default';
        this.gridMapLayer.mouseState = new GridMapMouseStateDefault(this.gridMapLayer);
    }
}