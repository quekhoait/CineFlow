import * as animation from "../utils/animation.js";
import * as userComponents from "../components/user_components.js"

document.addEventListener('DOMContentLoaded', function () {
    animation.headerScroll();
    userComponents.appearAuth()
    userComponents.updateMasterCard()
    window.scrollSlider = animation.scrollSlider;
})