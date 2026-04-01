
import * as filmComponents from "../components/film_components.js"

document.addEventListener('DOMContentLoaded', function () {
    filmComponents.loadFilms('showing', 'slider-1')
    filmComponents.loadFilms('future', 'slider-2');

})