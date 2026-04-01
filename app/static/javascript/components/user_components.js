import {loadHTML} from "../utils/load.js";

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

