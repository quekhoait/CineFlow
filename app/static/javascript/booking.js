document.addEventListener("DOMContentLoaded", () => {
    const nav = document.getElementById("booking-nav");
    const block_move = document.getElementById("nav-booking-move");
    const items = nav.querySelectorAll(".nav-item");
    function updateActiveTab(element) {
        if (!element) return;
        const left = element.offsetLeft;
        const width = element.offsetWidth;
        block_move.style.left = `${left}px`;
        block_move.style.width = `${width}px`;
        items.forEach(item => {
            item.classList.remove("text-gray-800", "font-medium");
            item.classList.add("text-gray-500");
        });
        element.classList.remove("text-gray-500");
        element.classList.add("text-gray-800", "font-medium");
    }
    items.forEach(item => {
        item.addEventListener("click", function() {
            updateActiveTab(this);
        });
    });
});