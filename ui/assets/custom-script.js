function set_listener() {
    let url_input = document.querySelector("#url-input");
    let header = document.querySelector("#header");
    let content = document.querySelector("#content");

    if(url_input != null && header != null && content != null) {
        clearInterval(refreshID);

        document.addEventListener("dragenter", () => {
            url_input.classList.toggle("expand");
            header.classList.toggle("hide");
            content.classList.toggle("hide");
        });

        document.addEventListener("dragleave", () => {
            url_input.classList.toggle("expand");
            header.classList.toggle("hide");
            content.classList.toggle("hide");
        });

        url_input.addEventListener("input", () => {
            url_input.classList.toggle("expand");
            header.classList.toggle("hide");
            content.classList.toggle("hide");
        });
    }
}

// call this function every 250 ms
let refreshID = setInterval(set_listener, 250);