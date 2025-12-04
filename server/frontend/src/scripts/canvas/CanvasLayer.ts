import { RenderCanvas } from '@/components/canvas/RenderCanvas.vue';

export abstract class CanvasLayer {

    protected signals: Map<string, Function> = new Map();
    protected getCanvas: () => HTMLCanvasElement | null;
    protected getContext: () => CanvasRenderingContext2D | null;
    protected emitSignal: (signalName: string, ...args: any[]) => void;
    protected canvasRender: () => void;
    protected canvasPanZoom: { x: number; y: number; zoom: number };

    public zIndex: number;

    constructor(renderCanvas: RenderCanvas, zIndex: number = 0) {
        this.getCanvas = renderCanvas.getCanvas;
        this.getContext = renderCanvas.getContext;
        this.emitSignal = renderCanvas.emitSignal;
        this.canvasRender = renderCanvas.render;
        this.canvasPanZoom = renderCanvas.panZoomLevels;
        this.zIndex = zIndex;
        
        this.initialize();
    }

    public initialize(): void { }

    public prerender(): void { }

    public abstract render(): void;

    public registerSignal(signalName: string, handler: Function) {
        this.signals.set(signalName, handler);
    }

    public recieveSignal(signalName: string, ...args: any[]) {
        const signalHandler = this.signals.get(signalName);
        if (signalHandler) {
            signalHandler(...args);
        }
    }

    public onMouseClick(event: MouseEvent): void { }

    public onMouseUp(event: MouseEvent): void { }

    public onMouseDown(event: MouseEvent): void { }

    public onMouseMove(event: MouseEvent): void { }

    public onMouseWheel(event: WheelEvent): void { }

}