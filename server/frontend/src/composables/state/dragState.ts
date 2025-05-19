import { Ref } from 'vue'
import { MouseState, MouseStateReturn } from '@/composables/state/mouseState'
import { DefaultState } from '@/composables/state/defaultState'

export class DragState extends MouseState {
    static id = 'MOUSESTATE_DRAG';
    panOffset: { x: number, y: number };
    panStart: { x: number, y: number };

    constructor(canvasRef: Ref<HTMLCanvasElement> | null, panOffset: { x: number, y: number }) {
        super(canvasRef);
        this.panOffset = panOffset;
    }   

    updateDetails(details: {}): void {
        this.panStart = details['panStart'];
        this.panStart.x -= this.panOffset.x;
        this.panStart.y -= this.panOffset.y;
    }

    handleMouseMove(event: MouseEvent): MouseStateReturn {
        if (!Boolean(event.buttons & 4)) {
            this.canvasRef.value.style.cursor = 'default';
            return {"state": DefaultState.id, "details": {}};
        }
        this.panOffset.x = event.clientX - this.panStart.x;
        this.panOffset.y = event.clientY - this.panStart.y;

        return {"state": DragState.id, "details": {}};
    }

    handleMiddleMouseUp(event: MouseEvent): MouseStateReturn {
        this.canvasRef.value.style.cursor = 'default';
        return {"state": DefaultState.id, "details": {}};
    }
}