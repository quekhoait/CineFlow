import { getShowSeat } from "./booking_components.js";
import { loadHTML } from "../utils/load.js";
import { getBookingByCode, getSeats } from "./payment_components.js";

export async function renderTicket() {
  try {
    const data = await getShowSeat();
    const seats = await getSeats();
    const booking = await getBookingByCode();
    console.log(booking);
    console.log(seats);
    const stringSeats = seats.data.map((item) => item.seat.name).join(", ");

    const templateResponse = await loadHTML(
      "/templates/components/booking_seat/ticket_components.html",
    );
    const template = templateResponse.body.innerHTML;
    let html = template
        .replace("{{theater}}", data.show_info.cinema_name)
        .replace("{{address}}", data.show_info.address)
        .replace("{{movie_title}}", data.show_info.film_title)
        .replace("{{room}}", data.show_info.room_name)
        .replace("{{seats}}", stringSeats)
        .replace("{{date}}", "1")
        .replace("{{time}}", "1")
        .replace("{{code}}", booking.data.code)
        .replace("{{price}}", booking.data.total_price);
    const container = document.getElementById("ticket");
    container.innerHTML = html;
  } catch (e) {
    console.error("Lỗi khi tải thông tin đặt vé:", e);
  }
}
