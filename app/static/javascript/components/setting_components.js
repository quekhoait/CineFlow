import { showAlert } from "../utils/alert.js";
import { showError } from "../utils/load.js";
import fetchAPI from "../utils/apiClient.js";

export function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
        tab.classList.remove('block');
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-[#000]/10', 'text-[#000]');
        btn.classList.add('text-gray-800', 'hover:bg-gray-100');
    });

    const targetTab = document.getElementById(tabId);
    if (targetTab) {
        targetTab.classList.remove('hidden');
        targetTab.classList.add('block');
    }

    const activeBtn = document.querySelector(`.tab-btn[data-target="${tabId}"]`);
    if (activeBtn) {
        activeBtn.classList.remove('text-gray-800', 'hover:bg-gray-100');
        activeBtn.classList.add('bg-[#000]/10', 'text-[#000]');
    }
}

export function updateBtn() {
    const btn = document.getElementById('updateBtn');
    if (!btn) return;

    btn.onclick = async () => {
        btn.innerText = "Đang lưu ...";
        btn.disabled = true;

        const keys = ["SINGLE_WEEKDAY", "COUPLE_WEEKDAY", "SINGLE_WEEKEND", "COUPLE_WEEKEND"];
        const payload = [];

        keys.forEach(key => {
            const input = document.getElementById(key);
            if (input) {
                payload.push({ name: key, value: input.value });
            }
        });

        try {
            const res = await fetchAPI('/api/rules/update', {
                method: 'PATCH',
                body: JSON.stringify(payload)
            });

            if (res.ok && res.data?.status === "success") {
                showAlert("success", "Update price", res.data.message || "Cập nhật thành công");
            } else {
                showError("Update Price", res.data);
            }
        } catch (error) {
            console.error("Update error: ", error);
            showAlert("error", "Update Price", "Server Error");
        } finally {
            btn.innerText = "Cập nhập";
            btn.disabled = false;
        }
    };
}

export async function loadPriceSettings() {
    const keys = ["SINGLE_WEEKDAY", "COUPLE_WEEKDAY", "SINGLE_WEEKEND", "COUPLE_WEEKEND"];

    try {
        const res = await fetchAPI('/api/rules', { method: "GET" });

        if (res.ok && res.data?.status === "success") {
            const priceMap = {};
            const rulesData = res.data.data || [];

            rulesData.forEach(item => {
                priceMap[item.name] = item.value;
            });

            keys.forEach(key => {
                const inputElement = document.getElementById(key);
                if (inputElement && priceMap[key] !== undefined) {
                    inputElement.value = parseInt(priceMap[key]);
                }
            });
        } else {
            showError("Load Rules", res.data);
        }
    } catch (error) {
        showAlert("error", "Load rules", "Server Error");
        console.error("Server Error:", error);
    }
}