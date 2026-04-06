import {initFlowCancel, cancelTicket} from "../components/cancel_components.js";

document.addEventListener('DOMContentLoaded', async () => {
    await initFlowCancel()
    window.cancelTicket = cancelTicket
})