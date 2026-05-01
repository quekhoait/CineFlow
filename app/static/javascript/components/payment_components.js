import { loadHTML, showError } from "../utils/load.js";
import { initBookingFlow } from "./booking_components.js";
import { getUser } from "./base.js";
import { showAlert } from "../utils/alert.js";
import fetchAPI from "../utils/apiClient.js";

export function switchStep(activeStepId) {
    const steps = ["step-seat-selection", "step-payment", "step-ticket"];
    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (id === activeStepId) el.classList.remove("hidden");
            else el.classList.add("hidden");
        }
    });
}

export async function getBookingByCode() {
    try {
        const code_booking = sessionStorage.getItem("code") ?? window.history.state?.code;
        if (!code_booking) return null;

        const res = await fetchAPI(`/api/bookings/${code_booking}`, { method: 'GET' });

        if (res.ok) {
            return res.data?.data || res.data;
        }
        return null;
    } catch (error) {
        console.error("Lỗi getBookingByCode:", error);
        showAlert("error", "Lỗi kết nối", "Không thể kết nối đến CineFlow");
        return null;
    }
}

export async function loadBookingPayment(booking) {
    try {
        const { body } = await loadHTML("/templates/components/card_booking_film.html");

        const html = body.innerHTML
            .replace(/{{code}}/g, booking.code || '')
            .replace(/{{poster}}/g, booking.poster || '')
            .replace(/{{title}}/g, booking.film_title || '')
            .replace(/{{room}}/g, booking.room_name || '')
            .replace(/{{time}}/g, booking.start_time || '')
            .replace(/{{seats}}/g, booking.seats ? booking.seats.map(s => s.name).join(", ") : '')
            .replace(/{{price}}/g, `${(parseInt(booking.total_price) || 0).toLocaleString("vi-VN")} VND`);

        const container = document.getElementById("info_film");
        if (container) {
            container.innerHTML = html;
            const btnNext = container.querySelector("#btn_next_payment");
            const btnPayment = container.querySelector("#btn_payment");

            if (btnNext) btnNext.style.display = "none";
            if (btnPayment) btnPayment.classList.remove("hidden");
        }
    } catch (e) {
        console.error("Lỗi khi tải thông tin đặt vé:", e);
    }
}

export async function renderInvoice(bookingData = null) {
    const booking = bookingData || await getBookingByCode();
    const container = document.getElementById("invoice_items");

    if (!container || !booking) return;

    const groupedSeats = {
        SINGLE: { label: "Ghế đơn", count: 0, names: [], totalPrice: 0 },
        COUPLE: { label: "Ghế đôi", count: 0, names: [], totalPrice: 0 }
    };

    booking.seats.forEach((item) => {
        const group = groupedSeats[item.type];
        if (group) {
            group.count++;
            group.names.push(item.name);
            group.totalPrice += parseInt(item.price) || 0;
        }
    });

    container.innerHTML = Object.values(groupedSeats)
        .filter(group => group.count > 0)
        .map(group => `
            <tr class="border-b border-gray-50 last:border-0">
                <td class="py-4 pl-10 text-gray-800">
                    <span class="font-bold">${group.label}</span>
                    <span class="text-sm text-gray-500 ml-1">(${group.names.join(", ")})</span>
                </td>
                <td class="py-4 text-center font-medium">${group.count}</td>
                <td class="py-4 pr-10 text-right font-bold text-gray-500">${group.totalPrice.toLocaleString("vi-VN")} VND</td>
            </tr>
        `).join("");

    const totalEl = document.getElementById("final_total");
    if (totalEl) totalEl.innerText = `${(booking.total_price || 0).toLocaleString("vi-VN")} VND`;

    await loadBookingPayment(booking);
}

export async function getInfoUser() {
    const formUser = document.getElementById("info_user");
    if (!formUser) return;

    const result = await getUser();
    if (!result?.data) {
        formUser.innerHTML = "<p class='text-red-500'>Không thể tải thông tin người dùng.</p>";
        return;
    }

    const user = result.data.data || result.data;
    const { full_name, phone_number, email } = user;

    formUser.innerHTML = `
        <div class="flex justify-between items-center w-full mb-2">
            <p><span class="text-gray-500">Họ và tên:</span> <span class="font-semibold ml-2 text-gray-800">${full_name || "N/A"}</span></p>
            <p><span class="text-gray-500">Số điện thoại:</span> <span class="font-semibold ml-2 text-gray-800">${phone_number || "N/A"}</span></p>
        </div>
        <p><span class="text-gray-500">Email:</span> <span class="font-semibold ml-2 text-gray-800">${email || "N/A"}</span></p>
    `;
}

export async function handleStartPayment(code) {
    if (!code) return showAlert("error", "Lỗi", "Không tìm thấy mã đặt vé");

    try {
        const res = await fetchAPI("/api/payments/create", {
            method: "POST",
            body: JSON.stringify({ method: "momo", booking_code: code }),
        });

        if (res.ok && res.data?.status === "success") {
            window.location.href = res.data.data.payUrl;
        } else {
            showError("Payment create: ", res.data);
        }
    } catch (error) {
        console.error("Payment Error:", error);
        showAlert("error", "Lỗi kết nối", "Không thể kết nối đến máy chủ thanh toán");
    }
}

export async function checkMomoReturn() {
    const urlParams = new URLSearchParams(window.location.search);
    const resultCode = urlParams.get('resultCode');
    const orderId = urlParams.get('orderId');

    if (resultCode === null || !orderId) return;

    try {
        const res = await fetchAPI(`/api/payments/momo/transaction`, {
            method: 'POST',
            body: JSON.stringify({ orderId: orderId })
        });

        if (res.ok && res.data?.status === "success") {
            const bookingCode = urlParams.get('extraData');
            if (bookingCode) {
                sessionStorage.setItem("code", bookingCode);
            }
            showAlert("success", "Thanh toán", "Thanh toán thành công!");

            const url = new URL(window.location.href);
            url.search = '';
            window.history.replaceState({}, document.title, url.toString());

        } else {
            const errorMsg = res.data?.message || "Giao dịch không thành công!";
            showAlert("error", "Thanh toán", errorMsg);
        }
    } catch (error) {
        console.error("Lỗi xác thực thanh toán:", error);
        showAlert("error", "Lỗi", "Không thể kết nối với máy chủ để xác nhận thanh toán!");
    } finally {
        initBookingFlow();
    }
}