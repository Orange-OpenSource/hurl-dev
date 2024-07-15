document.getElementById("home-samples")
    .addEventListener("change", (event) => {
    const sampleId = event.target.value;
    const divSample = document.querySelector(".home-sample");
    const sample = document.querySelector("." + sampleId);
    divSample.innerHTML = sample.outerHTML;
});

AsciinemaPlayer.create('/assets/cast/starwars.cast', document.getElementById('home-demo'), {
    loop: true,
    speed: 3,
    theme: "asciinema",
    poster: "npt:00:56",
});
