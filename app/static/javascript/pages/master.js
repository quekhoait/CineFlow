import * as animation from "../utils/animation.js";
import * as userComponents from "../components/user_components.js"
import * as baseComponents from "../components/base.js"
import {notifyError} from "../utils/alert.js";
import {formatDate} from "../utils/format.js";



document.addEventListener('DOMContentLoaded', function () {
    notifyError()
    animation.headerScroll();
    userComponents.appearAuth()
    userComponents.updateMasterCard()

    window.scrollSlider = animation.scrollSlider;
    window.getUser = baseComponents.getUser
    window.getUser = baseComponents.getCinema

    sessionStorage.setItem("selected_date", formatDate(new Date()))

const searchInput = document.getElementById('master-search');

    if (searchInput) {
        const urlParams = new URLSearchParams(window.location.search);
        const queryFromUrl = urlParams.get('q');
        const isFilmPage = window.location.pathname.includes('/film');
        if (queryFromUrl) {
            searchInput.value = queryFromUrl;
            if (isFilmPage) {
                setTimeout(async () => {
                await baseComponents.performSearch(queryFromUrl);
            }, 100);
            }
        }

        if (isFilmPage) {
            baseComponents.handleAutoSearch(searchInput, (query) => {
                baseComponents.performSearch(query);
            });
        } else {
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    const query = searchInput.value.trim();
                    if (query) {
                        baseComponents.performSearch(query);
                    }
                }
            });
        }
    }

})