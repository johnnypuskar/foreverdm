import { RenderCanvasData } from '@/components/canvas/RenderCanvas.vue';

export abstract class CanvasLayer {

    protected signals: Map<string, Function> = new Map();
    public getCanvas: () => HTMLCanvasElement | null;
    protected getContext: () => CanvasRenderingContext2D | null;
    protected canvasRender: () => void;
    
    public canvasPanZoom: { x: number; y: number; zoom: number };
    public zIndex: number;

    constructor(renderCanvas: RenderCanvasData, zIndex: number = 0) {
        this.getCanvas = renderCanvas.getCanvas;
        this.getContext = renderCanvas.getContext;
        this.canvasRender = renderCanvas.render;
        this.canvasPanZoom = renderCanvas.panZoomLevels;
        this.zIndex = zIndex;

        this.initialize();
    }

    public initialize(): void { }

    public abstract render(): void;
}