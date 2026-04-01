import * as animation from "../utils/animation.js";
import * as userComponents from "../components/user_components.js"

document.addEventListener('DOMContentLoaded', function () {
    animation.headerScroll();
    window.scrollSlider = animation.scrollSlider;

    userComponents.translateMode();
    userComponents.appearAuth()


})