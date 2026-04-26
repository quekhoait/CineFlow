document.addEventListener('DOMContentLoaded', () => {
    if (window.opener && !window.opener.closed) {
            window.opener.postMessage({ type: 'GOOGLE_AUTH_SUCCESS' }, window.location.origin);
            window.close();
        } else {
            document.body.innerHTML = "<h3>Lỗi: Cửa sổ chính đã bị đóng!</h3>";
        }
})