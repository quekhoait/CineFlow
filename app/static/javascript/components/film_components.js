import { loadHTML } from "../utils/load.js";
import { showAlert } from "../utils/alert.js";
import { renderScheduleData } from "./base.js";
import fetchAPI from "../utils/apiClient.js";

export async function loadFilms(strategy, containerId) {
    try {
        const doc = await loadHTML("/templates/components/card_film.html");
        const cardTemplate = doc.body.innerHTML;
        const container = document.getElementById(containerId);

        if (!container) return;
        const res = await fetchAPI(`/api/films?strategy=${strategy}`, { method: 'GET' });

        if (res.ok && res.data?.status === 'success') {
            let html = '';
            const movies = res.data.data || [];

            movies.forEach(movie => {
                let cardHtml = cardTemplate
                    .replace(/{{poster}}/g, movie.poster)
                    .replace(/{{content}}/g, strategy === 'showing' ? 'Xem chi tiết' : `Khởi chiếu ${movie.release_date}`)
                    .replace(/{{id}}/g, movie.id);

                html += cardHtml;
            });
            container.innerHTML = html;
        } else {
            console.error(`Không tải được danh sách phim (${strategy})`);
        }
    } catch (err) {
        console.error(`Lỗi khi load ${strategy}:`, err);
    }
}

export async function handleSelectFilm(id) {
    sessionStorage.setItem('currentId', id);
    window.location.href = `/film/detail`;
}

export async function getFilmById(id) {
    if (!id) return null;

    try {
        const res = await fetchAPI(`/api/films/${id}`, { method: 'GET' });

        if (res.ok) {
            return res.data;
        }

        showAlert("error", "Lỗi tải phim", res.data?.message || "Không thể lấy thông tin phim.");
        return null;
    } catch (error) {
        console.error("Get film Error:", error);
        showAlert("error", "Lỗi mạng", "Không thể kết nối đến máy chủ CineFlow.");
        return null;
    }
}

export async function loadFilmDetail() {
    const idFilm = sessionStorage.getItem('currentId') ?? window.history.state?.currentId;

    if (!idFilm) {
        showAlert("error", "Lỗi", "Không tìm thấy thông tin phim.");
        setTimeout(() => window.location.href = '/', 1500);
        return;
    }

    window.history.replaceState({ currentId: idFilm }, "");

    try {
        const filmResponse = await getFilmById(idFilm);

        if (!filmResponse || !filmResponse.data) return; // Nếu API lỗi thì dừng luôn

        const film = filmResponse.data;
        const { body } = await loadHTML("/templates/components/film_detail/description_film.html");
        const container = document.getElementById("film_description");

        if (container) {
            container.innerHTML = body.innerHTML
                .replace(/{{poster}}/g, film.poster || '')
                .replace(/{{title}}/g, film.title || '')
                .replace(/{{description}}/g, film.description || 'Chưa có thông tin mô tả.')
                .replace(/{{genre}}/g, film.genre || '')
                .replace(/{{duration}}/g, film.duration || '')
                .replace(/{{age-limit}}/g, film.age_limit || '');
        }
    } catch (e) {
        console.error("Lỗi khi tải thông tin chi tiết phim:", e);
    }
}

export async function loadCinemas() {
    const idFilm = sessionStorage.getItem('currentId') ?? window.history.state?.currentId;
    const selectedDate = sessionStorage.getItem('selected_date');
    if (!idFilm || !selectedDate) {
        const container = document.getElementById("list-cinemas");
        if (container) container.innerHTML = `<p class="text-center text-gray-500 mt-4">Vui lòng chọn ngày để xem lịch chiếu.</p>`;
        return;
    }

    console.log(idFilm, selectedDate)

    await renderScheduleData({
        apiUrl: `/api/films/${idFilm}/cinemas?date=${selectedDate}`,
        containerId: "list-cinemas",
        templateUrl: "/templates/components/film_detail/cinemas_show_item.html",
        mapper: (template, cinema, buttonsHtml) => {
            return template
                .replace(/{{name}}/g, cinema.name)
                .replace(/{{address}}/g, cinema.address)
                .replace(/{{province}}/g, cinema.province)
                .replace(/{{time}}/g, buttonsHtml);
        }
    });
}