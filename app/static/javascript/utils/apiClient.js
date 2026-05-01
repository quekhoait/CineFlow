import { getCookie } from "./load.js";
import { showAlert } from "./alert.js";

async function fetchAPI(endpoint, options = {}) {
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    if (options.method && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(options.method.toUpperCase())) {
        defaultHeaders['X-CSRF-TOKEN'] = getCookie('csrf_access_token');
    }

    const config = {
        credentials: 'include',
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(endpoint, config);
        const data = await response.json().catch(() => null);

        return {
            ok: response.ok,
            status: response.status,
            data: data? data: undefined,
        };
    } catch (error) {
        console.error(`API Error at ${endpoint}:`, error);
        showAlert("error", "Lỗi kết nối", "Không thể kết nối đến máy chủ CineFlow.");
        return { ok: false, status: 500, data: null };
    }
}

export default fetchAPI;