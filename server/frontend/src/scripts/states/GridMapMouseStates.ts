import RenderCanvas, { RenderCanvasData } from "@/components/canvas/RenderCanvas.vue";
import { GridMapComponents } from "@/components/GridMap.vue";

export abstract class GridMapMouseState {
    public mousePosition: { x: number; y: number } = { x: -1, y: -1 };
    protected gridMap: GridMapComponents;

    constructor(gridMap: GridMapComponents) {
        this.gridMap = gridMap;
    }

    public onMouseMove(event: MouseEvent): void {
        this.mousePosition.x = event.clientX;
        this.mousePosition.y = event.clientY;
    }

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
        super.onMouseMove(event);

        // Updates selected cell when mouse is moved
        const selectedCell = this.gridMap.gridMapLayer.getCellAtScreenPos(event.clientX, event.clientY);

        if (selectedCell && selectedCell.x >= 0 && selectedCell.x < this.gridMap.gridMapLayer.getMapSize().width && 
                selectedCell.y >= 0 && selectedCell.y < this.gridMap.gridMapLayer.getMapSize().height) {
            this.gridMap.renderCanvas.getCanvas().style.cursor = 'pointer';
        }
        else {
            this.gridMap.renderCanvas.getCanvas().style.cursor = 'default';
        }
    }

    public onMouseWheel(event: WheelEvent): void {
        // TODO: See if this can be optimized any better
        const rect = this.gridMap.renderCanvas.getCanvas().getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const oldWorldX = (mouseX - this.gridMap.renderCanvas.panZoomLevels.x) / this.gridMap.renderCanvas.panZoomLevels.zoom;
        const oldWorldY = (mouseY - this.gridMap.renderCanvas.panZoomLevels.y) / this.gridMap.renderCanvas.panZoomLevels.zoom;

        const oldZoomLevel = this.gridMap.renderCanvas.panZoomLevels.zoom;
        let newZoomLevel = oldZoomLevel;

        const ZOOM_MAX = 2.0;
        const ZOOM_MIN = 0.6;

        if (event.deltaY < 0) {
            // Zoom In
            if (oldZoomLevel >= ZOOM_MAX) return;
            newZoomLevel *= 1.2;
        }
        else if (event.deltaY > 0) {
            // Zoom Out
            if (oldZoomLevel <= ZOOM_MIN) return;
            newZoomLevel *= 0.8;
        }

        newZoomLevel = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, newZoomLevel));
        if (Math.abs(1.0 - newZoomLevel) < 0.05) { newZoomLevel = 1.0; }

        if (newZoomLevel === oldZoomLevel) return;

        this.gridMap.renderCanvas.panZoomLevels.zoom = newZoomLevel;

        this.gridMap.renderCanvas.panZoomLevels.x = mouseX - oldWorldX * this.gridMap.renderCanvas.panZoomLevels.zoom;
        this.gridMap.renderCanvas.panZoomLevels.y = mouseY - oldWorldY * this.gridMap.renderCanvas.panZoomLevels.zoom;
    }

    public onMiddleMouseDown(event: MouseEvent): void {
        this.gridMap.renderCanvas.getCanvas().style.cursor = 'grabbing';
        this.gridMap.setMouseState(new GridMapMouseStateDragging(this.gridMap));
    }
}

export class GridMapMouseStateDragging extends GridMapMouseState {
    public onMouseMove(event: MouseEvent): void {
        super.onMouseMove(event);

        if (!Boolean(event.buttons & 4)) { // Middle mouse button is no longer held
            this.exitDrag(event);
        }
        else {
            this.gridMap.renderCanvas.panZoomLevels.x += event.movementX;
            this.gridMap.renderCanvas.panZoomLevels.y += event.movementY;
        }

    }
    
    public onMiddleMouseUp(event: MouseEvent): void {
        this.exitDrag(event);
    }

    private exitDrag(event: MouseEvent): void {
        this.gridMap.renderCanvas.getCanvas().style.cursor = 'default';
        const defaultMouseState = new GridMapMouseStateDefault(this.gridMap);
        this.gridMap.setMouseState(defaultMouseState);
        defaultMouseState.onMouseMove(event);
    }
}