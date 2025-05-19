export class GridRenderable extends EventTarget {
    x: number;
    y: number;
    _clickedEvent: MouseEvent | null;

    clickDown(event: MouseEvent) { this.dispatchEvent(new CustomEvent("clickDown", {detail: {renderable: this}})); }
    clickUp(event: MouseEvent) { this.dispatchEvent(new CustomEvent("clickUp", {detail: {renderable: this}})); }
    click(event: MouseEvent) { this.dispatchEvent(new CustomEvent("click", {detail: {renderable: this}})); }
    draw(context: CanvasRenderingContext2D, cellSize: number) { }
    drawAtCoords(context: CanvasRenderingContext2D, x: number, y: number, cellSize: number) { }
}

export class MapToken extends GridRenderable {
    x: number;
    y: number;
    color: string;
    size: number;

    constructor(x: number, y: number, color: string, size: number) {
        super();
        this.x = x;
        this.y = y;
        this.color = color;
        this.size = size;
    }

    clickDown(event: MouseEvent) {
        super.clickDown(event);
    }

    clickUp(event: MouseEvent) {
        super.clickUp(event);
    }

    draw(context: CanvasRenderingContext2D, cellSize: number) {
        return this.drawAtCoords(context, this.x * cellSize, this.y * cellSize, cellSize);
    }

    drawAtCoords(context: CanvasRenderingContext2D, x: number, y: number, cellSize: number) {
        context.save();

        context.fillStyle = this.color;
        context.strokeStyle = "#000000";
        context.lineWidth = 2;
        context.beginPath();
        context.arc(x + this.size * cellSize / 2.0, y + this.size * cellSize / 2.0, this.size * cellSize / 2.0 - 2, 0, Math.PI * 2);
        context.fill();
        context.stroke();
        context.closePath();

        context.restore();
    }
}