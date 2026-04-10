import {showAlert} from "../utils/alert.js";
import {loadHTML} from "../utils/load.js";
import {formatTime} from "../utils/format.js";

export async function getUser() {
    try {
        const res = await fetch('/api/user/profile', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            },
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
        if (result.data && result.data.length > 0) {
            const htmlContent = result.data.map(item => {
                const buttonsHtml = item.schedule.map(slot => `
                    <button onclick="handleSelectShow('${slot.id}')" 
                            class="bg-white border border-gray-100 py-2 rounded-xl text-xs font-bold text-[#3d55a4] hover:!bg-[#3d55a4] hover:!text-white transition-all shadow-sm">
                        ${formatTime(slot.start_time)}
                    </button>
                `).join('');
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