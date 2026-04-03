import { loadHTML } from "../utils/load.js";
import { getShowSeat, updateNav } from "./booking_components.js";
import { getUser } from "./base.js";
import { showAlert } from "../utils/alert.js";
import { renderTicket } from "./ticket_component.js";

export async function getSeats() {
  try {
    const code_booking = sessionStorage.getItem("code");
    const res = await fetch(`/api/bookings/seats/${code_booking}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
      },
    });

    if (res.status === 200) {
      return await res.json();
    }
    return null;
  } catch (error) {
    console.error("Profile Error:", error);
    showAlert("error", "Error Connection", "Error Connection to CineFlow");
    return null;
  }
}

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
      return result;
    }
    return null;
  } catch (error) {
    console.error("Profile Error:", error);
    showAlert("error", "Error Connection", "Error Connection to CineFlow");
    return null;
  }
}

export async function loadBookingPayment() {
  try {
    const data = await getShowSeat();
    const seats = await getSeats();
    const booking = await getBookingByCode();
    const stringSeats = seats.data.map((item) => item.seat.name).join(", ");
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
      .replace("{{seats}}", stringSeats)
      .replace("{{price}}", booking.data.total_price);
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
  const info = await getSeats();
  const booking = await getBookingByCode();
  console.log(booking);
  const container = document.getElementById("invoice_items");
  if (!container) return;
  let itemsHtml = "";
  info.data.forEach((seat) => {
    const description = (seat.type = "SeatType.SINGLE" ? "Ghế đơn" : "Ghế đôi");

    itemsHtml += `
            <tr class="border-b border-gray-50 last:border-0">
                <td class="py-4">
                    <div class="font-bold text-gray-800">${description}</div>
                    <div class="text-xs text-gray-400">Phim: ${info.film_title || "N/A"}</div>
                </td>
                <td class="py-4 text-center font-mono text-gray-600">${seat.seat.name}</td>
                <td class="py-4 text-center">1</td>
                <td class="py-4 text-right font-bold">${booking.data.total_price}</td>
            </tr>
        `;
  });
  container.innerHTML = itemsHtml;
  final_total_price = booking.data.total_price;
  // document.getElementById('vat_amount').innerText = `${vat.toLocaleString('vi-VN')} VND`;
  document.getElementById("final_total").innerText =
    `${final_total_price.toLocaleString("vi-VN")} VND`;
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
        <p><span class="text-gray-500">Họ và tên:</span> <span class="font-semibold ml-2 text-gray-800">${user.full_name || "N/A"}</span></p>
        <p><span class="text-gray-500">Số điện thoại:</span> <span class="font-semibold ml-2 text-gray-800">${user.phone_number || "N/A"}</span></p>
        <p><span class="text-gray-500">Email:</span> <span class="font-semibold ml-2 text-gray-800">${user.email || "N/A"}</span></p>
    `;

  formUser.innerHTML = template;
}

export async function goBackToSeats() {
  const seatSection = document.getElementById("step-seat-selection");
  const paymentSection = document.getElementById("step-payment");
  const btnPayment = document.getElementById("btn_payment");
  if (seatSection && paymentSection) {
    seatSection.classList.remove("hidden");
    paymentSection.classList.add("hidden");
    btnPayment.classList.add("hidden");
    updateNav(2);
  }
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
      updateNav(2);
      renderTicket();
      window.open(result.data.payUrl, "_blank");
    }
  } catch (error) {
    console.error("Profile Error:", error);
    showAlert("error", "Error Connection", "Error Connection to CineFlow");
    return null;
  }
}
