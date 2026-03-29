let currentMode = 'login';

function switchMode(mode) {
    currentMode = mode;
    const title = document.getElementById('form-title');
    const submitBtn = document.getElementById('submit-btn');
    const confirmGroup = document.getElementById('confirm-pass-group');
    const tabLogin = document.getElementById('tab-login');
    const tabRegis = document.getElementById('tab-regis');
     const googleLogin = document.getElementById('google-login');
    if (mode === 'login') {
        title.innerText = "Chào mừng quay trở lại!";
        submitBtn.innerText = "Đăng nhập";
        confirmGroup.classList.add('hidden');
        googleLogin.classList.remove('hidden');
        tabLogin.className = "pb-3 px-4 text-blue-600 font-semibold border-b-2 border-blue-600";
        tabRegis.className = "pb-3 px-4 text-gray-400 font-semibold border-b-2 border-transparent";
    } else {
        title.innerText = "Tạo tài khoản mới";
        submitBtn.innerText = "Đăng ký ngay";
        confirmGroup.classList.remove('hidden');
        googleLogin.classList.add('hidden');
        tabRegis.className = "pb-3 px-4 text-blue-600 font-semibold border-b-2 border-blue-600";
        tabLogin.className = "pb-3 px-4 text-gray-400 font-semibold border-b-2 border-transparent";
    }
}

//document.getElementById('auth-form').addEventListener('submit', async function(e) {
//    e.preventDefault();
//    const formData = new FormData(this);
//    const data = Object.fromEntries(formData.entries());
//
//    // Xác định URL dựa trên mode hiện tại
//    const url = currentMode === 'login' ? '/auth/login' : '/auth/register';
//
//    const response = await fetch(url, {
//        method: 'POST',
//        headers: { 'Content-Type': 'application/json' },
//        body: JSON.stringify(data)
//    });
//
//    const result = await response.json();
//    alert(result.message);
//});