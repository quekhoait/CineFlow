import { loadHTML } from "../utils/load.js";
import { showAlert } from "../utils/alert.js";
import { getCinema, renderScheduleData } from "./base.js";
import fetchAPI from "../utils/apiClient.js";

let selectedBranchId = null;

export async function loadDate() {
    try {
        const doc = await loadHTML("/templates/components/schedule/nav_date.html");
        const nav_date = doc.body.innerHTML;
        const days = ["Chủ nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"];
        const today = new Date();
        const dateData = [];

        for (let i = 0; i < 7; i++) {
            const nextDate = new Date(today);
            nextDate.setDate(today.getDate() + i);
            const dateString = `${nextDate.getFullYear()}-${String(nextDate.getMonth() + 1).padStart(2, '0')}-${String(nextDate.getDate()).padStart(2, '0')}`;
            const dayLabel = (i === 0) ? "Hôm nay" : days[nextDate.getDay()];

            dateData.push({
                label: dayLabel,
                date: dateString,
            });
        }

        const htmlContent = dateData.map(item => {
            return nav_date
                .replace(/{{label}}/g, item.label)
                .replace(/{{date}}/g, item.date)
                .replace(/{{date_time}}/g, item.date);
        }).join('');

        const containers = [
            document.getElementById('date_picker'),
            document.getElementById('date_film')
        ];

        let defaultDateSet = false;

        containers.forEach(container => {
            if (container) {
                container.innerHTML = htmlContent;
                const firstBtn = container.querySelector('.date-item');
                if (firstBtn) {
                    firstBtn.classList.add('bg-[#3d55a4]', 'text-white', 'border-red-800');
                    firstBtn.classList.remove('bg-[#41414133]', 'text-black');

                    if (!defaultDateSet) {
                        const dateVal = dateData[0].date;
                        if (!sessionStorage.getItem('selected_date')) {
                            sessionStorage.setItem('selected_date', dateVal);
                        }
                        defaultDateSet = true;
                    }
                }
            }
        });
    } catch (error) {
        console.error("Lỗi khi tải template date:", error);
    }
}

export async function loadBranch() {
    try {
        const templateDoc = await loadHTML("/templates/components/schedule/branch.html");
        const branchTemplate = templateDoc.body.innerHTML;
        const result = await getCinema();

        if (result && result.data && result.data.length > 0) {
            const htmlContent = result.data.map(city => {
                const buttonsHtml = city.location.map(item => `
                    <button onclick="window.handleSelectBranch(this, '${item.id}')" 
                            class="btn-branch w-full text-left px-4 py-2 rounded-xl bg-white border border-gray-100 transition-colors shadow-sm text-sm">
                        ${item.name}
                    </button>
                `).join('');

                return branchTemplate
                    .replace(/{{province}}/g, city.province)
                    .replace(/{{branches}}/g, buttonsHtml);
            }).join('');

            const container = document.getElementById("branch_location");
            if (container) {
                container.innerHTML = htmlContent;
                const firstBtn = container.querySelector('.btn-branch');
                if (firstBtn) {
                    const firstBranchId = result.data[0].location[0].id;
                    window.handleSelectBranch(firstBtn, firstBranchId);
                }
            }
        } else {
            let errorDetail = result?.message || "Không có dữ liệu chi nhánh";
            showAlert("error", "Lỗi dữ liệu", errorDetail);
        }
    } catch (error) {
        console.error("Lỗi khi tải branch:", error);
    }
}

export async function loadFilm() {
    const selectedDate = sessionStorage.getItem('selected_date');
    if (!selectedDate || !selectedBranchId) return;

    await renderScheduleData({
        apiUrl: `/api/cinemas/${selectedBranchId}/films?date=${selectedDate}`,
        containerId: "schedule-film",
        templateUrl: "/templates/components/schedule/film.html",
        mapper: (template, film, buttonsHtml) => {
            return template
                .replace(/{{poster}}/g, film.poster || '')
                .replace(/{{title}}/g, film.title || '')
                .replace(/{{duration}}/g, film.duration || '')
                .replace(/{{genre}}/g, film.genre || '')
                .replace(/{{age_limit}}/g, film.age_limit || '')
                .replace(/{{show_time}}/g, buttonsHtml || '');
        }
    });
}

function renderAddress(cinema_name, address) {
    return `
        <p class="font-bold text-black text-lg">${cinema_name || ''}</p>
        <p class="text-sm text-gray-700">${address || ''}</p>
    `;
}

window.handleSelectBranch = async function (element, id) {
    selectedBranchId = id;

    document.querySelectorAll('.btn-branch').forEach(btn => {
        btn.classList.remove('bg-[#3d55a4]', 'text-white');
        btn.classList.add('bg-white', 'text-gray-800');
    });

    if (element) {
        element.classList.remove('bg-white', 'text-gray-800');
        element.classList.add('bg-[#3d55a4]', 'text-white');
    }

    try {
        const res = await fetchAPI(`/api/cinemas/${id}`, { method: 'GET' });

        if (res.ok && res.data?.status === "success") {
            const cinemaData = res.data.data || res.data;
            const addrContainer = document.getElementById("address_cinema");
            if (addrContainer) {
                addrContainer.innerHTML = renderAddress(cinemaData.name, cinemaData.address);
            }
        } else {
            console.error("Lỗi API:", res.data?.message);
        }
    } catch (error) {
        console.error("Lỗi khi lấy thông tin rạp:", error);
    }

    loadFilm();
};

window.handleSelectDate = function (element, date) {
    document.querySelectorAll('.date-item').forEach(btn => {
        btn.classList.remove('bg-[#3d55a4]', 'text-white');
        btn.classList.add('bg-[#41414133]', 'text-black');
    });

    if (element) {
        element.classList.remove('bg-[#41414133]', 'text-black');
        element.classList.add('bg-[#3d55a4]', 'text-white');
    }

    sessionStorage.setItem('selected_date', date);
    loadFilm();
};

export const handleSelectBranch = window.handleSelectBranch;
export const handleSelectDate = window.handleSelectDate;