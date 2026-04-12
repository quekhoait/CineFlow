import {loadHTML, showError} from "../utils/load.js";
import {showAlert} from "../utils/alert.js";
import {getInfoUser, renderInvoice, getBookingByCode, switchStep} from "./payment_components.js";
import {renderTicket} from "./ticket_component.js";

let selectedSeats = [];

export function handleSelectShow(id) {
    sessionStorage.setItem("selectedShowId", id);
    window.location.href = `/booking`;
}

export async function getShowSeat() {
    const id = sessionStorage.getItem('selectedShowId') === null ? window.history.state?.selectedShowId : sessionStorage.getItem('selectedShowId');
    if (!id) return null;
    window.history.replaceState({selectedShowId: id}, "")
    sessionStorage.removeItem("selectedShowId");

    try {
        const res = await fetch(`/api/shows/${id}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
        });
        const result = await res.json();

        if (res.ok) return result.data;

        showError('Get Seats', result);
        return null;
    } catch (e) {
        showAlert("error", "Get Seats", "Load seat failed");
        return null;
    }
}

export async function loadBooking(data) {
    try {
        if (!data) return console.error("None data in");

        const {body} = await loadHTML("/templates/components/card_booking_film.html");
        let html = body.innerHTML
            .replace("{{poster}}", data.poster)
            .replace("{{title}}", data.film_title)
            .replace("{{room}}", data.room_name)
            .replace("{{time}}", data.start_time)
            .replace("{{seats}}", " ")
            .replace("{{price}}", (data.base_price || 0).toLocaleString("vi-VN"));

        const container = document.getElementById("booking_summary");
        if (container) container.innerHTML = html;
    } catch (e) {
        console.error("Lỗi khi tải thông tin đặt vé:", e);
    }
}

export async function loadSeat() {
    const data = await getShowSeat();
    const container = document.getElementById("seat_container");
    if (!container || !data?.seats) return console.error("No find container to load seat");

    const seats = data.seats;
    const rows = seats.reduce((acc, seat) => {
        (acc[seat.row] = acc[seat.row] || []).push(seat);
        return acc;
    }, {});

    let finalHTML = `<div class="grid grid-cols-[24px_max-content] items-center gap-y-3 gap-x-4 mx-auto w-max">`;

    Object.entries(rows)
        .sort(([a], [b]) => a.localeCompare(b)) // Sắp xếp A, B, C cho chuẩn
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
    loadBooking(data)
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

export async function handlePayment(id) {
    if (!selectedSeats.length) return showAlert("error", "Thông báo", "Vui lòng chọn ghế");

    try {
        const res = await fetch(`/api/bookings/create`, {
            method: "POST",
            body: JSON.stringify({
                id_show: window.history.state?.showId,
                code_seats: selectedSeats.map((seat) => seat.code),
            }),
            headers: {
                "Content-Type": "application/json",
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            },
        });

        if (!res.ok) return showAlert("error", "Thông báo", "Vui lòng đăng nhập");

        const {data} = await res.json();
        showAlert("success", "Thông báo", "Giữ chỗ thành công");
        sessionStorage.setItem("code", data.code);

        document.getElementById("step-seat-selection")?.classList.add("hidden");
        document.getElementById("step-payment")?.classList.remove("hidden");

        initBookingFlow()
    } catch (e) {
        console.error("Lỗi fetch:", e);
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
        let url = `/api/bookings?page=${page}&limit=${limit}`
        if (q !== '') url += `&q=${q}`
        const response = await fetch(url, {
            headers: {Authorization: `Bearer ${localStorage.getItem("accessToken")}`},
        });
        const result = await response.json();

        if (result.status === "success") {
            await renderHistoryItems(result.data.bookings);
            renderPagination(result.data);
        }
    } catch (error) {
        console.error("Lỗi khi tải lịch sử:", error);
    }
}

function buttonHtml(status, code) {
    const isDisabled = status === "REFUNDED";
    const isPaid = status === "PAID";
    const disabledClass = "bg-gray-300 text-gray-600 cursor-not-allowed";

    const cancelBtn = `<button ${isDisabled ? 'disabled' : ''} class="btn-cancel px-4 py-1 ${isDisabled ? disabledClass : 'bg-[#FF000050] text-black'} text-xs rounded-md">Hủy vé</button>`;

    const payBtn = `<button ${isDisabled || isPaid ? 'disabled' : ''} class="btn-payment px-4 py-1 ${isDisabled || isPaid ? disabledClass : 'bg-[#00B7FF50] text-black'} text-xs rounded-md">Thanh toán</button>`;

    return `${cancelBtn}\n${payBtn}`;
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

    const {body} = await loadHTML("/templates/components/history/item_history.html");
    const template = body.innerHTML;

    const typeConfig = {
        'PENDING': {color: "#00B8FF", text: "Chưa thanh toán"},
        'PAID': {color: "#36D431", text: "Đã thanh toán"},
        'REFUNDED': {color: "#FF2323", text: "Đã hủy"}
    };

    container.innerHTML = bookings.map(booking => {
        const statusConfig = typeConfig[booking.payment_status];
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
            .replace(/{{action_button}}/g, buttonHtml(booking.payment_status, booking.code));
    }).join("");

    container.addEventListener("click", async (e) => {
        let card = e.target.closest("div[data-code]:not(.cursor-not-allowed)")
        const code = card.dataset.code
        sessionStorage.setItem('code', code);
        if (e.target.closest(".btn-cancel")) {
            window.location.href = `/cancel`;
        } else {
            window.location.href = `/booking`;
        }
    });
}

export async function searchHis() {
    const search = document.getElementById('search-his')
    let typingTimer
    const doneTypingInterval = 500
    search.addEventListener('input', () => {
        clearTimeout()
        typingTimer = setTimeout(() => {
            const q = search.value
            bookingHistory(1, 5, q)
        }, doneTypingInterval)
    })

}

function renderPagination(meta) {
    const container = document.getElementById("pagination-controls");
    if (!container) return;

    const totalPages = Math.ceil(meta.total / meta.limit);
    const prevClass = meta.isPrevious ? "bg-white text-gray-700 hover:bg-gray-50" : "bg-gray-200 text-gray-400 cursor-not-allowed shadow-inner";
    const nextClass = meta.isNext ? "bg-white text-gray-700 hover:bg-gray-50" : "bg-gray-200 text-gray-400 cursor-not-allowed shadow-inner";

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
    const code = sessionStorage.getItem('code') === null ? window.history.state?.code : sessionStorage.getItem('code');
    sessionStorage.setItem('code', code)
    if (code) {
        const bookingData = await getBookingByCode();
        window.history.replaceState({code: bookingData.code}, "")
        if (bookingData) {
            console.log(bookingData.payment_status)
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
                window.location.href = '/history'
            }
        }
    }

    sessionStorage.removeItem("code");
    const showid = sessionStorage.getItem('selectedShowId') === null ? window.history.state?.selectedShowId : sessionStorage.getItem('selectedShowId');
    if (showid) {
        switchStep("step-seat-selection");
        updateNav(0);
        loadSeat();
    }
}