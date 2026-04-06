import * as animation from "../utils/animation.js";
import * as userComponents from "../components/user_components.js"
import * as baseComponents from "../components/base.js"

document.addEventListener('DOMContentLoaded', function () {
    animation.headerScroll();
    userComponents.appearAuth()
    userComponents.updateMasterCard()

    window.scrollSlider = animation.scrollSlider;
    window.getUser = baseComponents.getUser
    window.getUser = baseComponents.getCinema
})