import {loadHTML} from "../utils/load.js";

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
                    .replace('{{content}}', strategy === 'showing'? movie.release_date : 'Xem chi tiết')
                    .replace('{{flag}}', strategy === 'showing' ? '<span class="text-white text-sm font-medium">Khởi chiếu</span>' : '')

                html += cardHtml;
                });
                container.innerHTML = html;
        })
        .catch(err => console.error(`Lỗi khi load ${strategy}:`, err));
}