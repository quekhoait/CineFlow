import * as filmComponents from "../components/film_components.js"
import * as scheduleComponent from "../components/schedule_components.js"
import * as scheduleComponents from "../components/schedule_components.js";

document.addEventListener('DOMContentLoaded', function () {
    filmComponents.loadFilms('showing', 'list_film')
    scheduleComponent.loadDate();
    window.handleSelectDate = scheduleComponents.handleSelectDate;
    window.handleSelectFilm = filmComponents.handleSelectFilm;
})