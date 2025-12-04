import { CanvasLayer } from "./CanvasLayer";

export class GridMapHighlightLayer extends CanvasLayer {

    public initialize(): void {
        this.registerSignal('click', this.signalText);
    }

    public render(): void {
        const ctx = this.getContext();
        const canvas = this.getCanvas();
        if (!ctx || !canvas) return;

        ctx.fillStyle = 'blue';
        ctx.fillRect(0, 0, 120, 30);
    }

    public signalText(message: string, x: number, y: number): void {
        console.log('GridMapHighlightLayer received signal:', message, x, y);
    }
}