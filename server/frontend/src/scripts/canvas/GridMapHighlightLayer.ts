import { CanvasLayer } from "./CanvasLayer";

export class GridMapHighlightLayer extends CanvasLayer {

    public static readonly SIGNAL_HIGHLIGHT_REGION = "highlightRegion";
    public static readonly COLOR_DARK = 'rgba(105, 125, 245, 1.0)';
    public static readonly COLOR_LIGHT = 'rgba(0, 55, 255, 0.1)';

    private highlightQueue: Set<HighlightRegion> = new Set<HighlightRegion>();

    public initialize(): void {
        this.registerSignal(GridMapHighlightLayer.SIGNAL_HIGHLIGHT_REGION, this.addHighlightRegion);
    }

    public addHighlightRegion(region: HighlightRegion): void {
        this.highlightQueue.add(region);
    }

    public render(): void {
        const ctx = this.getContext();
        const canvas = this.getCanvas();
        if (!ctx || !canvas) return;

        for (const region of this.highlightQueue) {
            region.draw(ctx);
        }

        this.highlightQueue.clear();
    }
}



// Highlight Region Classes for defining areas to highlight
export abstract class HighlightRegion {
    x: number;
    y: number;
    stroke: string;
    fill: string;

    constructor(x: number, y: number, stroke: string, fill: string) {
        this.x = x;
        this.y = y;
        this.stroke = stroke;
        this.fill = fill;
    }

    public draw(ctx: CanvasRenderingContext2D): void {
        ctx.strokeStyle = this.stroke;
        ctx.fillStyle = this.fill;
    }
}

export class RectHighlightRegion extends HighlightRegion {
    width: number;
    height: number;

    constructor(x: number, y: number, stroke: string, fill: string, width: number, height: number) {
        super(x, y, stroke, fill);
        this.width = width;
        this.height = height;
    }

    public draw(ctx: CanvasRenderingContext2D): void {
        super.draw(ctx);
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.strokeRect(this.x, this.y, this.width, this.height);
    }
}

export class CircleHighlightRegion extends HighlightRegion {
    radius: number;

    constructor(x: number, y: number, stroke: string, fill: string, radius: number) {
        super(x, y, stroke, fill);
        this.radius = radius;
    }

    public draw(ctx: CanvasRenderingContext2D): void {
        super.draw(ctx);
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
    }
}