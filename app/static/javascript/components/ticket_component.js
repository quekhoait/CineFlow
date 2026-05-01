import { loadHTML } from "../utils/load.js";

export async function renderTicket(booking) {
    if (!booking) return;

    try {
        const stringSeats = (booking.seats || []).map((item) => item.name).join(", ");
        const [time = '', date = ''] = (booking.start_time || '').split(" ");
        const priceStr = (parseInt(booking.total_price) || 0).toLocaleString("vi-VN");

        const templateResponse = await loadHTML("/templates/components/booking_seat/ticket_components.html");
        const template = templateResponse.body.innerHTML;

        let html = template
            .replace(/{{theater}}/g, booking.cinema_name || '')
            .replace(/{{address}}/g, booking.address || '')
            .replace(/{{movie_title}}/g, booking.film_title || '')
            .replace(/{{room}}/g, booking.room_name || '')
            .replace(/{{seats}}/g, stringSeats)
            .replace(/{{date}}/g, date)
            .replace(/{{time}}/g, time)
            .replace(/{{code}}/g, booking.code || '')
            .replace(/{{price}}/g, priceStr);

        const container = document.getElementById("ticket");
        if (container) {
            container.innerHTML = html;
        }

        const qrContainer = document.getElementById("ticket-qrcode");
        if (qrContainer && typeof QRCode !== 'undefined') {
            qrContainer.innerHTML = "";
            new QRCode(qrContainer, {
                text: booking.code || '',
                width: 150,
                height: 150,
                colorDark: "#000000",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.H
            });
        }
    } catch (e) {
        console.error("Lỗi khi tải thông tin đặt vé:", e);
    }
}

export function downloadTicketImage() {
    const save_ticket = document.getElementById("save-ticket");
    if (!save_ticket) return;

    save_ticket.onclick = async () => {
        const ticketElement = document.getElementById("ticket");
        if (!ticketElement || typeof html2canvas === 'undefined') return;

        const originalRadius = ticketElement.style.borderRadius;

        try {
            ticketElement.style.borderRadius = "0px";
            const canvas = await html2canvas(ticketElement, {
                scale: 2,
                useCORS: true,
                backgroundColor: null
            });

            ticketElement.style.borderRadius = originalRadius || "2.5rem";

            const imageUrl = canvas.toDataURL("image/png");
            const downloadLink = document.createElement("a");
            downloadLink.href = imageUrl;
            downloadLink.download = `Ve_CineFlow_${Date.now()}.png`;
            downloadLink.click();

        } catch (error) {
            console.error("Error download ticket:", error);
            ticketElement.style.borderRadius = originalRadius || "2.5rem";
        }
    };
}