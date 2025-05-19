import { ref, Ref } from 'vue'
import { MouseState, MouseStateReturn } from '@/composables/state/mouseState'
import { DefaultState } from './defaultState';
import { ScreenRenderable, MapToken } from '../gridRenderable';

export class MoveState extends MouseState {
    static id = 'MOUSESTATE_MOVE';

    static indicatorDark = 'rgba(0, 0, 0, 0.5)';
    static indicatorLight = 'rgba(0, 0, 0, 0.2)';

    render: Function;
    cellSize: number;
    panOffset: { x: number, y: number };
    convertMousePosToCellPos: Function;
    pickedScreenRenderable: Ref<ScreenRenderable | null>
    screenRenderables: Ref<Array<ScreenRenderable>>;
    tokens: Ref<Array<MapToken>>;
    highlightCircleRegions: Ref<Record<string, { x: number, y: number, size: number, border: string, fill: string }>>;
    originalCellPosition: { x: number, y: number };

    constructor(canvasRef: Ref<HTMLCanvasElement> | null, render: Function, cellSize: number, panOffset: { x: number, y: number }, convertMousePosToCellPos: Function,
                tokens: Ref<Array<MapToken>>, screenRenderables: Ref<Array<ScreenRenderable>>,
                highlightCircleRegions: Ref<Record<string, { x: number, y: number, size: number, border: string, fill: string }>>) {
        super(canvasRef);
        this.render = render;
        this.cellSize = cellSize;
        this.panOffset = panOffset;
        this.convertMousePosToCellPos = convertMousePosToCellPos;
        this.tokens = tokens;
        this.highlightCircleRegions = highlightCircleRegions;
        this.pickedScreenRenderable = ref<ScreenRenderable | null>(null);
        this.screenRenderables = screenRenderables;
    }

    updateDetails(details: {}): void {
        this.originalCellPosition = details['originalCellPosition'];
        this.pickedScreenRenderable.value = details['pickedScreenRenderable'];
        console.log(details['pickedScreenRenderable']);
        this.highlightCircleRegions.value["tokenMovementIndicator"] = {
            x: this.originalCellPosition.x,
            y: this.originalCellPosition.y,
            size: 0.9,
            border: MoveState.indicatorDark,
            fill: MoveState.indicatorLight
        };
    }

    handleMouseMove(event: MouseEvent): MouseStateReturn {
        const { x: cellX, y: cellY, inbounds: inbounds } = this.convertMousePosToCellPos(event.clientX, event.clientY);
        if (!Boolean(event.buttons & 1)) {
            return this.handleLeftMouseUp(event);
        }
        this.pickedScreenRenderable.value.x = event.clientX;
        this.pickedScreenRenderable.value.y = event.clientY;

        console.log(this.pickedScreenRenderable.value.x, this.pickedScreenRenderable.value.y);

        this.highlightCircleRegions.value["tokenMovementIndicator"].x = cellX;
        this.highlightCircleRegions.value["tokenMovementIndicator"].y = cellY;
        
        return { "state": MoveState.id, "details": {} };
    }

    handleLeftMouseUp(event: MouseEvent): MouseStateReturn {
        const { x: cellX, y: cellY, inbounds: inbounds } = this.convertMousePosToCellPos(event.clientX, event.clientY);
        this.canvasRef.value.style.cursor = 'default';
        if (!inbounds) {
            this.pickedScreenRenderable.value.renderable.x = this.originalCellPosition.x;
            this.pickedScreenRenderable.value.renderable.y = this.originalCellPosition.y;
        }
        else {
            this.pickedScreenRenderable.value.renderable.x = cellX;
            this.pickedScreenRenderable.value.renderable.y = cellY;
        }
        delete this.screenRenderables.value[this.screenRenderables.value.indexOf(this.pickedScreenRenderable.value)];
        delete this.highlightCircleRegions.value["tokenMovementIndicator"];
        this.tokens.value.push(this.pickedScreenRenderable.value.renderable as MapToken);
        return { "state": DefaultState.id, "details": {} };
    }
}