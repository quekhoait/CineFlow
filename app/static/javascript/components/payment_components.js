import { loadHTML } from "../utils/load.js";
import { getShowSeat } from "./booking_components.js";

export async function loadBookingPayment() {
  try {
    const data = await getShowSeat();
    const rawData = sessionStorage.getItem("bookingData");
    const info = JSON.parse(rawData);
    const seatNames = info.seats.map((seat) => seat.name).join(", ");
    const totalPrice = info.seats.reduce((sum, seat) => sum + seat.price, 0);
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
      .replace("{{seats}}", seatNames)
      .replace("{{price}}", totalPrice);
    const container = document.getElementById("info_film");
    console.log(container);
    if (container) {
      container.innerHTML = html;
    }
  } catch (e) {
    console.error("Lỗi khi tải thông tin đặt vé:", e);
  }
}

export function renderInvoice() {
  const rawData = sessionStorage.getItem("bookingData");
  if (!rawData) return;
  const info = JSON.parse(rawData);
  const container = document.getElementById("invoice_items");
  if (!container) return;
  let itemsHtml = "";
  let subTotal = 0;
  info.seats.forEach((seat) => {
    const description = (seat.type = "SINGLE" ? "Ghế đơn" : "Ghế đôi");
    subTotal += seat.price;
    itemsHtml += `
            <tr class="border-b border-gray-50 last:border-0">
                <td class="py-4">
                    <div class="font-bold text-gray-800">${description}</div>
                    <div class="text-xs text-gray-400">Phim: ${info.film_title || "N/A"}</div>
                </td>
                <td class="py-4 text-center font-mono text-gray-600">${seat.name}</td>
                <td class="py-4 text-center">1</td>
                <td class="py-4 text-right font-bold">${seat.price.toLocaleString("vi-VN")}</td>
            </tr>
        `;
  });
  container.innerHTML = itemsHtml;
  const finalTotal = subTotal;
  // document.getElementById('vat_amount').innerText = `${vat.toLocaleString('vi-VN')} VND`;
  document.getElementById("final_total").innerText =
    `${finalTotal.toLocaleString("vi-VN")} VND`;
}
