import {loadHTML, showError} from "../utils/load.js";
import {showAlert} from "../utils/alert.js";
import {getUser} from "./base.js";

export async function setupAuthMode(mod = "") {
    const tabs = document.querySelectorAll('.tab-auth')
    const container = document.getElementById('form-auth')
    const title = document.getElementById('title-auth')
    let regisDoc = await loadHTML("/templates/components/user/tab-regis.html")
    let loginDoc = await loadHTML("/templates/components/user/tab-login.html")

    const regisHTML = regisDoc.body.innerHTML;
    const loginHTML = loginDoc.body.innerHTML;

    container.onclick = async (e) => {
        const submitBtn = e.target.closest('#submit-login');
        const eyeIcon = e.target.closest('.fa-eye, .fa-eye-slash');
        const sendOTPBtn = e.target.closest('#otp-btn');
        const regisBtn = e.target.closest('#regis-btn');
        const googleBtn = e.target.closest('#btn-google')

        if (submitBtn) {
            e.preventDefault();
            await authEmail();
        }

        if (regisBtn) {
            e.preventDefault();
            await regisEmail();
        }

        if (eyeIcon) {
            const container = eyeIcon.closest('.relative');
            if (container) {
                const input = container.querySelector('input');
                if (input) {
                    const isPassword = input.type === 'password';
                    input.type = isPassword ? 'text' : 'password';

                    if (isPassword) {
                        eyeIcon.classList.remove('fa-eye');
                        eyeIcon.classList.add('fa-eye-slash');
                    } else {
                        eyeIcon.classList.remove('fa-eye-slash');
                        eyeIcon.classList.add('fa-eye');
                    }
                }
            }
        }

        if (sendOTPBtn) {
            e.preventDefault();
            const originalContent = sendOTPBtn.innerHTML;
            sendOTPBtn.disabled = true;
            sendOTPBtn.classList.add('opacity-70', 'cursor-not-allowed');
            sendOTPBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i> Đang gửi`;

            try {
                await sendOTP();
            } finally {
                sendOTPBtn.disabled = false;
                sendOTPBtn.classList.remove('opacity-70', 'cursor-not-allowed');
                sendOTPBtn.innerHTML = originalContent;
            }
        }

        if (googleBtn) {
            e.preventDefault()
            await authGoogle()
        }
    };

    const switchTab = (mode) => {
        if (mode === 'regis') {
            title.innerText = "Tạo tài khoản mới";
            container.innerHTML = regisHTML;
        } else {
            title.innerText = "Chào mừng quay trở lại";
            container.innerHTML = loginHTML;
        }

        tabs.forEach(t => {
            const isActive = t.id === mode;
            t.classList.toggle('text-blue-600', isActive);
            t.classList.toggle('border-blue-600', isActive);
            t.classList.toggle('text-gray-400', !isActive);
            t.classList.toggle('border-transparent', !isActive);
        });
    };

    tabs.forEach(tab => {
        tab.onclick = (e) => {
            switchTab(e.currentTarget.id);
        };
    });

    switchTab(mod === "" ? "login" : mod)
}

export function appearAuth() {
    const form = document.getElementById('auth')
    const openButton = document.getElementById('master-card')
    const closeButton = document.getElementById('close-auth')

    openButton.addEventListener('click', async () => {
        let isAuthenticate = await checkAuthenticate()
        if (!isAuthenticate) {
            await setupAuthMode()
            form.classList.remove('hidden')
        }
    })

    closeButton.addEventListener('click', () => {
        form.classList.add('hidden')
    })

    form.addEventListener('mousedown', (e) => {
        (e.target === form) && form.classList.add('hidden');
    });
}

function checkAuthenticate() {
    return fetch('/api/user/auth/me', {
        method: 'GET',
        credentials: 'include',
    }).then(res => {
        if (res.status === 200) {
            return true
        } else if (res.status === 400) {
            return false
        }
    }).catch(error => {
        return false
    })
}

export async function updateMasterCard() {
    const navMasterCard = document.getElementById('master-card')
    if (!navMasterCard) return;
    let isAuthenticate = await checkAuthenticate()
    if (isAuthenticate) {
        const result = await getUser()
        let masterCard = await loadHTML("/templates/components/user/master_card.html")
        const avatarEl = masterCard.getElementById('master-avatar');
        const nameEl = masterCard.getElementById('master-name');
        const usernameEl = masterCard.getElementById('mater-username')

        if (avatarEl && result.data.avatar) {
            avatarEl.src = result.data.avatar;
        }
        if (nameEl && result.data.full_name) {
            nameEl.innerText = result.data.full_name;
        }
        if (usernameEl && result.data.username) {
            usernameEl.innerText = result.data.username;
        }
        navMasterCard.innerHTML = masterCard.body.innerHTML
        const logoutBtn = document.getElementById('logout')
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault()
            await logOutAccount()
        })

    } else {
        navMasterCard.innerHTML = `
            <div class="flex nav-item justify-center items-center space-x-2 px-2 py-1.5 bg-gray-100 rounded-xl cursor-pointer hover:bg-gray-200 hover:text-black text-gray-400 transition-colors min-w-[140px]">
                <img src="/static/image/icon_user.png" alt="User" class="w-8 h-8 rounded-full object-cover border-2 border-white flex-shrink-0">
                <div class="text-sm font-medium whitespace-nowrap relative top-[4px]" style="font-family: 'Ponnala', sans-serif;">Đăng nhập</div>
            </div>
        `;
    }
}

async function authEmail() {
    const form = document.getElementById('form-auth');
    const auth_form = document.getElementById('auth')
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    return fetch('/api/user/auth/email', {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify(data)
    }).then(async res => {
        let result = await res.json()
        if (result.status === "success") {
            await updateMasterCard()
            auth_form.classList.add('hidden')
            showAlert("success", result.message, `Wellcome my page`);

        } else {
            showError("Authenticate email", result)
        }
    }).catch(error => {
        console.error("Auth Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
    })
}

async function sendOTP() {
    const container = document.getElementById('form-auth')
    const emailInput = container.querySelector('input[name="email"]')
    if (emailInput) {
        return fetch('/api/user/send-otp', {
            method: "POST",
            credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({"email": emailInput.value.trim()})
        }).then(async res => {
            const result = await res.json()
            if (res.status === 200) {
                showAlert("success", "Send OTP", result.message)
            } else {
                showError("Send OTP", result)
            }
        }).catch(error => {
            showAlert("error", "Error Connection", "Error Connection to CineFlow");
        })
    }
}

async function regisEmail() {
    const form = document.getElementById('form-auth');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (data['re-password'] !== data.password) {
        showAlert("error", "Invalid Input", "Password and re-password not match")
        return;
    }

    return fetch('api/user/register', {
        method: "POST",
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(async res => {
        let result = await res.json()
        if (res.status === 201) {
            const loginTab = document.getElementById('login');
            if (loginTab) {
                loginTab.click();
            }
            showAlert("success", "Register account", result.message)
        } else {
            showError("Register account", result)
        }
    }).catch(error => {
        showAlert("error", "Register account", "Internal Internet Error")
    })
}

async function logOutAccount() {
    fetch("/api/user/logout", {
        method: 'GET',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
    }).then(res => res.json())
        .then(async (result) => {
            if (result.status === 'success') {
                await updateMasterCard();
                window.location.reload(true);
                showAlert("success", "Logout", "See you later!!");
            } else {
                showError("Logout", result)
            }
        }).catch(error => {
        console.error(error)
        showAlert('error', 'Logout', 'Server Error')
    })
}

async function authGoogle() {
    const popup = window.open('', 'Google Login', 'width=500,height=600,left=200,top=100');

    if (!popup) {
        showAlert("error", "Lỗi", "Trình duyệt đã chặn Popup. Vui lòng cấp quyền!");
        return;
    }

    popup.document.write('<h3 style="font-family: sans-serif; text-align: center; margin-top: 50px;">Đang khởi tạo kết nối...</h3>');

    try {
        const res = await fetch('/api/user/auth/google', {method: 'GET'});
        const result = await res.json();

        if (res.status === 200 && result.data && result.data.url) {
            popup.location.href = result.data.url;

            const handleMessage = (event) => {
                if (event.origin !== window.location.origin) return;

                const data = event.data;

                if (data.type === 'GOOGLE_AUTH_SUCCESS') {
                    updateMasterCard();
                    const authForm = document.getElementById('auth');
                    if (authForm) authForm.classList.add('hidden');
                    showAlert("success", "Google Login", "Welcome to CineFlow");
                } else if (data.type === 'GOOGLE_AUTH_ERROR') {
                    showAlert("error", "Lỗi", "Đăng nhập Google thất bại!");
                }

                clearInterval(checkPopupClosed);
            };

            window.addEventListener('message', handleMessage, {once: true});

            const checkPopupClosed = setInterval(() => {
                try {
                    if (popup.closed) {
                        clearInterval(checkPopupClosed);
                        window.removeEventListener('message', handleMessage);
                    }
                } catch (e) {
                }
            }, 1000);

        } else {
            throw new Error("Không lấy được URL chuyển hướng");
        }
    } catch (error) {
        console.error("Google Auth Error:", error);
        if (popup && !popup.closed) {
            popup.close();
        }
        showAlert("error", "Lỗi mạng", "Không kết nối được với máy chủ");
    }
}
