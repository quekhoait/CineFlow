import {loadHTML} from "../utils/load.js";
import {formatDate, formatTime} from "../utils/format.js";
import {showAlert} from "../utils/alert.js";
import {getCinema, renderScheduleData} from "./base.js";

let selectedBranchId = 1;


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
                .replace('{{label}}', item.label)
                .replace('{{date}}', item.date)
                .replace('{{date_time}}', item.date);
        }).join('');

        const containers = [
            document.getElementById('date_picker'),
            document.getElementById('date_film')
        ];

        containers.forEach(container => {
            if (container) {
                container.innerHTML = htmlContent;
                const firstBtn = container.querySelector('.date-item');
                if (firstBtn) {
                    firstBtn.classList.add('bg-[#3d55a4]', 'text-white', 'border-red-800');
                    firstBtn.classList.remove('bg-[#41414133]', 'text-black');
                }
            }
        });
    } catch (error) {
        console.error("Lỗi khi tải template date:", error);
    }
}

export async function loadBranch() {
    const templateDoc = await loadHTML("/templates/components/schedule/branch.html");
    const branchTemplate = templateDoc.body.innerHTML;
           const result = await getCinema()
            if (result.data && result.data.length > 0) {
                const htmlContent = result.data.map(city => {
                    const buttonsHtml = city.location.map(item => `
                        <button onclick="handleSelectBranch(this, '${item.id}')" 
                                class="btn-branch w-full text-left px-4 py-2 rounded-xl bg-white border border-gray-100  transition-colors shadow-sm text-sm">
                            ${item.name}
                        </button>
                    `).join('');
                    return branchTemplate
                        .replace('{{province}}', city.province)
                        .replace('{{branches}}', buttonsHtml);
                }).join('');

                const container = document.getElementById("branch_location");
                if (container) {
                    container.innerHTML = htmlContent;
                    const firstBtn = container.querySelector('.btn-branch');
                    if (firstBtn) {
                        firstBtn.classList.add('bg-[#3d55a4]', 'text-white', 'border-red-800');
                        firstBtn.classList.remove('bg-white', 'bg-[#3d55a4]');
                        const firstBranchId = result.data[0].location[0].id;
                        handleSelectBranch(firstBtn, firstBranchId);
                    }
                }

            } else {
                let errorDetail = result.message || "Không có dữ liệu chi nhánh";
                showAlert("error", "Lỗi dữ liệu", errorDetail);
            }
}

export async function loadFilm() {
    const selectedDate = sessionStorage.getItem('selected_date');
    // Lưu ý: Đảm bảo selectedBranchId đã được định nghĩa ở đâu đó trong scope của bạn
    if (!selectedDate || !selectedBranchId) return;

    await renderScheduleData({
        apiUrl: `/api/cinemas/${selectedBranchId}/films?date=${selectedDate}`,
        containerId: "schedule-film",
        templateUrl: "/templates/components/schedule/film.html",
        mapper: (template, film, buttonsHtml) => {
            return template
                .replace('{{poster}}', film.poster)
                .replace('{{title}}', film.title)
                .replace('{{duration}}', film.duration)
                .replace('{{genre}}', film.genre)
                .replace("{{age_limit}}", film.age_limit)
                .replace('{{show_time}}', buttonsHtml);
        }
    });
}



function renderAddress(cinema_name, address) {
    return `
        <p class="font-bold text-black text-lg">${cinema_name}</p>
        <p class="text-sm text-gray-700">${address}</p>
    `
}

export function handleSelectBranch(element, id) {
    selectedBranchId = id;
    document.querySelectorAll('.btn-branch').forEach(btn => {
        btn.classList.remove('bg-[#3d55a4]', 'text-white');
        btn.classList.add('bg-white', 'text-gray-800');
    });
    if (element) {
        element.classList.remove('bg-white', 'text-gray-800');
        element.classList.add('bg-[#3d55a4]', 'text-white');
    }
    fetch(`/api/cinemas/${id}`)
        .then(res => res.json())
        .then(res => {
            if (res.status === "success") {
                document.getElementById("address_cinema").innerHTML = renderAddress(res.data.name, res.data.address)
            } else {
                console.error("Lỗi API:", res.message);
            }
        })
    loadFilm()
}

export function handleSelectDate(element, date) {
    document.querySelectorAll('.date-item').forEach(btn => {
        btn.classList.remove('bg-[#3d55a4]', 'text-white');
        btn.classList.add('bg-[#41414133]', 'text-black');
    });
    if (element) {
        element.classList.remove('bg-[#41414133]', 'text-black');
        element.classList.add('bg-[#3d55a4]', 'text-white');
    }
    sessionStorage.setItem('selected_date', date)
    loadFilm();
}