import * as booking_components from "../components/booking_components.js";
import {bookingHistory} from "../components/booking_components.js";

document.addEventListener("DOMContentLoaded", () => {
    booking_components.bookingHistory(1)
    window.goToPage = function (pageNumber) {
        booking_components.bookingHistory(pageNumber);
        window.scrollTo({top: 0, behavior: 'smooth'});
    };
})