import {loadHTML, showError} from "../utils/load.js";
import {showAlert} from "../utils/alert.js";
import {
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
