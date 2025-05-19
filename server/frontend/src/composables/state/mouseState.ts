import { Ref } from 'vue';

export interface MouseStateReturn {
    state: string;
    details: {};
}

export class MouseState {
    static id: string;
    canvasRef: Ref<HTMLCanvasElement> | null;

    constructor(canvasRef: Ref<HTMLCanvasElement> | null) {
        this.canvasRef = canvasRef;
    }

    updateDetails(details: {}): void { }

    handleMouseDown(event: MouseEvent): MouseStateReturn {
        switch (event.button) {
            case 0:
                return this.handleLeftMouseDown(event);
            case 1:
                return this.handleMiddleMouseDown(event);
            case 2:
                return this.handleRightMouseDown(event);
        }
        return { state: (this.constructor as typeof MouseState).id, details: {} };
    }
    handleLeftMouseDown(event: MouseEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }
    handleMiddleMouseDown(event: MouseEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }
    handleRightMouseDown(event: MouseEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }

    handleMouseUp(event: MouseEvent): MouseStateReturn {
        switch (event.button) {
            case 0:
                return this.handleLeftMouseUp(event);
            case 1:
                return this.handleMiddleMouseUp(event);
            case 2:
                return this.handleRightMouseUp(event);
        }
        return { state: (this.constructor as typeof MouseState).id, details: {} };
    }
    handleLeftMouseUp(event: MouseEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }
    handleMiddleMouseUp(event: MouseEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }
    handleRightMouseUp(event: MouseEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }

    handleKeyDown(event: KeyboardEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }
    handleMouseMove(event: MouseEvent): MouseStateReturn { return { state: (this.constructor as typeof MouseState).id, details: {} }; }
}