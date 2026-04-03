import { loadHTML } from "../utils/load.js";
import { showAlert } from "../utils/alert.js";
import {
  getInfoUser,
  loadBookingPayment,
  renderInvoice,
} from "./payment_components.js";
import { getUser } from "./base.js";

export function handleSelectShow(id) {
  sessionStorage.setItem("selectedShowId", id);
  window.location.href = `/booking-seat`;
}

export async function getShowSeat() {
  const id = sessionStorage.getItem("selectedShowId");
  if (!id) return null;
  try {
    const res = await fetch(`/api/shows/${id}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });
    if (res.status === 200) {
      const result = await res.json();
      return result.data;
    } else {
      const errorData = await res.json();
      showAlert("error", "Lỗi", errorData.message);
      return null;
    }
  } catch (e) {
    console.error("Lỗi fetch:", e);
    return null;
  }
}

export async function loadBooking() {
  try {
    const data = await getShowSeat();
    if (!data || !data.show_info) {
      console.error("Dữ liệu suất chiếu không tồn tại");
      return;
    }
    const templateResponse = await loadHTML(
      "/templates/components/card_booking_film.html",
    );
    const template = templateResponse.body.innerHTML;
    let html = template
        .replace("{{poster}}", data.show_info.poster)
        .replace("{{title}}", data.show_info.film_title)
        .replace("{{room}}", data.show_info.room_name)
        .replace("{{time}}", data.show_info.start_time)
        .replace("{{seats}}", " ")
        .replace(
            "{{price}}",
            (data.show_info.base_price || 0).toLocaleString("vi-VN"),
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
  const seats = data.seats;
  const container = document.getElementById("seat_container");
  if (container && seats) {
    const rows = Object.groupBy(seats, (seat) => seat.row);
    const maxCols = Math.max(...seats.map((s) => s.col));
    let finalHTML = "";
    Object.entries(rows)
      .sort()
      .forEach(([label, seatsInRow]) => {
        let rowSeatsHTML = "";
        for (let col = 1; col <= maxCols; col++) {
            const seat = seatsInRow.find((s) => s.col === col);
            if (seat) {
                const isCouple = seat.type === "COUPLE";
                const isBooked = seat.is_booked === true;
                let seatClass = isCouple ? "w-16 bg-[#F8A4FF]" : "w-10 bg-white";
                if (isBooked) {
                seatClass =
                    (isCouple ? "w-16" : "w-10") +
                    " bg-[#A1A3A6] cursor-not-allowed opacity-60";
                } else {
                seatClass +=
                    " cursor-pointer hover:border-[#F1B400] hover:scale-105";
                }
                rowSeatsHTML += `
                                <div class="seat-item h-8 ${seatClass} border border-gray-200 rounded-md flex items-center justify-center text-[10px] font-bold transition-all shadow-sm"
                                     data-code="${seat.code}"
                                     data-booked="${isBooked}"
                                     data-location = "${seat.row}${seat.col}"
                                     data-type="${seat.type}"
                                     >
                                    ${seat.row}${seat.col}
                                </div>`;
            } else {
                rowSeatsHTML += `<div class="w-10 h-8"></div>`;
            }
        }
        finalHTML += `
                        <div class="flex items-center gap-4 mb-3 justify-center">
                            <span class="w-6 text-xs font-bold text-gray-500 text-center">${label}</span>
                            <div class="flex gap-2">
                                ${rowSeatsHTML}
                            </div>
                            <span class="w-6 text-xs font-bold text-gray-500 text-center">${label}</span>
                        </div>`;
        });
    container.innerHTML = finalHTML;
    setupSeatSelection();
  } else {
    console.error("Không tìm thấy container hoặc dữ liệu ghế trống");
  }
}

let selectedSeats = [];

export function setupSeatSelection() {
    const seatElements = document.querySelectorAll(
        '.seat-item[data-booked="false"]',
    );
    const priceSingle = 60000;
    const priceCouple = 120000;

    selectedSeats = [];

    seatElements.forEach((el) => {
        el.addEventListener("click", function () {
            const seatCode = this.getAttribute("data-code");
            const location = this.getAttribute("data-location");
            const type = this.getAttribute("data-type");

            const isDouble = this.classList.contains("w-16"); // Giả định ghế đôi có class w-16
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
            // --- LOGIC CHỌN GHẾ ---
            selectedSeats.push({
            code: seatCode,
            name: location,
            price: isDouble ? priceCouple : priceSingle,
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
    if (seatListElement) seatListElement.innerText = "Ghe: ";
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
    const token = localStorage.getItem("accessToken");
    try {
        const res = await fetch(`/api/bookings/create`, {
        method: "POST",
        body: JSON.stringify({
            id_show: idShow,
            code_seats: codeSeat,
        }),
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
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
            loadBookingPayment();
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

export function updateNav(stepIndex) {
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
                item.classList.remove("text-gray-500");
                item.classList.add("text-white", "font-medium");
            } else {
                item.classList.remove("text-white", "font-medium");
                item.classList.add("text-gray-500");
            }
    });
}
