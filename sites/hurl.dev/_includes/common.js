addEventListener("load", onLoad);

function toggleElem() {
    return document.getElementById("theme-toggle");
}

function menuElem() {
    return document.getElementById("menu");
}


function onLoad() {
    const systemInitiatedDark = window.matchMedia("(prefers-color-scheme: dark)");
    const defaultTheme = systemInitiatedDark.matches ? "dark" : "light";

    // This checks for local storage telling to override the system preferences
    let currentTheme = localStorage.getItem("theme");
    if (!currentTheme) {
        currentTheme = defaultTheme;
    }

    setTheme(currentTheme);

    toggleElem().addEventListener("click", onThemeClick);
    menuElem().addEventListener("click", onMenuClick);
    systemInitiatedDark.addEventListener("change", onPreferColorSchemeChange);
}

function setTheme(theme) {
    const lightElem = "<span class=\"svg-icon\"><svg viewBox=\"0 0 512 512\" width=\"18\" height=\"18\"><use href=\"#sun\"></use></svg>&nbsp;</span><span class=\"u-underline\">Theme</span>";
    const darkElem = "<span class=\"svg-icon\"><svg viewBox=\"0 0 512 512\" width=\"18\" height=\"18\"><use href=\"#moon\"></use></svg>&nbsp;</span><span class=\"u-underline\">Theme</span>";
    document.documentElement.setAttribute("data-theme", theme);
    if (theme === "dark") {
        toggleElem().innerHTML = lightElem;
    }
    else {
        toggleElem().innerHTML = darkElem;
    }
    localStorage.setItem("theme", theme);
}

function onMenuClick() {
    const x = document.getElementById("top-nav-toc");
    if (x.style.display !== "block") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function onPreferColorSchemeChange(e) {
    if (e.matches) {
        setTheme("dark");
    } else {
        setTheme("light");
    }
}

function onThemeClick() {
    const currentTheme = localStorage.getItem("theme");
    if (currentTheme === "dark") {
        setTheme("light");
    } else if (currentTheme === "light") {
        setTheme("dark");
    } else {
        setTheme("light");
    }
}
