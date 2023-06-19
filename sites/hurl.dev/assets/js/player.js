function valid(value, regex, defaultValue) {
    if (value && regex.test(value)) {
        return value;
    } else {
        return defaultValue;
    }
}

function loadPlayer() {
    const queryString = location.search;
    if (!queryString) {
        return;
    }
    const params = new URLSearchParams(queryString);
    const id = valid(params.get("id"), /[a-z\d-]+/);
    if (!id) {
        return;
    }
    const cast = `/assets/cast/${id}.cast`;
    const speedStr = valid(params.get("speed"), /\d+/, "1");
    const speed = parseInt(speedStr);
    const posterStr = valid(params.get("poster"), /\d+:\d+/)
    let poster;
    if (posterStr) {
        poster = `npt:${posterStr}`;
    }


    AsciinemaPlayer.create(cast, document.getElementById("player"), {
        autoplay: true,
        loop: true,
        speed: speed,
        theme: "asciinema",
        poster: poster,
    });
}

loadPlayer();