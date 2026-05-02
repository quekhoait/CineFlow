import {loadHTML} from "../utils/load.js";
import {formatTime} from "../utils/format.js";
import { showAlert } from "../utils/alert.js";
import fetchAPI from "../utils/apiClient.js";

export async function getUser() {
    const response = await fetchAPI('/api/user/profile', { method: 'GET' });
    if (response.ok) return response.data;
    return null;
}

export async function getCinema() {
    const response = await fetchAPI('/api/cinemas', { method: 'GET' });
    if (response.ok) return response.data;
    return null;
}

export async function getFilm(query) {
    const response = await fetchAPI(`/api/films/search?title=${query}`, { method: 'GET' });
    if (response.ok) return response.data;
    return null;
}

export async function renderScheduleData({ apiUrl, containerId, templateUrl, mapper }) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
        const [templateDoc, res] = await Promise.all([
            loadHTML(templateUrl),
            fetch(apiUrl, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            })
        ]);

        if (res.status !== 200) {
            const errorData = await res.json();
            throw new Error(errorData.message || "Lỗi hệ thống");
        }
        const branchTemplate = templateDoc.body.innerHTML;
        const result = await res.json();
        console.log(result.data)
        if (result.data && result.data.length > 0) {
          const htmlContent = result.data.map(item => {
            const buttonsHtml = item.schedule.map(slot => {
                const expiredClass = !slot.is_expired
                    ? "opacity-40 cursor-not-allowed pointer-events-none grayscale-[0.5]"
                    : "hover:!bg-[#3d55a4] hover:!text-white shadow-sm cursor-pointer";

                // Kiểm tra nếu hết hạn thì không cho gọi hàm handleSelectShow
                const onClickAction = !slot.is_expired
                    ? ""
                    : `onclick="handleSelectShow('${slot.id}')"`;

                return `
                    <button ${onClickAction} 
                            class="bg-white border border-gray-100 py-2 rounded-xl text-xs font-bold text-[#3d55a4] transition-all ${expiredClass}">
                        ${formatTime(slot.start_time)}
                    
                    </button>
                `;
            }).join('');

            return mapper(branchTemplate, item, buttonsHtml);
        }).join('');

            container.innerHTML = htmlContent;
        } else {
            container.innerHTML = `
                <div class="col-span-full text-center py-10">
                    <p class="text-gray-800 italic">Hiện tại không có suất chiếu nào cho ngày đã chọn.</p>
                </div>`;
        }
    } catch (error) {
        console.error("Render Error:", error);
        showAlert("error", error.name === 'Error' ? "Lỗi hệ thống" : "Lỗi kết nối", error.message || "Không thể kết nối đến máy chủ");
    }
}

export async function renderFilm(query) {
    const container = document.getElementById('list_film');
    if (!container) return;

    container.innerHTML = '<p class="loading">Đang tìm kiếm phim...</p>';

    const doc = await loadHTML("/templates/components/card_film.html");
    const card = doc.body.innerHTML;
    const res = await getFilm(query);
    if (!res?.data || res?.data.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <p>Không tìm thấy phim nào phù hợp với từ khóa "${query}"</p>
            </div>`;
        return;
    }

    let html = '';
    res.data.forEach(movie => {
        let cardHtml = card
            .replace('{{poster}}', movie.poster)
            .replace('{{content}}', "Xem chi tiết")
            .replace('{{id}}', movie.id);
        html += cardHtml;
    });

    container.innerHTML = html;
}

export async function performSearch(query) {
    if (!query) return;
    const isFilmPage = window.location.pathname.includes('/film');

    if (isFilmPage) {
        renderFilm(query)

    } else {
        window.location.href = `/film?q=${encodeURIComponent(query)}`;
    }

}

export function handleAutoSearch(inputElement, callback) {
    let typingTimer;
    const interval = 500;

    inputElement.addEventListener('keyup', () => {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            callback(inputElement.value.trim());
        }, interval);
    });
}


