export async function loadHTML(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error("LOAD PAGE ERROR!!!");
    const parser = new DOMParser();
    return parser.parseFromString(await response.text(), 'text/html')
}