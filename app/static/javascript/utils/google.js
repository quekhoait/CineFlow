document.addEventListener("DOMContentLoaded", () => {
    const bodyData = document.querySelector('body').dataset;
    const status = bodyData.status;

    if (window.opener) {
        if (status === 'success') {
            window.opener.postMessage({
                type: 'GOOGLE_AUTH_SUCCESS',
                access_token: bodyData.accessToken,
                refresh_token: bodyData.refreshToken
            }, "*");
        } else {
            window.opener.postMessage({
                type: 'GOOGLE_AUTH_ERROR'
            }, "*");
        }
    }

    window.close();
});