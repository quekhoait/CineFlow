import * as bookingComponents from "../components/booking_components.js"
import * as paymentComponents from "../components/payment_components.js"


document.addEventListener('DOMContentLoaded', function () {
    bookingComponents.loadSeat()
    window.getShowSeat = bookingComponents.getShowSeat
    window.handlePayment= bookingComponents.handlePayment
    bookingComponents.loadBooking()

})