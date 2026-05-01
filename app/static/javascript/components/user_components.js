import { loadHTML, showError } from "../utils/load.js";
import { showAlert } from "../utils/alert.js";
import { getUser } from "./base.js";
import fetchAPI from "../utils/apiClient.js";

export async function setupAuthMode(mod = "") {
    const tabs = document.querySelectorAll('.tab-auth');
    const container = document.getElementById('form-auth');
    const title = document.getElementById('title-auth');

    let regisDoc = await loadHTML("/templates/components/user/tab-regis.html");
    let loginDoc = await loadHTML("/templates/components/user/tab-login.html");

    const regisHTML = regisDoc.body.innerHTML;
    const loginHTML = loginDoc.body.innerHTML;

    container.onclick = async (e) => {
        const submitBtn = e.target.closest('#submit-login');
        const eyeIcon = e.target.closest('.fa-eye, .fa-eye-slash');
        const sendOTPBtn = e.target.closest('#otp-btn');
        const regisBtn = e.target.closest('#regis-btn');
        const googleBtn = e.target.closest('#btn-google');

        if (submitBtn) {
            e.preventDefault();
            await authEmail();
        }

        if (regisBtn) {
            e.preventDefault();
            await regisEmail();
        }

        if (eyeIcon) {
            const wrapper = eyeIcon.closest('.relative');
            if (wrapper) {
                const input = wrapper.querySelector('input');
                if (input) {
                    const isPassword = input.type === 'password';
                    input.type = isPassword ? 'text' : 'password';
                    eyeIcon.classList.toggle('fa-eye', !isPassword);
                    eyeIcon.classList.toggle('fa-eye-slash', isPassword);
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
            e.preventDefault();
            await authGoogle();
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
        tab.onclick = (e) => switchTab(e.currentTarget.id);
    });

    switchTab(mod === "" ? "login" : mod);
}

export function appearAuth() {
    const form = document.getElementById('auth');
    const openButton = document.getElementById('master-card');
    const closeButton = document.getElementById('close-auth');

    openButton.addEventListener('click', async () => {
        let isAuthenticate = await checkAuthenticate();
        if (!isAuthenticate) {
            await setupAuthMode();
            form.classList.remove('hidden');
        }
    });

    closeButton.addEventListener('click', () => {
        form.classList.add('hidden');
    });

    form.addEventListener('mousedown', (e) => {
        if (e.target === form) form.classList.add('hidden');
    });
}

async function checkAuthenticate() {
    const response = await fetchAPI('/api/user/auth/me', { method: 'GET' });
    return response.ok;
}

export async function updateMasterCard() {
    const navMasterCard = document.getElementById('master-card');
    if (!navMasterCard) return;

    let isAuthenticate = await checkAuthenticate();
    if (isAuthenticate) {
        const result = await getUser();
        let masterCard = await loadHTML("/templates/components/user/master_card.html");

        const avatarEl = masterCard.getElementById('master-avatar');
        const nameEl = masterCard.getElementById('master-name');
        const usernameEl = masterCard.getElementById('mater-username');

        if (avatarEl && result?.data?.avatar) avatarEl.src = result.data.avatar;
        if (nameEl && result?.data?.full_name) nameEl.innerText = result.data.full_name;
        if (usernameEl && result?.data?.username) usernameEl.innerText = result.data.username;

        navMasterCard.innerHTML = masterCard.body.innerHTML;

        const logoutBtn = document.getElementById('logout');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                await logOutAccount();
            });
        }
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
    const auth_form = document.getElementById('auth');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const response = await fetchAPI('/api/user/auth/email', {
        method: 'POST',
        body: JSON.stringify(data)
    });

    if (response.ok && response.data?.status === "success") {
        await updateMasterCard();
        auth_form.classList.add('hidden');
        showAlert("success", "Login Email", response.data.message || `Welcome to CineFlow`);
    } else {
        showError("Authenticate email", response.data || { message: "Lỗi đăng nhập" });
    }
}

async function sendOTP() {
    const container = document.getElementById('form-auth');
    const emailInput = container.querySelector('input[name="email"]');

    if (emailInput) {
        const response = await fetchAPI('/api/user/send-otp', {
            method: "POST",
            body: JSON.stringify({ "email": emailInput.value.trim() })
        });

        if (response.ok) {
            showAlert("success", "Send OTP", response.data?.message || "Đã gửi OTP");
        } else {
            showError("Send OTP", response.data || { message: "Lỗi gửi OTP" });
        }
    }
}

async function regisEmail() {
    const form = document.getElementById('form-auth');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    if (data['re-password'] !== data.password) {
        showAlert("error", "Invalid Input", "Password and re-password not match");
        return;
    }

    const response = await fetchAPI('/api/user/register', {
        method: "POST",
        body: JSON.stringify(data)
    });

    if (response.status === 201 || response.ok) {
        const loginTab = document.getElementById('login');
        if (loginTab) loginTab.click();
        showAlert("success", "Register account", response.data?.message || "Đăng ký thành công");
    } else {
        showError("Register account", response.data || { message: "Lỗi đăng ký" });
    }
}

async function logOutAccount() {
    const response = await fetchAPI("/api/user/logout", { method: 'GET' });

    if (response.ok && response.data?.status === 'success') {
        await updateMasterCard();
        window.location.reload(true);
        showAlert("success", "Logout", "See you later!!");
    } else {
        showError("Logout", response.data || { message: "Lỗi đăng xuất" });
    }
}

async function authGoogle() {
    const popup = window.open('', 'Google Login', 'width=500,height=600,left=200,top=100');

    if (!popup) {
        showAlert("error", "Login google: ", "Trình duyệt đã chặn Popup. Vui lòng cấp quyền!");
        return;
    }

    popup.document.write('<h3 style="font-family: sans-serif; text-align: center; margin-top: 50px;">Đang khởi tạo kết nối...</h3>');
    const response = await fetchAPI('/api/user/auth/google', { method: 'GET' });

    if (response.ok && response.data?.data?.url) {
        popup.location.href = response.data.data.url;
        const handleStorageChange = (event) => {
            if (event.key === 'GOOGLE_AUTH_SUCCESS') {
                updateMasterCard();
                const authForm = document.getElementById('auth');
                if (authForm) authForm.classList.add('hidden');
                showAlert("success", "Google Login", "Welcome to CineFlow");

                localStorage.removeItem('GOOGLE_AUTH_SUCCESS');
                window.removeEventListener('storage', handleStorageChange);
            }
            else if (event.key === 'GOOGLE_AUTH_ERROR') {
                showAlert("error", "Lỗi", "Đăng nhập Google thất bại!");
                localStorage.removeItem('GOOGLE_AUTH_ERROR');
                window.removeEventListener('storage', handleStorageChange);
            }
        };

        window.addEventListener('storage', handleStorageChange);

    } else {
        popup.close();
        showAlert("error", "Lỗi mạng", "Không kết nối được với máy chủ");
    }
}