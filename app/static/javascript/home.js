function scrollSlider(sliderId, distance) {
console.log(2)
        const slider = document.getElementById(sliderId);
        if (slider) {
            slider.scrollBy({
                left: distance,
                behavior: 'smooth' // Cuộn mượt mà
            });
        }
    }