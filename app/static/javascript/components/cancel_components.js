import { renderInvoice, getBookingByCode, getInfoUser } from "./payment_components.js";
import { showAlert } from "../utils/alert.js";
import { showError } from "../utils/load.js";
import fetchAPI from "../utils/apiClient.js";

export async function initFlowCancel() {
    const code = sessionStorage.getItem('code') ?? window.history.state?.code;

    if (!code) {
        showAlert("error", "Lỗi", "Không tìm thấy thông tin vé cần hủy.");
        setTimeout(() => window.location.href = '/history', 1500);
        return;
    }
    window.history.replaceState({ code: code }, "");

    const bookingData = await getBookingByCode();

    if (bookingData) {
        await renderInvoice(bookingData);
        await getInfoUser();
        const container = document.getElementById("info_film");
        if (container) {
            const btnPayment = container.querySelector("#btn_payment");
            const btnCancel = container.querySelector("#btn_cancel");
            if (btnPayment) btnPayment.style.display = "none";
            if (btnCancel) btnCancel.classList.remove("hidden");
        }

        const titleBill = document.getElementById('title-bill');
        if (titleBill) titleBill.innerText = "Số tiền hoàn trả";

        if (bookingData.payment_status === 'PENDING') {
            const totalPrice = document.getElementById('total_price');
            if (totalPrice) totalPrice.innerText = '0 VND';
        }
    } else {
        showAlert("error", "Lỗi", "Không tải được thông tin vé.");
    }
}

export async function cancelTicket(code) {
    if (!code) {
        return showAlert('error', 'Lỗi', 'Không có mã vé để hủy.');
    }

    try {
        const res = await fetchAPI(`/api/bookings/${code}/cancel`, {
             method: "POST",
             body: JSON.stringify({"method":"momo"})
        });

        if (res.ok) {
            showAlert('success', 'Hủy vé', 'Hủy vé thành công, bạn chờ hoàn tiền nhé!');
            sessionStorage.removeItem('code');

            setTimeout(() => {
                window.location.href = '/history';
            }, 2000);
        } else {
            showError('Cancel ticket', res);
        }
    } catch (error) {
        console.error("Lỗi khi hủy vé:", error);
        showAlert('error', 'Lỗi mạng', 'Không thể kết nối đến máy chủ.');
    }
}