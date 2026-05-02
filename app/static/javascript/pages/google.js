document.addEventListener('DOMContentLoaded', () => {
    localStorage.setItem('GOOGLE_AUTH_SUCCESS', Date.now().toString());
    document.body.innerHTML = `
        <div style="text-align: center; margin-top: 50px; font-family: sans-serif;">
            <h3 style="color: #4CAF50;">Đăng nhập thành công!</h3>
            <p>Đang chuyển hướng...</p>
        </div>
    `;
    setTimeout(() => {
        window.close();
    }, 500);
})