import {loadHTML} from "../utils/load.js";
import {showAlert} from "../utils/alert.js";
import {formatTime} from "../utils/format.js";
import {renderScheduleData} from "./base.js";

export async function loadFilms(strategy, containerId) {
    const doc = await loadHTML("/templates/components/card_film.html");
    const card = doc.body.innerHTML;
    const container = document.getElementById(containerId);
    fetch(`/api/films?strategy=${strategy}`)
        .then(res => res.json())
        .then(res => {
                let html = '';
                res.data.forEach(movie => {
                let cardHtml = card
                    .replace('{{poster}}', movie.poster)
                    .replace('{{content}}', strategy === 'showing'?'Xem chi tiết' : `Khởi chiếu ${movie.release_date}`  )
                    .replace('{{id}}', movie.id)

                html += cardHtml;
                });
                container.innerHTML = html;
        })
        .catch(err => console.error(`Lỗi khi load ${strategy}:`, err));
}

export async function handleSelectFilm(id){
    sessionStorage.setItem('currentId', id)
    window.location.href = `/film/detail`;
}

export async function getFilmById(id){
        try {
        const res = await fetch(`/api/films/${id}`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        });
        const result = await res.json();
        if (res.status === 200) {
            return result;
        }
    } catch (error) {
        console.error("Get film Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
}

export async function loadFilmDetail(){
    const idFilm = sessionStorage.getItem('currentId')
     try {
        const film = await getFilmById(idFilm)
        const { body } = await loadHTML("/templates/components/film_detail/description_film.html");
        console.log(film)
        const html = body.innerHTML
            .replace("{{poster}}", film?.data.poster)
            .replace("{{title}}", film?.data.title)
            .replace("{{description}}", film?.data.description)
            .replace("{{genre}}", film?.data.genre)
            .replace("{{duration}}", film?.data.duration)
            .replace("{{age-limit}}", film?.data.age_limit);

        const container = document.getElementById("film_description");
        if (container) {
            container.innerHTML = html;
        }
    } catch (e) {
        console.error("Lỗi khi tải thông tin phim", e);
    }
}

export async function loadCinemas() {
    const idFilm = sessionStorage.getItem('currentId');
    const selectedDate = sessionStorage.getItem('selected_date');
    if (!idFilm || !selectedDate) return;

    await renderScheduleData({
        apiUrl: `/api/films/${idFilm}/cinemas?date=${selectedDate}`,
        containerId: "list-cinemas",
        templateUrl: "/templates/components/film_detail/cinemas_show_item.html",
        mapper: (template, cinema, buttonsHtml) => {
            return template
                .replace('{{name}}', cinema.name)
                .replace('{{address}}', cinema.address)
                .replace('{{province}}', cinema.province)
                .replace('{{time}}', buttonsHtml);
        }
    });
}