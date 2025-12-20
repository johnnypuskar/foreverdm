import { reactive } from "vue";
import { CanvasLayer } from "./CanvasLayer";

export class GridMapTokenLayer extends CanvasLayer {

    public static readonly SIGNAL_DISPLAY_TOKEN = "displayToken";
    public tokens: Record<string, DisplayToken> = reactive({});

    public render(): void {
        const ctx = this.getContext();
        if (!ctx ) return;

        for (const token of Object.values(this.tokens)) {
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 3;
            ctx.fillStyle = token.color;
            ctx.beginPath();
            ctx.arc(token.x, token.y, token.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        }
    }

    public addDisplayToken(name: string, token: DisplayToken): void {
        this.tokens[name] = token;
    }

    public removeDisplayToken(name: string): void {
        delete this.tokens[name];
    }
}

export class DisplayToken {
    public x: number;
    public y: number;
    public radius: number;
    public color: string;

    constructor(x: number, y: number, radius: number, color: string) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
    }
}