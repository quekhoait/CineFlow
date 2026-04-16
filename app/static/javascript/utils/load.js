import {showAlert} from "./alert.js";

export async function loadHTML(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error("LOAD PAGE ERROR!!!");
    const parser = new DOMParser();
    return parser.parseFromString(await response.text(), 'text/html')
}

export function showError(title, result) {
    let errorDetail = "";
    if (result.data && typeof result.data === 'object') {
        const allErrors = Object.values(result.data);
        errorDetail = allErrors.join("<br>");
    } else {
        errorDetail = result.message
    }
    showAlert("error",title , errorDetail);
}

export function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) {
        return match[2];
    }
    return null;
}