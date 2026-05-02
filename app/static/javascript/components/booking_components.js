import { getCookie, loadHTML, showError } from "../utils/load.js";
import { showAlert } from "../utils/alert.js";
import { getInfoUser, renderInvoice, getBookingByCode, switchStep } from "./payment_components.js";
import { renderTicket } from "./ticket_component.js";
import fetchAPI from "../utils/apiClient.js";

let selectedSeats = [];

export function handleSelectShow(id) {
    sessionStorage.removeItem("code");
    sessionStorage.setItem("selectedShowId", id);
    window.location.href = `/booking`;
}

function parseBookingDate(dateString) {
    if (!dateString) return new Date();
    if (dateString.includes("T")) return new Date(dateString);

    let normalizedDate = dateString.replace('h', ':').replace("'", "");

    const parts = normalizedDate.split(" ");
    if (parts.length === 2) {
        if (parts[1].includes("/")) {
            const [hours, minutes] = parts[0].split(":");
            const [day, month, year] = parts[1].split("/");
            return new Date(year, month - 1, day, hours, minutes);
        }
        if (parts[0].includes("-")) {
            const [year, month, day] = parts[0].split("-");
            const [hours, minutes, seconds] = parts[1].split(":");
            return new Date(year, month - 1, day, hours, minutes, seconds || 0);
        }
    }
    return new Date(normalizedDate);
}

async function fetchCancelHour() {
    try {
        const res = await fetchAPI('/api/rules', { method: 'GET' });
        if (res.ok && res.data?.status === "success") {
            const rules = res.data.data || [];
            const cancelRule = rules.find(r => r.name === 'CANCEL_HOUR');
            return cancelRule ? parseInt(cancelRule.value) : 2;
        }
    } catch (e) {}
    return 2;
}

export async function getShowSeat() {
    const id = sessionStorage.getItem('selectedShowId') ?? window.history.state?.selectedShowId;
    console.log(id)
    if (!id) {
        showAlert("error", "Lỗi", "Không tìm thấy thông tin suất chiếu.");
        return null;
    }

    window.history.replaceState({ selectedShowId: id }, "");
    sessionStorage.removeItem("selectedShowId");

    try {
        const res = await fetchAPI(`/api/shows/${id}`, { method: 'GET' });
        if (res.ok) {
            return res.data?.data || res.data;
        }

        showError('Get Seats', res.data || "Không thể tải dữ liệu ghế");
        return null;
    } catch (e) {
        showAlert("error", "Lỗi mạng", "Không thể kết nối đến máy chủ.");
        return null;
    }
}

export async function loadBooking(data) {
    try {
        if (!data) return;

        const { body } = await loadHTML("/templates/components/card_booking_film.html");
        let html = body.innerHTML
            .replace("{{poster}}", data.poster)
            .replace("{{title}}", data.film_title)
            .replace("{{room}}", data.room_name)
            .replace("{{time}}", data.start_time)
            .replace("{{seats}}", " ")
            .replace("{{price}}", (data.base_price || 0).toLocaleString("vi-VN"));

        const container = document.getElementById("booking_summary");
        if (container) container.innerHTML = html;
    } catch (e) {}
}

export async function loadSeat() {
    const data = await getShowSeat();
    const container = document.getElementById("seat_container");
    if (!container || !data?.seats) return;

    const seats = data.seats;
    const rows = seats.reduce((acc, seat) => {
        (acc[seat.row] = acc[seat.row] || []).push(seat);
        return acc;
    }, {});

    let finalHTML = `<div class="grid grid-cols-[24px_max-content] items-center gap-y-3 gap-x-4 mx-auto w-max">`;

    Object.entries(rows)
        .sort(([a], [b]) => a.localeCompare(b))
        .forEach(([label, seatsInRow]) => {
            let rowSeatsHTML = "";
            const maxColInRow = Math.max(...seatsInRow.map(s => parseInt(s.col || 0)));

            for (let col = 1; col <= maxColInRow; col++) {
                const seat = seatsInRow.find((s) => parseInt(s.col) === col);

                if (!seat) {
                    rowSeatsHTML += `<div class="w-10 h-8"></div>`;
                    continue;
                }

                const isCouple = seat.type === "COUPLE";
                const isBooked = seat.is_booked;
                const baseClass = isCouple ? "w-[88px]" : "w-10";

                const bgClass = isBooked
                    ? "bg-[#A1A3A6] cursor-not-allowed opacity-60"
                    : `${isCouple ? "bg-[#F8A4FF]" : "bg-white"} cursor-pointer hover:border-[#F1B400] hover:scale-105`;

                rowSeatsHTML += `
                    <div class="seat-item h-8 ${baseClass} ${bgClass} border border-gray-200 rounded-md flex items-center justify-center text-[10px] font-bold transition-all shadow-sm"
                         data-code="${seat.code}" data-booked="${isBooked}"
                         data-location="${seat.row}${seat.col}"
                         data-type="${seat.type}" data-price="${seat.price}">
                        ${seat.row}${seat.col}
                    </div>`;
            }

            finalHTML += `
                <span class="text-xs font-bold text-gray-500 text-right">${label}</span>
                <div class="flex gap-2 justify-start w-fit">${rowSeatsHTML}</div>
            `;
        });

    container.innerHTML = finalHTML + `</div>`;
    loadBooking(data);
    setupSeatSelection();
}

export function setupSeatSelection() {
    selectedSeats = [];
    document.querySelectorAll('.seat-item[data-booked="false"]').forEach((el) => {
        el.addEventListener("click", function () {
            const code = this.dataset.code;
            const isDouble = this.dataset.type === "COUPLE";
            const index = selectedSeats.findIndex((s) => s.code === code);

            if (index > -1) {
                selectedSeats.splice(index, 1);
                this.classList.remove("bg-[#F1B400]", "text-white", "border-[#F1B400]");
                this.classList.add(isDouble ? "bg-[#F8A4FF]" : "bg-white");
            } else {
                selectedSeats.push({
                    code,
                    name: this.dataset.location,
                    price: parseInt(this.dataset.price),
                    type: this.dataset.type,
                });
                this.classList.add("bg-[#F1B400]", "text-white", "border-[#F1B400]");
                this.classList.remove("bg-[#F8A4FF]", "bg-white");
            }
            updateSummaryDisplay();
        });
    });
}

function updateSummaryDisplay() {
    const seatListElement = document.getElementById("selected_seats_list");
    const totalPriceElement = document.getElementById("total_price");

    if (seatListElement) {
        seatListElement.innerText = selectedSeats.length ? `Ghế: ${selectedSeats.map(s => s.name).join(", ")}` : "Ghế: ";
    }

    if (totalPriceElement) {
        const total = selectedSeats.reduce((sum, s) => sum + s.price, 0);
        totalPriceElement.innerText = selectedSeats.length ? `${total.toLocaleString("vi-VN")} VND` : "0 VND";
    }
}

export async function handlePayment() {
    if (!selectedSeats.length) return showAlert("error", "Thông báo", "Vui lòng chọn ghế");
    const showId = window.history.state?.selectedShowId;
    if (!showId) return showAlert("error", "Lỗi", "Không tìm thấy mã suất chiếu.");

    try {
        const res = await fetchAPI(`/api/bookings/create`, {
            method: "POST",
            body: JSON.stringify({
                id_show: showId,
                code_seats: selectedSeats.map((seat) => seat.code),
            }),
        });

        if (!res.ok) {
            return showAlert("error", "Thông báo", res.data?.message || "Lỗi tạo đơn hàng. Vui lòng đăng nhập lại.");
        }

        const data = res.data?.data || res.data;
        showAlert("success", "Thông báo", "Giữ chỗ thành công");
        sessionStorage.setItem("code", data.code);

        document.getElementById("step-seat-selection")?.classList.add("hidden");
        document.getElementById("step-payment")?.classList.remove("hidden");

        initBookingFlow();
    } catch (e) {
        showAlert("error", "Lỗi", "Có lỗi xảy ra trong quá trình đặt vé.");
    }
}

export default function updateNav(stepIndex) {
    const items = document.querySelectorAll("#booking-nav .nav-item-step");
    const block_move = document.getElementById("nav-booking-move");
    const targetElement = items[stepIndex];

    if (!targetElement || !block_move) return;

    block_move.style.left = `${targetElement.offsetLeft}px`;
    block_move.style.width = `${targetElement.offsetWidth}px`;

    items.forEach((item, index) => {
        const isActive = index === stepIndex;
        item.classList.toggle("text-black", isActive);
        item.classList.toggle("font-medium", isActive);
        item.classList.toggle("text-gray-600", !isActive);
    });
}

export async function bookingHistory(page = 1, limit = 5, q = '') {
    try {
        let url = `/api/bookings?page=${page}&limit=${limit}`;
        if (q !== '') url += `&q=${q}`;

        const res = await fetchAPI(url, { method: 'GET' });

        if (res.ok && res.data?.status === "success") {
            const responseData = res.data.data;
            await renderHistoryItems(responseData.bookings);
            renderPagination(responseData);
        } else {
            showAlert("error", "Lỗi", "Không thể lấy lịch sử đặt vé.");
        }
    } catch (error) {}
}

function buttonHtml(booking, cancelHour) {
    const now = new Date();
    const startTime = parseBookingDate(booking.start_time);

    let isExpired = false;
    if (booking.expired_time) {
        const expiresTime = parseBookingDate(booking.expired_time);
        isExpired = now > expiresTime;
    }

    const hoursUntilStart = (startTime - now) / (1000 * 60 * 60);

    let cancelText = "Hủy vé";
    let cancelDisabled = true;
    let cancelClass = "bg-gray-300 text-gray-600 cursor-not-allowed";

    let payDisabled = true;
    let payClass = "bg-gray-300 text-gray-600 cursor-not-allowed";

    if (booking.payment_status === "PAID") {
        if (hoursUntilStart > cancelHour) {
            cancelDisabled = false;
            cancelClass = "bg-[#FF000050] text-black hover:bg-red-400";
        } else {
            cancelDisabled = true;
            cancelClass = "bg-gray-300 text-gray-600 cursor-not-allowed";
        }
    } else if (booking.payment_status === "REFUNDING") {
        cancelText = "Hoàn tiền";
        cancelDisabled = false;
        cancelClass = "bg-[#FF000050] text-black hover:bg-red-400";
    } else if (booking.payment_status === "REFUNDED") {
        cancelText = "Hoàn tiền";
        cancelDisabled = true;
    } else if (booking.payment_status === "PENDING") {
        cancelDisabled = true;
        cancelClass = "bg-gray-300 text-gray-600 cursor-not-allowed";
    }

    if (booking.payment_status === "PENDING") {
        if (!isExpired) {
            payDisabled = false;
            payClass = "bg-[#00B7FF50] text-black hover:bg-blue-400";
        } else {
            payDisabled = true;
            payClass = "bg-gray-300 text-gray-600 cursor-not-allowed";
        }
    }

    const cancelBtn = `<button ${cancelDisabled ? 'disabled' : ''} data-action="${cancelText === 'Hoàn tiền' ? 'refund' : 'cancel'}" class="btn-cancel w-[90px] h-[28px] text-xs rounded-md ${cancelClass} transition-colors flex justify-center items-center">${cancelText}</button>`;
    const payBtn = `<button ${payDisabled ? 'disabled' : ''} class="btn-payment w-[90px] h-[28px] text-xs rounded-md ${payClass} transition-colors flex justify-center items-center">Thanh toán</button>`;

    return `<div class="flex items-center gap-2">\n${cancelBtn}\n${payBtn}\n</div>`;
}

async function renderHistoryItems(bookings) {
    const container = document.getElementById("history-list");
    if (!container) return;

    if (!bookings.length) {
        container.innerHTML = `
            <div class="text-center py-10">
                <p class="text-gray-500 mb-4">Bạn chưa có lịch sử đặt vé nào.</p>
                <a href="/schedule" class="px-6 py-2 bg-blue-500 text-white rounded-full">Đặt vé ngay</a>
            </div>`;
        return;
    }

    const cancelHour = await fetchCancelHour();
    const { body } = await loadHTML("/templates/components/history/item_history.html");
    const template = body.innerHTML;

    const typeConfig = {
        'PENDING': { color: "#00B8FF", text: "Chưa thanh toán" },
        'PAID': { color: "#36D431", text: "Đã thanh toán" },
        'REFUNDING': { color: "#00B8FF", text: "Đang hoàn tiền" },
        'REFUNDED': { color: "#FF2323", text: "Đã hoàn tiền" }
    };

    container.innerHTML = bookings.map(booking => {
        const statusConfig = typeConfig[booking.payment_status] || typeConfig['PENDING'];
        const [time, date] = booking.start_time.split(" ");

        const cardClass = booking.payment_status === "REFUNDED"
            ? "opacity-70 cursor-not-allowed bg-gray-50"
            : "cursor-pointer hover:shadow-lg hover:-translate-y-1";

        return template
            .replace(/{{card_class}}/g, cardClass)
            .replace(/{{code}}/g, booking.code)
            .replace(/{{film}}/g, booking.film_title)
            .replace(/{{time}}/g, time)
            .replace(/{{date}}/g, date)
            .replace(/{{type}}/g, statusConfig.text)
            .replace(/{{color}}/g, statusConfig.color)
            .replace(/{{action_button}}/g, buttonHtml(booking, cancelHour));
    }).join("");

    container.addEventListener("click", async (e) => {
        const card = e.target.closest("div[data-code]:not(.cursor-not-allowed)");
        if (!card) return;

        const code = card.dataset.code;
        sessionStorage.setItem('code', code);

        const cancelBtn = e.target.closest(".btn-cancel:not([disabled])");
        if (cancelBtn) {
            const action = cancelBtn.dataset.action;
            sessionStorage.setItem('action', action);
            window.location.href = `/cancel`;
            return;
        }

        if (e.target.closest(".btn-payment:not([disabled])")) {
            window.location.href = `/booking`;
            return;
        }

        if (!e.target.closest("button")) {
            window.location.href = `/booking`;
        }
    });
}

export async function searchHis() {
    const search = document.getElementById('search-his');
    if (!search) return;

    let typingTimer;
    const doneTypingInterval = 500;

    search.addEventListener('input', () => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            const q = search.value;
            bookingHistory(1, 5, q);
        }, doneTypingInterval);
    });
}

window.goToPage = function(page) {
    const searchInput = document.getElementById('search-his');
    const q = searchInput ? searchInput.value : '';
    bookingHistory(page, 5, q);
};

function renderPagination(meta) {
    const container = document.getElementById("pagination-controls");
    if (!container) return;

    const totalPages = Math.ceil(meta.total / meta.limit);
    const prevClass = meta.isPrevious ? "bg-white text-gray-700 hover:bg-gray-50 cursor-pointer" : "bg-gray-200 text-gray-400 cursor-not-allowed shadow-inner";
    const nextClass = meta.isNext ? "bg-white text-gray-700 hover:bg-gray-50 cursor-pointer" : "bg-gray-200 text-gray-400 cursor-not-allowed shadow-inner";

    container.innerHTML = `
        <button ${meta.isPrevious ? `onclick="window.goToPage(${meta.page - 1})"` : 'disabled'} 
                class="px-4 py-2 font-semibold rounded-xl transition shadow-sm ${prevClass}">
            <i class="fa-solid fa-chevron-left mr-2"></i> Trước
        </button>
        
        <span class="font-bold text-gray-600 bg-white px-4 py-2 rounded-xl shadow-sm">
            Trang ${meta.page} <span class="text-gray-400 font-normal">/ ${totalPages}</span>
        </span>
        
        <button ${meta.isNext ? `onclick="window.goToPage(${meta.page + 1})"` : 'disabled'} 
                class="px-4 py-2 font-semibold rounded-xl transition shadow-sm ${nextClass}">
            Sau <i class="fa-solid fa-chevron-right ml-2"></i>
        </button>
    `;
}

export async function initBookingFlow(wait = false) {
    const newShowId = sessionStorage.getItem('selectedShowId');

    if (newShowId) {
        sessionStorage.removeItem('code');
        switchStep("step-seat-selection");
        updateNav(0);
        loadSeat();
        return;
    }

    const code = sessionStorage.getItem('code') ?? window.history.state?.code;

    if (code) {
        sessionStorage.setItem('code', code);
        const bookingData = await getBookingByCode();
        window.history.replaceState({ code: bookingData?.code }, "");

        if (bookingData) {
            if (bookingData.payment_status === "PENDING") {
                switchStep("step-payment");
                updateNav(1);
                renderInvoice(bookingData);
                getInfoUser();
                return;
            }

            if (bookingData.payment_status === "PAID") {
                switchStep("step-ticket");
                updateNav(2);
                renderTicket(bookingData);
                getInfoUser();
                return;
            }

            if (bookingData.payment_status === "REFUNDED") {
                window.location.href = '/history';
                return;
            }
        }
    } else {
        sessionStorage.removeItem("code");
    }

    const historyShowId = window.history.state?.selectedShowId;
    if (historyShowId) {
        switchStep("step-seat-selection");
        updateNav(0);
        loadSeat();
    }
}