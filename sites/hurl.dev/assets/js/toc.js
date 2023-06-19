// Toc switcher
let toc; // A map of toc entry - target
let visibleLinks = new Set(); // Set of actives nodes
let lastVisibleLink;   // Last visibles links.

function buildToc() {
    const lis = document.querySelectorAll(".doc-toc li");
    const map = new Map();
    [...lis].forEach(link => {
        const a = link.querySelector("a");
        const href = a.getAttribute("href");
        const match = href.match(/^.*(#.*)$/);
        const targetId = match[1];
        const target = document.querySelector(targetId);
        map.set(target, link);
    });
    return map;
}

function addClass(el, value) {
    if (el && !el.classList.contains(value)) {
        el.classList.add(value);
    }
}

function onIntersect(entries) {
    entries.forEach((entry) => {
        const target = entry.target;
        const link = toc.get(target);
        if (entry.isIntersecting && entry.intersectionRatio === 1.0) {
            visibleLinks.add(link);
        } else {
            if (visibleLinks.size === 1) {
                lastVisibleLink = link;
            }
            visibleLinks.delete(link);
        }
    });
    highlightVisible();
}

function highlightVisible() {
    const links = [...toc.values()];
    const firstVisibleLink = links.find(link => visibleLinks.has(link));
    links.forEach(link => link.classList.remove("visible"));
    if (firstVisibleLink) {
        addClass(firstVisibleLink, "visible");
    } else {
        addClass(lastVisibleLink, "visible");
    }
}

function loadScrollObserver() {
    let options = {
        root: null,
        rootMargin: "-64px 0px 0px 0px",
        threshold: 1.0
    };
    let observer = new IntersectionObserver(onIntersect, options);
    for (const target of toc.keys()) {
        observer.observe(target);
    }
}

function changeTocUrl(url) {
    location = url;
}

if(!!window.IntersectionObserver) {
    window.addEventListener("load", () => {
        toc = buildToc();
        loadScrollObserver();
    });
}

window.addEventListener("load", () => {
    const elt = document.querySelector(".doc-picker >  select");
    if (!elt) {
        return;
    }
    elt.addEventListener("change", (event) => changeTocUrl(event.target.value));
})

