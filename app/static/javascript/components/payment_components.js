import { loadHTML } from "../utils/load.js";
import updateNav, {initBookingFlow} from "./booking_components.js";
import { getUser } from "./base.js";
import { showAlert } from "../utils/alert.js";
import { renderTicket } from "./ticket_component.js";

export function switchStep(activeStepId) {
    const steps = ["step-seat-selection", "step-payment", "step-ticket"];
    steps.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (id === activeStepId) el.classList.remove("hidden");
            else el.classList.add("hidden");
        }
    });
    if(activeStepId !== 1) sessionStorage.removeItem('code')
    if(activeStepId !== 0) sessionStorage.removeItem('')
}

export async function getBookingByCode() {
    try {
        const code_booking = sessionStorage.getItem("code");
        if (!code_booking) return null;

        const res = await fetch(`/api/bookings/${code_booking}`, {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
        });

        if (res.ok) {
            const result = await res.json();
            console.log(result.data)
            return result.data;
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
            .replace(/{{code}}/g, booking.code)
            .replace("{{poster}}", booking.poster)
            .replace("{{title}}", booking.film_title)
            .replace("{{room}}", booking.room_name)
            .replace("{{time}}", booking.start_time)
            .replace("{{seats}}", booking.seats.map(s => s.name).join(", "))
            .replace("{{price}}", `${(parseInt(booking.total_price) || 0).toLocaleString("vi-VN")} VND`);

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

    const { full_name, phone_number, email } = result.data;

    formUser.innerHTML = `
        <div class="flex justify-between items-center w-full mb-2">
            <p><span class="text-gray-500">Họ và tên:</span> <span class="font-semibold ml-2 text-gray-800">${full_name || "N/A"}</span></p>
            <p><span class="text-gray-500">Số điện thoại:</span> <span class="font-semibold ml-2 text-gray-800">${phone_number || "N/A"}</span></p>
        </div>
        <p><span class="text-gray-500">Email:</span> <span class="font-semibold ml-2 text-gray-800">${email || "N/A"}</span></p>
    `;
}

export async function handleStartPayment(code) {
    const code_booking = code
    if (!code_booking) return showAlert("error", "Lỗi", "Không tìm thấy mã đặt vé");

    try {
        const res = await fetch("/api/payments/create", {
            method: "POST",
            body: JSON.stringify({ method: "momo", booking_code: code_booking }),
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
        });

        const result = await res.json();
        if (result.status === "success") {
            window.location.href = result.data.payUrl;
        } else {
            showAlert("error", "Lỗi tạo thanh toán", result.message || "Vui lòng thử lại");
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
        const response = await fetch(`/api/payments/momo/transaction`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                 Authorization: `Bearer ${localStorage.getItem("accessToken")}`,

            },
            body: JSON.stringify({ orderId: orderId })
        });

        const resData = await response.json();
        if (response.ok && resData.status === "success") {
            const bookingCode = urlParams.get('extraData');
            if (bookingCode) {
                sessionStorage.setItem("code", bookingCode);
            }
            showAlert("success", "Thanh toán", "Thanh toán thành công!");
            initBookingFlow();
        } else {
            const errorMsg = resData.message || "Giao dịch không thành công!";
            showAlert("error", "Thanh toán", errorMsg);
            initBookingFlow();
        }

    } catch (error) {
        console.error("Lỗi xác thực thanh toán:", error);
        showAlert("error", "Lỗi", "Không thể kết nối với máy chủ để xác nhận thanh toán!");
    }
}