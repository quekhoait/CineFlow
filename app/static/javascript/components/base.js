import {showAlert} from "../utils/alert.js";

export async function getUser() {
    try {
        const res = await fetch('/api/user/profile', {
            method: 'GET',
            credentials: 'include',
        });
        const result = await res.json();
        if (res.status === 200) {
            return result;
        }
    } catch (error) {
        console.error("Profile Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
}

export async function getCinema() {
    try {
        const res = await fetch('/api/cinemas', {
            method: 'GET',
            credentials: 'include',
            headers: {'Content-Type': 'application/json'}
        });
        const result = await res.json();
        if (res.status === 200) {
            return result;
        }
    } catch (error) {
        console.error("Profile Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
}

