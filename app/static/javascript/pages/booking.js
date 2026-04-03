import * as bookingComponents from "../components/booking_components.js"
import * as paymentComponents from "../components/payment_components.js"
import * as ticketComponents from  "../components/ticket_component.js"
import {renderTicket} from "../components/ticket_component.js";


document.addEventListener('DOMContentLoaded', function () {
    bookingComponents.loadSeat()
    window.getShowSeat = bookingComponents.getShowSeat
    window.handlePayment= bookingComponents.handlePayment
    bookingComponents.loadBooking()
    bookingComponents.updateNav(0)
    window.handleStartPayment= paymentComponents.handleStartPayment
    window.getSeats = paymentComponents.getSeats
    window.getBookingCode = paymentComponents.getBookingByCode

    window.renderTicket = ticketComponents.renderTicket
})