export function makePlayCommand(
    command: string,
    args: Array<string | number> = []
) {
    return {
        command: command,
        args: args
    };
}