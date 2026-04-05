import {loadHTML} from "../utils/load.js";
import {getBookingByCode} from "./payment_components.js";

export async function renderTicket() {
    try {
        const booking = await getBookingByCode();
        console.log(booking)
        const stringSeats = booking.seats.map((item) => item.name).join(", ");
        const templateResponse = await loadHTML(
            "/templates/components/booking_seat/ticket_components.html",
        );
        const template = templateResponse.body.innerHTML;
        let html = template
            .replace("{{theater}}", booking.cinema_name)
            .replace("{{address}}", booking.address)
            .replace("{{movie_title}}", booking.film_title)
            .replace("{{room}}", booking.room_name)
            .replace("{{seats}}", stringSeats)
            .replace("{{date}}", booking.start_time.split(" ")[1])
            .replace("{{time}}", booking.start_time.split(" ")[0])
            .replace("{{code}}", booking.code)
            .replace("{{price}}", `${booking.total_price.toLocaleString("vi-VN")}`);
        const container = document.getElementById("ticket");
        container.innerHTML = html;
        const qrContainer = document.getElementById("ticket-qrcode");
        if (qrContainer) {
            qrContainer.innerHTML = "";
            new QRCode(qrContainer, {
                text: booking.code,
                width: 150,
                height: 150,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H
            });
        }
    } catch
        (e) {
        console.error("Lỗi khi tải thông tin đặt vé:", e);
    }
}

export function downloadTicketImage() {
    const save_ticket = document.getElementById("save-ticket")
    save_ticket.addEventListener('click', async () => {
        const ticketElement = document.getElementById("ticket");
        if (!ticketElement) return;
        try {
            ticketElement.style.borderRadius = "0px";
            const canvas = await html2canvas(ticketElement, {
                scale: 2,
                useCORS: true,
                backgroundColor: null
            });

            ticketElement.style.borderRadius = "2.5rem";

            const imageUrl = canvas.toDataURL("image/png");

            const downloadLink = document.createElement("a");
            downloadLink.href = imageUrl;
            downloadLink.download = `Ve_CineFlow_${sessionStorage.getItem("code")}.png`;
            downloadLink.click();

        } catch (error) {
            console.error("Error download ticket:", error);
        }
    })
}
