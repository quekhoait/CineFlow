// Animation header
export function headerScroll(scrollId = 'master-scroll', headerId = 'header') {
    const container = document.getElementById(scrollId);
    const header = document.getElementById(headerId)
    if (!container || !header) return;
    container.addEventListener('scroll', function() {
        if (container.scrollTop > 50) {
            header.classList.remove("py-3");
            header.classList.add('shadow-[0px_3px_8px_rgba(0,0,0,0.24)]', "py-2.5");
        } else {
            header.classList.remove('shadow-[0px_3px_8px_rgba(0,0,0,0.24)]', "py-2.5");
            header.classList.add("py-3");
        }
    })
}

// Animation active nav
export function navActive(attribute='href', value= window.location.pathname,  cls='.nav-item', warp=false) {
    const items = document.querySelector(cls)
    items.forEach(item => {
        if (item.getAttribute(attribute) === value) {
            (warp) && item.classList.add('')
        } else {
            item.classList.add()
        }
    })
}