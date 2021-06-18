function toggleMenu() {
    const x = document.getElementById("top-nav-toc");
    if (x.style.display !== "block") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}


// Dark mode switcher
// Courtesy of https://derekkedziora.com/blog/dark-mode-revisited
// Source code from: https://github.com/derekkedziora/jekyll-demo

const lightElem = "<i class='fas fa-sun'></i> Theme";
const darkElem = "<i class='fas fa-moon'></i> Theme";


// This checks whether system dark mode is set
const systemInitiatedDark = window.matchMedia("(prefers-color-scheme: dark)");
// this checks for session storage telling to override
// the system preferences
const theme = sessionStorage.getItem('theme');


if (systemInitiatedDark.matches) {
    document.getElementById("theme-toggle").innerHTML = lightElem;
} else {
    document.getElementById("theme-toggle").innerHTML = darkElem;
}

// Detect if the system preferences change.
// Changes the site to match the system preferences.
function prefersColorTest(e) {
    if (e.matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
        document.getElementById("theme-toggle").innerHTML = lightElem;
        // this clears the session storage
        sessionStorage.setItem('theme', '');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        document.getElementById("theme-toggle").innerHTML = darkElem;
        sessionStorage.setItem('theme', '');
    }
}
systemInitiatedDark.addListener(prefersColorTest);

function modeSwitcher() {
    // It’s important to check for overrides again
    let currentTheme = sessionStorage.getItem('theme');
    // Checks if reader selected dark mode
    if (currentTheme === "dark") {
        document.documentElement.setAttribute('data-theme', 'light');
        sessionStorage.setItem('theme', 'light');
        document.getElementById("theme-toggle").innerHTML = darkElem;
        // checks if reader selected light mode
    }   else if (currentTheme === "light") {
        document.documentElement.setAttribute('data-theme', 'dark');
        sessionStorage.setItem('theme', 'dark');
        document.getElementById("theme-toggle").innerHTML = lightElem;
        // checks if system set dark mode
    } else if (systemInitiatedDark.matches) {
        document.documentElement.setAttribute('data-theme', 'light');
        sessionStorage.setItem('theme', 'light');
        document.getElementById("theme-toggle").innerHTML = darkElem;
        // the only option left is system set light mode
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        sessionStorage.setItem('theme', 'dark');
        document.getElementById("theme-toggle").innerHTML = lightElem;
    }
}

if (theme === "dark") {
    document.documentElement.setAttribute('data-theme', 'dark');
    sessionStorage.setItem('theme', 'dark');
    document.getElementById("theme-toggle").innerHTML = lightElem;
} else if (theme === "light") {
    document.documentElement.setAttribute('data-theme', 'light');
    sessionStorage.setItem('theme', 'light');
    document.getElementById("theme-toggle").innerHTML = darkElem;
}