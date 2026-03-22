function scrollSlider(sliderId, distance) {
        const slider = document.getElementById(sliderId);
        if (slider) {
            slider.scrollBy({
                left: distance,
                behavior: 'smooth'
            });
        }
    }