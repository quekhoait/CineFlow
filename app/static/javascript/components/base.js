import {showAlert} from "../utils/alert.js";
import {loadHTML} from "../utils/load.js";
import {formatTime} from "../utils/format.js";

export async function getUser() {
    try {
        const res = await fetch('/api/user/profile', {
            method: 'GET',
            credentials: 'include',
        });
        const result = await res.json();
        if (res.status === 200) {
            return result;
        }
    } catch (error) {
        console.error("Profile Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
}

export async function getCinema() {
    try {
        const res = await fetch('/api/cinemas', {
            method: 'GET',
            credentials: 'include',
            headers: {'Content-Type': 'application/json'}
        });
        const result = await res.json();
        if (res.status === 200) {
            return result;
        }
    } catch (error) {
        console.error("Profile Error:", error);
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
}

export async function getFilm(query) {
    try {
        const res = await fetch(`/api/films/search?title=${query}`, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'},
        });
        const result = await res.json();
        if (res.status === 200) {
            return result;
        }
    } catch (error) {
        showAlert("error", "Error Connection", "Error Connection to CineFlow");
        return null;
    }
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
                // Kiểm tra nếu hết hạn thì thêm class opacity và disable
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

    // Hiển thị trạng thái đang tải (tùy chọn)
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

// searchLogic.js
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


