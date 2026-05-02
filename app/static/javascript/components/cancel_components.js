import { renderInvoice, getBookingByCode, getInfoUser } from "./payment_components.js";
import { showAlert } from "../utils/alert.js";
import { showError } from "../utils/load.js";
import fetchAPI from "../utils/apiClient.js";

function parseBookingDate(dateString) {
    if (!dateString) return new Date();
    if (dateString.includes("T")) return new Date(dateString);
    let normalized = dateString.replace('h', ':').replace("'", "");
    const parts = normalized.split(" ");
    if (parts.length === 2) {
        if (parts[1].includes("/")) {
            const [hours, minutes] = parts[0].split(":");
            const [day, month, year] = parts[1].split("/");
            return new Date(year, month - 1, day, hours, minutes);
        }
        if (parts[0].includes("-")) {
            const [year, month, day] = parts[0].split("-");
            const [timePart] = parts[1].split(".");
            const [hours, minutes, seconds] = timePart.split(":");
            return new Date(year, month - 1, day, hours, minutes, seconds || 0);
        }
    }
    return new Date(normalized);
}

export async function initFlowCancel() {
    const code = sessionStorage.getItem('code') ?? window.history.state?.code;
    const action = sessionStorage.getItem('action'); // 'cancel' hoặc 'refund'

    if (!code) {
        showAlert("error", "Lỗi", "Không tìm thấy thông tin vé.");
        setTimeout(() => window.location.href = '/history', 1500);
        return;
    }
    window.history.replaceState({ code: code }, "");

    const bookingData = await getBookingByCode();
    if (!bookingData) {
        showAlert("error", "Lỗi", "Không tải được thông tin vé.");
        return;
    }

    await renderInvoice(bookingData);
    await getInfoUser();

    const btnCancelDiv = document.getElementById("btn_cancel");
    const btnPaymentDiv = document.getElementById("btn_payment");
    const btnNext = document.getElementById("btn_next_payment");

    if (btnNext) btnNext.classList.add("hidden");
    if (btnPaymentDiv) btnPaymentDiv.classList.add("hidden");

    if (btnCancelDiv) {
        btnCancelDiv.classList.remove("hidden");
        const btn = btnCancelDiv.querySelector("button");

        if (btn) {
            const isRefund = (action === 'refund');
            btn.innerText = isRefund ? "Xác nhận hoàn tiền" : "Xác nhận hủy vé";

            // LOGIC QUAN TRỌNG: Chỉ chặn 2h đối với luồng HỦY VÉ
            if (!isRefund && bookingData.payment_status === "PAID") {
                const now = new Date();
                const startTime = parseBookingDate(bookingData.start_time);
                const hoursUntilStart = (startTime - now) / (1000 * 60 * 60);

                let cancelHour = 2;
                const res = await fetchAPI('/api/rules', { method: 'GET' }).catch(() => null);
                if (res?.ok) {
                    const rule = res.data.data.find(r => r.name === 'CANCEL_HOUR');
                    if (rule) cancelHour = parseInt(rule.value);
                }

                if (hoursUntilStart <= cancelHour) {
                    btn.disabled = true;
                    btn.innerText = "Đã hết hạn hủy vé";
                    btn.style.backgroundColor = "#9ca3af";
                    btn.classList.add("cursor-not-allowed");
                } else {
                    btn.disabled = false;
                    btn.style.backgroundColor = "#A50064";
                    btn.classList.remove("cursor-not-allowed");
                }
            } else {
                // Nếu là luồng HOÀN TIỀN thì luôn cho phép bấm (Không bị chặn bởi thời gian)
                btn.disabled = false;
                btn.style.backgroundColor = "#A50064";
                btn.classList.remove("cursor-not-allowed");
            }
        }
    }

    const titleBill = document.getElementById('title-bill');
    if (titleBill) titleBill.innerText = (action === 'refund') ? "Hỗ trợ hoàn tiền" : "Xác nhận hủy vé";
}

export async function cancelTicket(code) {
    if (!code) return showAlert('error', 'Lỗi', 'Không có mã vé.');

    const action = sessionStorage.getItem('action');
    const isRefund = (action === 'refund');

    // Phân luồng API chính xác theo yêu cầu
    const endpoint = isRefund ? `/api/payments/refund` : `/api/bookings/${code}/cancel`;
    const bodyData = isRefund
        ? { "method": "momo", "booking_code": code }
        : { "method": "momo" };

    try {
        const res = await fetchAPI(endpoint, {
             method: "POST",
             body: JSON.stringify(bodyData)
        });

        if (res.ok) {
            const msg = isRefund ? 'Gửi yêu cầu hoàn tiền thành công!' : 'Hủy vé thành công!';
            showAlert('success', 'Thành công', msg);
            sessionStorage.removeItem('code');
            sessionStorage.removeItem('action');
            setTimeout(() => window.location.href = '/history', 2000);
        } else {
            showError('Thao tác thất bại', res);
        }
    } catch (error) {
        showAlert('error', 'Lỗi kết nối', 'Vui lòng thử lại sau.');
    }
}