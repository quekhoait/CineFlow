import {loadHTML} from "../utils/load.js";
import {authEmail} from "../api/user_api.js";

export function translateMode() {
    const tabs = document.querySelectorAll('.tab-auth')
    const container = document.getElementById('form-auth')
    const title = document.getElementById('title-auth')
    let regisHTML = ''
    let loginHTML = ''
    loadHTML("/templates/components/user/tab-regis.html").then(doc => regisHTML = doc.body.innerHTML)
    loadHTML("/templates/components/user/tab-login.html").then(doc => loginHTML = doc.body.innerHTML)

    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const mode = e.currentTarget.id;
            if (mode === 'login') {
                title.innerText = "Chào mừng quay trở lại"
                container.innerHTML = loginHTML
                loginHTML.getElementById('submit-login').addEventListener('click', async() => {
                   await authEmail()
                })
            } else {
                title.innerText = "Tạo tài khoảng mới"
                container.innerHTML = regisHTML
            }
            tabs.forEach(t => {
                const isActive = t === e.currentTarget
                t.classList.toggle('text-blue-600', isActive);
                t.classList.toggle('border-blue-600', isActive);

                t.classList.toggle('text-gray-400', !isActive);
                t.classList.toggle('border-transparent', !isActive);
            })
        })
    })
}

export function appearAuth() {
    const form = document.getElementById('auth')
    const openButton = document.getElementById('master-card')
    const closeButton = document.getElementById('close-auth')

    openButton.addEventListener('click', () => {
        form.classList.remove('hidden')
    })

    closeButton.addEventListener('click', () => {
        form.classList.add('hidden')
    })

    form.addEventListener('click', (e) => {
        (e.target === form) && form.classList.add('hidden')
    })
}

export async function authEmail() {
    const form = document.getElementById('form-auth');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    await fetch('/api/user/auth/email', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(async res => {
        if (res.status === 20) {
            let result = await res.json()
            if (result.access_token) {
                localStorage.setItem('accessToken', result.data.access_token);
                localStorage.setItem('refreshToken', result.data.refresh_token);
                localStorage.setItem('isLoggedIn', 'true');

                showAlert("success", result.message, `Chào mừng ${result.data.user.full_name}!`);


            } else {
                let errorDetail = "";
                if (result.data && typeof result.data === 'object') {
                    const allErrors = Object.values(data.data);
                    errorDetail = allErrors.join("<br>");
                } else {
                    errorDetail = result.message;
                }
                showAlert("error",result.message , errorDetail);
            }
        }
    }).catch (error => {
        console.error("Auth Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
    })
}
