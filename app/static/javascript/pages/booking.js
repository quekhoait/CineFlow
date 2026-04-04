import * as bookingComponents from "../components/booking_components.js"
import * as paymentComponents from "../components/payment_components.js"
import * as ticketComponents from  "../components/ticket_component.js"
import {downloadTicketImage} from "../components/ticket_component.js";
import {checkMomoReturn} from "../components/payment_components.js";

document.addEventListener('DOMContentLoaded', function () {
    bookingComponents.default(0)
    checkMomoReturn()
    downloadTicketImage()
    bookingComponents.loadSeat()
    window.handlePayment = bookingComponents.handlePayment
    bookingComponents.loadBooking()
    window.handleStartPayment= paymentComponents.handleStartPayment
    window.getBookingCode = paymentComponents.getBookingByCode
    window.renderTicket = ticketComponents.renderTicket
})