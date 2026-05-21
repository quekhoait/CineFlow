import {showAlert} from "./alert.js";

export async function loadHTML(path) {
    const response = await fetch(path);
    if (!response.ok) throw new Error("LOAD PAGE ERROR!!!");
    const parser = new DOMParser();
    return parser.parseFromString(await response.text(), 'text/html')
}

export function showError(title, result) {
    const payload = result?.data;
    let errorDetail = result?.message || "";

    if (payload && typeof payload === 'object') {
        const parts = [];
        if (typeof payload.message === 'string' && payload.message) {
            parts.push(payload.message);
        }

        if (payload.data) {
            const values = [];
            const pushValue = (value) => {
                if (Array.isArray(value)) {
                    value.forEach(pushValue);
                } else if (value !== null && value !== undefined && value !== '') {
                    values.push(String(value));
                }
            };

            if (typeof payload.data === 'object') {
                Object.values(payload.data).forEach(pushValue);
            } else {
                pushValue(payload.data);
            }

            if (values.length) {
                parts.push(values.join(' | '));
            }
        }

        if (parts.length) {
            errorDetail = parts.join(': ');
        }
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