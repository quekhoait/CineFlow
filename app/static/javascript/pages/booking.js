import * as bookingComponents from "../components/booking_components.js";
import * as paymentComponents from "../components/payment_components.js";
import * as ticketComponents from "../components/ticket_component.js";

document.addEventListener('DOMContentLoaded', async function () {
    window.handlePayment = bookingComponents.handlePayment;
    window.handleStartPayment = paymentComponents.handleStartPayment;
    window.getBookingCode = paymentComponents.getBookingByCode;
    window.renderTicket = ticketComponents.renderTicket;
    ticketComponents.downloadTicketImage();
    await paymentComponents.checkMomoReturn();
    bookingComponents.initBookingFlow();
});