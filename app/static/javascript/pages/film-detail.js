import * as filmComponents from "../components/film_components.js"
import * as scheduleComponent from "../components/schedule_components.js"
import * as bookingComponent from "../components/booking_components.js"



document.addEventListener('DOMContentLoaded', function () {
    scheduleComponent.loadDate();
    window.handleSelectDate = scheduleComponent.handleSelectDate;
    window.handleSelectShow = bookingComponent.handleSelectShow;
    filmComponents.loadFilmDetail()
    filmComponents.loadCinemas()
})