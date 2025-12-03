export abstract class CanvasLayer {
    protected ctx: CanvasRenderingContext2D | null = null;
    protected canvas: HTMLCanvasElement | null = null;
    
    public zIndex: number;

    constructor(zIndex: number) {
        this.zIndex = zIndex;
    }

    public initialize(ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement) {
        this.ctx = ctx;
        this.canvas = canvas;
    }

    public abstract render(): void;
}