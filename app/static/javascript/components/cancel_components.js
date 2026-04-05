import {renderInvoice, getBookingByCode, getInfoUser} from "./payment_components.js";
import {showAlert} from "../utils/alert.js";
import {showError} from "../utils/load.js";

export async function initFlowCancel() {
    const code = sessionStorage.getItem('code');
    if (code) {
        const bookingData = await getBookingByCode();
        window.addEventListener('beforeunload', (event) => {
            sessionStorage.setItem('code', bookingData.code);
        });
        await renderInvoice(bookingData)
        await getInfoUser()
        const container = document.getElementById("info_film");
        const btnPayment = container.querySelector("#btn_payment");
        const btnCancel = container.querySelector("#btn_cancel");
        if (btnPayment) btnPayment.style.display = "none";
        if (btnCancel) btnCancel.classList.remove("hidden");
        document.getElementById('title-bill').innerText = "Số tiền hoàn trả"
        if (bookingData.payment_status === 'PENDING') document.getElementById('total_price').innerText = '0 VND'
        sessionStorage.removeItem('code')
    }
}

export async function cancelTicket(code) {
    if (code) {
        try {
            const res = await fetch(`/api/bookings/${code}/cancel`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
                },
            })

            if (res.ok) {
                showAlert('success', 'Cancel Ticket', 'Hủy vé thành công, Bạn chờ hoàn tiền')
            } else {
                showError('Cancel ticket', await res.json())
            }
        }
        catch (error) {
            console.error(error)
        }


    }
}