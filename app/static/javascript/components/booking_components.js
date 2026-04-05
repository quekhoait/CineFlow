import {loadHTML, showError} from "../utils/load.js";
import {showAlert} from "../utils/alert.js";
import {
    getBookingByCode,
    getInfoUser,
    renderInvoice,
} from "./payment_components.js";

export function handleSelectShow(id) {
    sessionStorage.setItem("selectedShowId", id);
    window.location.href = `/booking`;
}

export async function getShowSeat() {
    const id = sessionStorage.getItem("selectedShowId");
    if (!id) return null;
    try {
        const res = await fetch(`/api/shows/${id}`, {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
        })
        if (res.status === 200) {
            const result = await res.json();
            return result.data;
        } else {
            const errorData = await res.json();
            showError('Get Seats', errorData)
            return null;
        }
    } catch (e) {
        showAlert("error", "Get Seats", "Load seat failed")
        return null;
    }
}

export async function loadBooking() {
    try {
        const data = await getShowSeat();
        if (!data) {
            console.error("Show not exist!!");
            return;
        }
        const templateResponse = await loadHTML(
            "/templates/components/card_booking_film.html",
        );
        const template = templateResponse.body.innerHTML;
        let html = template
            .replace("{{poster}}", data.poster)
            .replace("{{title}}", data.film_title)
            .replace("{{room}}", data.room_name)
            .replace("{{time}}", data.start_time)
            .replace("{{seats}}", " ")
            .replace(
                "{{price}}",
                (data.base_price || 0).toLocaleString("vi-VN"),
            );
        const container = document.getElementById("booking_summary");
        if (container) {
            container.innerHTML = html;
        }
    } catch (e) {
        console.error("Lỗi khi tải thông tin đặt vé:", e);
    }
}

export async function loadSeat() {
    const data = await getShowSeat();
    const seats = data?.seats;
    const container = document.getElementById("seat_container");

    if (container && seats) {
        const rows = seats.reduce((acc, seat) => {
            const r = seat.row;
            if (!acc[r]) acc[r] = [];
            acc[r].push(seat);
            return acc;
        }, {});

        const maxCols = Math.max(...seats.map((s) => parseInt(s.col || s.column || 0)));

        let finalHTML = `<div class="grid grid-cols-[24px_max-content] items-center gap-y-3 gap-x-4 mx-auto w-max">`;

        Object.entries(rows)
            .sort(([rowA], [rowB]) => {
                if (rowA.length !== rowB.length) return rowA.length - rowB.length;
                return rowA.localeCompare(rowB);
            })
            .forEach(([label, seatsInRow]) => {
                let rowSeatsHTML = "";

                for (let col = 1; col <= maxCols; col++) {
                    const seat = seatsInRow.find((s) => parseInt(s.col) === col);

                    if (seat) {
                        const isCouple = seat.type === "COUPLE";
                        const isBooked = seat.is_booked === true;

                        let seatClass = isCouple ? "w-[88px] bg-[#F8A4FF]" : "w-10 bg-white";

                        if (isBooked) {
                            seatClass = (isCouple ? "w-[88px]" : "w-10") + " bg-[#A1A3A6] cursor-not-allowed opacity-60";
                        } else {
                            seatClass += " cursor-pointer hover:border-[#F1B400] hover:scale-105";
                        }

                        rowSeatsHTML += `
                            <div class="seat-item h-8 ${seatClass} border border-gray-200 rounded-md flex items-center justify-center text-[10px] font-bold transition-all shadow-sm"
                                 data-code="${seat.code}"
                                 data-booked="${isBooked}"
                                 data-location="${seat.row}${seat.col || seat.column}"
                                 data-type="${seat.type}"
                                 data-price="${seat.price}">
                                ${seat.row}${seat.col || seat.column}
                            </div>`;
                    } else {
                        rowSeatsHTML += `<div class="w-10 h-8"></div>`;
                    }
                }

                finalHTML += `
                    <span class="text-xs font-bold text-gray-500 text-right">${label}</span>
                    <div class="flex gap-2 justify-start">
                        ${rowSeatsHTML}
                    </div>
                `;
            });

        finalHTML += `</div>`;

        container.innerHTML = finalHTML;
        setupSeatSelection();
    } else {
        console.error("No find container to load seat");
    }
}

let selectedSeats = [];

export function setupSeatSelection() {
    const seatElements = document.querySelectorAll(
        '.seat-item[data-booked="false"]',
    );

    selectedSeats = [];

    seatElements.forEach((el) => {
        el.addEventListener("click", function () {
            const seatCode = this.getAttribute("data-code");
            const location = this.getAttribute("data-location");
            const type = this.getAttribute("data-type");
            const price = this.getAttribute("data-price")

            const isDouble = type === "COUPLE";
            const index = selectedSeats.findIndex((s) => s.code === seatCode);

            if (index > -1) {
                selectedSeats.splice(index, 1);
                this.classList.remove("bg-[#F1B400]", "text-white", "border-[#F1B400]");
                if (isDouble) {
                    this.classList.add("bg-[#F8A4FF]");
                } else {
                    this.classList.add("bg-white");
                }
            } else {
                selectedSeats.push({
                    code: seatCode,
                    name: location,
                    price: parseInt(price),
                    type: type,
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

    if (selectedSeats.length > 0) {
        const names = selectedSeats.map((s) => s.name).join(", ");
        if (seatListElement) seatListElement.innerText = `Ghe: ${names}`;
        const totalPrice = selectedSeats.reduce((sum, s) => sum + s.price, 0);
        if (totalPriceElement)
            totalPriceElement.innerText = `${totalPrice.toLocaleString("vi-VN")} VND`;
    } else {
        if (seatListElement) seatListElement.innerText = "Ghế: ";
        if (totalPriceElement) totalPriceElement.innerText = "0 VND";
    }
}

export async function handlePayment() {
    if (selectedSeats.length === 0) {
        showAlert("error", "Thông báo", "Vui lòng chọn ghế");
        return;
    }
    const codeSeat = selectedSeats.map((seat) => seat.code);
    const idShow = sessionStorage.getItem("selectedShowId");
    try {
        const res = await fetch(`/api/bookings/create`, {
            method: "POST",
            body: JSON.stringify({
                id_show: idShow,
                code_seats: codeSeat,
            }),
            headers: {
                "Content-Type": "application/json",
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            },
        });
        if (res.ok) {
            const data = await res.json();
            showAlert("success", "Thống báo", "Giữ chỗ thành công");
            sessionStorage.setItem("code", data.data.code);
            const seatSection = document.getElementById("step-seat-selection");
            const paymentSection = document.getElementById("step-payment");
            if (seatSection && paymentSection) {
                seatSection.classList.add("hidden");
                paymentSection.classList.remove("hidden");
                updateNav(1);
            }
            renderInvoice();
            getInfoUser();
        } else {
            showAlert("error", "Thống báo", "Vui lòng đăng nhập");
        }
    } catch (e) {
        console.error("Lỗi fetch:", e);
        return null;
    }
}

function updateNav(stepIndex) {
    const nav = document.getElementById("booking-nav");
    const block_move = document.getElementById("nav-booking-move");
    const items = nav.querySelectorAll(".nav-item-step");
    const targetElement = items[stepIndex];
    if (!targetElement || !block_move) return;
    const left = targetElement.offsetLeft;
    const width = targetElement.offsetWidth;
    block_move.style.left = `${left}px`;
    block_move.style.width = `${width}px`;
    items.forEach((item, index) => {
        if (index === stepIndex) {
            item.classList.remove("text-gray-600");
            item.classList.add("text-black", "font-medium");
        } else {
            item.classList.remove("text-black", "font-medium");
            item.classList.add("text-gray-600");
        }
    });
}

export default updateNav

export async function bookingHistory(page = 1, limit = 5) {
    try {
        const response = await fetch(`/api/bookings?page=${page}&limit=${limit}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
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

function buttonHtml(type) {
    let html = ""
    if (type !== "REFUND") {
        html += `<button class="px-4 py-1 bg-[#FF000050] text-black text-xs rounded-md cursor-not-allowed">Hủy vé</button>`
        if (type !== "PAID") {
            html += `<button class="px-4 py-1 bg-[#00B7FF50] text-black text-xs rounded-md cursor-not-allowed">Thanh toán</button>`
        } else {
            html += `<button disabled  class="px-4 py-1 bg-gray-300 text-gray-600 text-xs rounded-md cursor-not-allowed">Thanh toán</button>`
        }
    }
    else {
        html +=
            `<button disabled className="px-4 py-1 bg-gray-300 text-gray-600 text-xs rounded-md cursor-not-allowed">Hủy vé</button>
            <button disabled  class="px-4 py-1 bg-gray-300 text-gray-600 text-xs rounded-md cursor-not-allowed">Thanh toán</button>`
    }
    return html
}

async function renderHistoryItems(bookings) {
    const container = document.getElementById("history-list");
    if (!container) return;

    if (bookings.length === 0) {
        container.innerHTML = `
            <div class="text-center py-10">
                <p class="text-gray-500 mb-4">Bạn chưa có lịch sử đặt vé nào.</p>
                <a href="/booking" class="px-6 py-2 bg-blue-500 text-white rounded-full">Đặt vé ngay</a>
            </div>`;
        return;
    }

    const historyHTML = await loadHTML("/templates/components/history/item_history.html");
    const template = historyHTML.body.innerHTML;

    let html = "";
    let type = {
        'PENDING': {"color": "#00B8FF","type": "Chưa thanh toán"},
        'PAID': {"color": "#36D431" ,"type": "Đã thanh toán"},
        'REFUND': {"color": "#FF2323", "type": "Đã hủy"}
    }
    bookings.forEach(booking => {
        const btns = buttonHtml(booking.payment_status, type)

        html += template
            .replace("{{code}}", booking.code)
            .replace("{{film}}", booking.film_title)
            .replace("{{time}}", booking.start_time.split(" ")[0])
            .replace("{{date}}", booking.start_time.split(" ")[1])
            .replace("{{type}}", type[booking.payment_status]["type"])
            .replace("{{color}}", type[booking.payment_status]["color"])
            .replace("{{color}}", type[booking.payment_status]["color"])
            .replace("{{action_button}}", btns);
    });


    container.innerHTML = html;
}

function renderPagination(metaData) {
    const container = document.getElementById("pagination-controls");
    if (!container) return;

    const totalPages = Math.ceil(metaData.total / metaData.limit);

    let html = "";

    if (metaData.isPrevious) {
        html += `<button onclick="window.goToPage(${metaData.page - 1})" class="px-4 py-2 bg-white text-gray-700 font-semibold rounded-xl shadow-sm hover:bg-gray-50 transition">
                    <i class="fa-solid fa-chevron-left mr-2"></i> Trước
                 </button>`;
    } else {
        html += `<button disabled class="px-4 py-2 bg-gray-200 text-gray-400 font-semibold rounded-xl shadow-inner cursor-not-allowed">
                    <i class="fa-solid fa-chevron-left mr-2"></i> Trước
                 </button>`;
    }

    html += `<span class="font-bold text-gray-600 bg-white px-4 py-2 rounded-xl shadow-sm">
                Trang ${metaData.page} <span class="text-gray-400 font-normal">/ ${totalPages}</span>
             </span>`;

    if (metaData.isNext) {
        html += `<button onclick="window.goToPage(${metaData.page + 1})" class="px-4 py-2 bg-white text-gray-700 font-semibold rounded-xl shadow-sm hover:bg-gray-50 transition">
                    Sau <i class="fa-solid fa-chevron-right ml-2"></i>
                 </button>`;
    } else {
        html += `<button disabled class="px-4 py-2 bg-gray-200 text-gray-400 font-semibold rounded-xl shadow-inner cursor-not-allowed">
                    Sau <i class="fa-solid fa-chevron-right ml-2"></i>
                 </button>`;
    }

    container.innerHTML = html;
}

window.goToPage = function (pageNumber) {
    bookingHistory(pageNumber);
    window.scrollTo({top: 0, behavior: 'smooth'});
};