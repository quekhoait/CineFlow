export function showAlert(type, title, message) {
    const alertBox = document.getElementById("form_alert");
    const iconBox = document.getElementById("alert_icon");
    const textBox = document.getElementById("alert_text");
    const closeBtn = document.getElementById("alert_close");

    if (!alertBox || !iconBox || !textBox) return;

    alertBox.classList.remove(
        "bg-green-50", "border-green-300", "text-green-800",
        "bg-red-50", "border-red-300", "text-red-800",
        "bg-orange-50", "border-orange-300", "text-orange-800",
        "bg-blue-50", "border-blue-300", "text-blue-800"
    );

    iconBox.innerHTML = "";
    textBox.innerHTML = "";

    let bg = "", border = "", txt = "", icon = "";

    switch (type) {
        case "success":
            bg = "bg-green-50";
            border = "border-green-300";
            txt = "text-green-800";
            icon = `<i class="fas fa-check-circle text-green-500 text-2xl"></i>`;
            break;

        case "error":
            bg = "bg-red-50";
            border = "border-red-300";
            txt = "text-red-800";
            icon = `<i class="fas fa-times-circle text-red-500 text-2xl"></i>`;
            break;

        case "loading":
            bg = "bg-blue-50";
            border = "border-blue-300";
            txt = "text-blue-800";
            icon = `<i class="fas fa-spinner fa-spin text-blue-500 text-2xl"></i>`;
            break;

        default: // warning
            bg = "bg-orange-50";
            border = "border-orange-300";
            txt = "text-orange-800";
            icon = `<i class="fas fa-exclamation-triangle text-orange-500 text-2xl"></i>`;
    }

    iconBox.innerHTML = icon;
    textBox.innerHTML = `
       <p class="font-bold mb-1">${title}</p>
       <p>${message}</p>
    `;

    alertBox.classList.add(bg, border, txt);
    alertBox.classList.remove("hidden");
    alertBox.style.opacity = "0";
    alertBox.style.transform = "translateX(15px)";

    setTimeout(() => {
        alertBox.style.transition = "0.3s ease";
        alertBox.style.opacity = "1";
        alertBox.style.transform = "translateX(0)";
    }, 10);

    if (closeBtn) {
        closeBtn.onclick = () => hideAlert();
    }

    (type !== "loading") && setTimeout(() => {
        hideAlert();
    }, 5000)
}

export function hideAlert() {
    const alertBox = document.getElementById("form_alert");
    if (!alertBox) return;

    alertBox.style.opacity = "0";
    alertBox.style.transform = "translateX(15px)";

    setTimeout(() => {
        alertBox.classList.add("hidden");
    }, 300);
}