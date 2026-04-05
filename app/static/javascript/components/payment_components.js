import {loadHTML} from "../utils/load.js";
import updateNav from "./booking_components.js";
import {getUser} from "./base.js";
import {showAlert} from "../utils/alert.js";
import {renderTicket} from "./ticket_component.js";

export async function getBookingByCode() {
    try {
        const code_booking = sessionStorage.getItem("code");
        const res = await fetch(`/api/bookings/${code_booking}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
        });

        if (res.status === 200) {
            const result = await res.json();
            console.log(result.data)
            return result.data;
        }
        return null;
    } catch (error) {
        console.error("Profile Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
}

export async function loadBookingPayment(booking) {
    try {
        const stringSeats = booking.seats.map((item) => item.name).join(", ");
        const templateResponse = await loadHTML(
            "/templates/components/card_booking_film.html",
        );
        const template = templateResponse.body.innerHTML;
        let html = template
            .replace("{{poster}}", booking.poster)
            .replace("{{title}}", booking.film_title)
            .replace("{{room}}", booking.room_name)
            .replace("{{time}}", booking.start_time)
            .replace("{{seats}}", stringSeats)
            .replace("{{price}}", `${(parseInt(booking.total_price) || 0).toLocaleString("vi-VN")} VND`);
        const container = document.getElementById("info_film");

        if (container) {
            container.innerHTML = html;
            const btnNext = container.querySelector("#btn_next_payment");
            const btnPayment = container.querySelector("#btn_payment");
            if (btnNext && btnPayment) {
                btnNext.style.display = "none";
                btnPayment.classList.remove("hidden");
            }
        }
    } catch (e) {
        console.error("Lỗi khi tải thông tin đặt vé:", e);
    }
}

let final_total_price;

export async function renderInvoice() {
    const booking = await getBookingByCode();
    const container = document.getElementById("invoice_items");
    if (!container) return;
    const groupedSeats = {
        SINGLE: {label: "Ghế đơn", count: 0, names: [], totalPrice: 0},
        COUPLE: {label: "Ghế đôi", count: 0, names: [], totalPrice: 0}
    };

    booking.seats.forEach((item) => {
        const seatPrice = parseInt(item.price) || 0;

        if (item.type === "SINGLE") {
            groupedSeats.SINGLE.count++;
            groupedSeats.SINGLE.names.push(item.name);
            groupedSeats.SINGLE.totalPrice += seatPrice;
        } else if (item.type === "COUPLE") {
            groupedSeats.COUPLE.count++;
            groupedSeats.COUPLE.names.push(item.name);
            groupedSeats.COUPLE.totalPrice += seatPrice;
        }
    });

    let itemsHtml = "";
    Object.values(groupedSeats).forEach(group => {
        if (group.count > 0) {
            const seatList = group.names.join(", ");

            itemsHtml += `
                <tr class="border-b border-gray-50 last:border-0">
                    <td class="py-4 pl-10 text-gray-800">
                        <span class="font-bold">${group.label}</span>
                        <span class="text-sm text-gray-500 ml-1">(${seatList})</span>
                    </td>
                    <td class="py-4 text-center font-medium">${group.count}</td>
                    <td class="py-4 pr-10 text-right font-bold text-gray-500">${group.totalPrice.toLocaleString("vi-VN")} VND</td>
                </tr>
            `;
        }
    });
    container.innerHTML = itemsHtml;
    final_total_price = booking.total_price;
    document.getElementById("final_total").innerText =
        `${final_total_price.toLocaleString("vi-VN")} VND`;

    await loadBookingPayment(booking)
}

export async function getInfoUser() {
    const formUser = document.getElementById("info_user");
    if (!formUser) return;
    const result = await getUser();
    if (!result || !result.data) {
        formUser.innerHTML =
            "<p class='text-red-500'>Không thể tải thông tin người dùng.</p>";
        return;
    }
    const user = result.data;
    const template = `
        <p>
            <div class="flex justify-between items-center w-full mb-2">
                <p><span class="text-gray-500">Họ và tên:</span> <span class="font-semibold ml-2 text-gray-800">${user.full_name || "N/A"}</span></p>
                <p><span class="text-gray-500">Số điện thoại:</span> <span class="font-semibold ml-2 text-gray-800">${user.phone_number || "N/A"}</span></p>
            </div>
        </p>
   
        <p><span class="text-gray-500">Email:</span> <span class="font-semibold ml-2 text-gray-800">${user.email || "N/A"}</span></p>
    `;

    formUser.innerHTML = template;
}

export async function handleStartPayment() {
    const code_booking = sessionStorage.getItem("code");
    try {
        const res = await fetch("/api/payments/create", {
            method: "POST",
            body: JSON.stringify({
                method: "momo",
                booking_code: code_booking,
            }),
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
        });
        const result = await res.json();
        if (result.status === "success") {
            const seatSection = document.getElementById("step-seat-selection");
            const paymentSection = document.getElementById("step-payment");
            const ticketSection = document.getElementById("step-ticket");

            if (paymentSection && ticketSection) {
                seatSection.classList.add("hidden");
                paymentSection.classList.add("hidden");
                ticketSection.classList.remove("hidden");
            }
            // updateNav(2);
            // renderTicket();
            window.location.href = result.data.payUrl;
        }
    } catch (error) {
        console.error("Profile Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
}

export async function checkMomoReturn() {
    const urlParams = new URLSearchParams(window.location.search);
    const resultCode = urlParams.get('resultCode')

    if (resultCode === null) return;
    if (resultCode === '0') {
        const bookingCode = urlParams.get('extraData');
        if(bookingCode) {
            sessionStorage.setItem("code", bookingCode);
        }

        const seatSection = document.getElementById("step-seat-selection");
        const paymentSection = document.getElementById("step-payment");
        const ticketSection = document.getElementById("step-ticket");

        if (seatSection && paymentSection && ticketSection) {
            seatSection.classList.add("hidden");
            paymentSection.classList.add("hidden");
            ticketSection.classList.remove("hidden");
        }

        updateNav(2);
        await renderTicket();
        showAlert("success", "Payment", "Payment successful");
        // window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        showAlert("error", "Payment", "Payment failed!");

        const seatSection = document.getElementById("step-seat-selection");
        const paymentSection = document.getElementById("step-payment");
        const ticketSection = document.getElementById("step-ticket");

        if (seatSection && paymentSection && ticketSection) {
            seatSection.classList.add("hidden");
            ticketSection.classList.add("hidden");
            paymentSection.classList.remove("hidden");
        }

        updateNav(1);
    }
}