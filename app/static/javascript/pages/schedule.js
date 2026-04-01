
import * as scheduleComponents from "../components/schedule_components.js"
import * as bookingComponents from "../components/booking_components.js"

document.addEventListener('DOMContentLoaded', function () {
    scheduleComponents.loadDate()
    scheduleComponents.loadBranch()
    scheduleComponents.loadFilm()
    window.handleSelectBranch = scheduleComponents.handleSelectBranch;
    window.handleSelectDate = scheduleComponents.handleSelectDate;
     window.handleSelectShow = bookingComponents.handleSelectShow;
})