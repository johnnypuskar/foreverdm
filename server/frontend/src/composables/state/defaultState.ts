import { reactive, Ref } from 'vue'
import { MouseState, MouseStateReturn } from '@/composables/state/mouseState'
import { DragState } from '@/composables/state/dragState'
import { MoveState } from '@/composables/state/moveState'
import { ScreenRenderable, GridRenderable, MapToken } from '@/composables/gridRenderable'

export class DefaultState extends MouseState {
    static id = 'MOUSESTATE_DEFAULT';
    static highlightDark = 'rgba(105, 125, 245, 1.0)';
    static highlightLight = 'rgba(0, 55, 255, 0.1)';

    tokenClickable: Ref<Boolean>;
    propClickable: Ref<Boolean>;
    cellClickable: Ref<Boolean>;

    mouseCellPos: { x: number, y: number };
    convertMousePosToCellPos: Function;
    clickableItemOffset: number;

    tokens: Ref<Array<MapToken>>;
    screenRenderables: Ref<Array<ScreenRenderable>>;
    mousePickedRenderable: Ref<GridRenderable | null>;

    // TODO: Create the definitions for these regions in CombatGrid.vue and import them here
    highlightCellRegions: Ref<Record<string, { x: number; y: number, width: number, height: number, border: string, fill: string }>>;
    highlightCircleRegions: Ref<Record<string, {x: number, y: number, size: number, border: string, fill: string}>>;

    constructor(canvasRef: Ref<HTMLCanvasElement> | null, convertMousePosToCellPos: Function, mousePickedRenderable: Ref<GridRenderable | null>,
                screenRenderables: Ref<Array<ScreenRenderable>>, tokenClickable: Ref<Boolean>, propClickable: Ref<Boolean>, cellClickable: Ref<Boolean>,
                tokens: Ref<Array<MapToken>>, 
                highlightCellRegions: Ref<Record<string, { x: number; y: number, width: number, height: number, border: string, fill: string }>>,
                highlightCircleRegions: Ref<Record<string, { x: number, y: number, size: number, border: string, fill: string }>>) {
        super(canvasRef);

        this.tokenClickable = tokenClickable;
        this.propClickable = propClickable;
        this.cellClickable = cellClickable;

        this.convertMousePosToCellPos = convertMousePosToCellPos;
        this.tokens = tokens;

        this.screenRenderables = screenRenderables;
        this.mousePickedRenderable = mousePickedRenderable;
        this.highlightCellRegions = highlightCellRegions;
        this.highlightCircleRegions = highlightCircleRegions;

        this.mouseCellPos = reactive({ x: 0, y: 0 });
        this.clickableItemOffset = 0;
    }

    updateMouseCellPos(event) {
        const { x: cellX, y: cellY, inbounds: inbounds} = this.convertMousePosToCellPos(event.clientX, event.clientY);

        if (!this.mouseCellPos.x || !this.mouseCellPos.y || this.mouseCellPos.x != cellX || this.mouseCellPos.y != cellY) {
            this.clickableItemOffset = 0;
        }

        this.mouseCellPos.x = cellX;
        this.mouseCellPos.y = cellY;

        return inbounds;
    }

    processCursor(inbounds) {
        if (!inbounds) {
            if (this.highlightCellRegions.value.hasOwnProperty("mouseCellHighlight")) { delete this.highlightCellRegions.value["mouseCellHighlight"]; }
            if (this.highlightCircleRegions.value.hasOwnProperty("mouseTokenHighlight")) { delete this.highlightCircleRegions.value["mouseTokenHighlight"]; }
            this.canvasRef.value.style.cursor = 'default';
            return {"state": DefaultState.id, "details": {}};
        }

        const tokensOnCell = this.tokens.value.filter(token => token.x == this.mouseCellPos.x && token.y == this.mouseCellPos.y);
        if (this.tokenClickable.value && this.clickableItemOffset < tokensOnCell.length) {
            if (this.highlightCellRegions.value.hasOwnProperty("mouseCellHighlight")) { delete this.highlightCellRegions.value["mouseCellHighlight"]; }

            this.canvasRef.value.style.cursor = 'pointer';
            this.mousePickedRenderable.value = tokensOnCell[this.clickableItemOffset];

            this.highlightCircleRegions.value["mouseTokenHighlight"] = {
                x: this.mouseCellPos.x,
                y: this.mouseCellPos.y,
                size: 1,
                border: DefaultState.highlightDark,
                fill: DefaultState.highlightLight
            }
            return {"state": DefaultState.id, "details": {}};
        }
        else if (this.cellClickable.value) {
            if (this.highlightCircleRegions.value.hasOwnProperty("mouseTokenHighlight")) { delete this.highlightCircleRegions.value["mouseTokenHighlight"]; }

            this.mousePickedRenderable.value = null;

            this.highlightCellRegions.value["mouseCellHighlight"] = {
                x: this.mouseCellPos.x,
                y: this.mouseCellPos.y,
                width: 1,
                height: 1,
                border: DefaultState.highlightDark,
                fill: DefaultState.highlightLight
            }
        }

        this.canvasRef.value.style.cursor = 'default';
        return {"state": DefaultState.id, "details": {}};
    }

    handleMouseMove(event: MouseEvent): MouseStateReturn { 
        const inbounds = this.updateMouseCellPos(event);
        return this.processCursor(inbounds);
    }

    handleLeftMouseDown(event: MouseEvent): MouseStateReturn {
        this.updateMouseCellPos(event);
        if (this.mousePickedRenderable.value instanceof MapToken) {
            const { x: cellX, y: cellY, inbounds: inbounds} = this.convertMousePosToCellPos(event.clientX, event.clientY);
            this.canvasRef.value.style.cursor = 'grabbing';
            delete this.tokens.value[this.tokens.value.indexOf(this.mousePickedRenderable.value)];
            delete this.highlightCircleRegions.value["mouseTokenHighlight"];

            const tokenScreenRenderable = {
                    x: event.clientX,
                    y: event.clientY,
                    renderable: this.mousePickedRenderable.value
                }
            this.screenRenderables.value.push(
                tokenScreenRenderable
            )
            return {"state": MoveState.id, "details": {
                "originalCellPosition": { x: cellX, y: cellY },
                "pickedScreenRenderable": tokenScreenRenderable
            }};
        }
        return {"state": DefaultState.id, "details": {}};
    }

    handleMiddleMouseDown(event: MouseEvent) {
        if (this.highlightCellRegions.value.hasOwnProperty("mouseCellHighlight")) { delete this.highlightCellRegions.value["mouseCellHighlight"]; }
        if (this.highlightCircleRegions.value.hasOwnProperty("mouseTokenHighlight")) { delete this.highlightCircleRegions.value["mouseTokenHighlight"]; }
        this.canvasRef.value.style.cursor = 'grabbing';
        return {"state": DragState.id, "details": {
            "panStart": { x: event.clientX, y: event.clientY }
        }}
    }

    handleKeyDown(event: KeyboardEvent): MouseStateReturn {
        if (event.key == "r") {
            if (this.mousePickedRenderable.value == null) {
                this.clickableItemOffset = 0;
            }
            else {
                this.clickableItemOffset += 1;
            }
        }
        return this.processCursor(true);
    }

    handleRightMouseDown(event: MouseEvent): MouseStateReturn {
        const { x: cellX, y: cellY, inbounds: inbounds} = this.convertMousePosToCellPos(event.clientX, event.clientY);
        if (inbounds) {
            this.tokens.value.push(new MapToken(cellX, cellY, "#6666AA", 1));
        }
        return {"state": DefaultState.id, "details": {}};
    }
}