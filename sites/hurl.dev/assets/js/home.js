document.getElementById("home-samples").addEventListener("change", (event) => selectSample(event.target.value));

function selectSample(sampleId) {
    const divSample = document.querySelector(".home-sample");
    const sample = document.querySelector("." + sampleId);
    divSample.innerHTML = sample.outerHTML;
}

AsciinemaPlayer.create('/assets/cast/hurl.cast', document.getElementById('home-demo'), {
    loop: true,
    speed: 3,
    theme: "asciinema",
    poster: "npt:1:00",
});
