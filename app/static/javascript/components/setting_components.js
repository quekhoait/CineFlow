import {showAlert} from "../utils/alert.js";
import {showError} from "../utils/load.js";

export function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
        tab.classList.remove('block');
    });

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('bg-[#000]/10', 'text-[#000]');
        btn.classList.add('text-gray-800', 'hover:bg-gray-100');
    });

    document.getElementById(tabId).classList.remove('hidden');
    document.getElementById(tabId).classList.add('block');

    const activeBtn = document.querySelector(`.tab-btn[data-target="${tabId}"]`);
    activeBtn.classList.remove('text-gray-800', 'hover:bg-gray-100');
    activeBtn.classList.add('bg-[#000]/10', 'text-[#000]');
}

export function updateBtn() {
    const updateBtn = document.getElementById('updateBtn');
    updateBtn.addEventListener('click', () => {
        updateBtn.innerText = "Đang lưu ...";
        const payload = [
            {
                "name": "SINGLE_WEEKDAY",
                "value": document.getElementById('SINGLE_WEEKDAY').value
            },
            {
                "name": "COUPLE_WEEKDAY",
                "value": document.getElementById('COUPLE_WEEKDAY').value
            },
            {
                "name": "SINGLE_WEEKEND",
                "value": document.getElementById('SINGLE_WEEKEND').value
            },
            {
                "name": "COUPLE_WEEKEND",
                "value": document.getElementById('COUPLE_WEEKEND').value
            }
        ];

        fetch('/api/rules/update', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        }).then(res => res.json())
            .then(result => {
                console.log(result)
                if (result.status === "success") showAlert("success", "Update price", result.message)
                else showError("Update Price", result)
            }).catch(error => {
            console.error("Update error: ", error)
            showAlert("error", "Update Price", "Sever Error")
        }).finally(() => {
            updateBtn.innerText = "Cập nhập"
        })
    })
}

export function loadPriceSettings() {
    const payload = {
        "name": ["SINGLE_WEEKDAY", "COUPLE_WEEKDAY", "SINGLE_WEEKEND", "COUPLE_WEEKEND"]
    }
    fetch('/api/rules', {
        method: "GET",
    }).then(res => res.json())
        .then(result => {
            if (result.status === "success") {
                const priceMap = {};
                result.data.forEach(item => {
                    priceMap[item.name] = item.value;
                });
                payload.name.forEach(item => {
                    const inputElement = document.getElementById(item);
                    if (inputElement && priceMap[item] !== undefined) {
                        inputElement.value = parseInt(priceMap[item]);
                    }
                })
            } else {
                showError("Load Rules", result)
            }
        }).catch(error => {
            showAlert("error", "Load rules", "Sever Error")
            console.error("Server Error:", error)
    });
}