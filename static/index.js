window.addEventListener("DOMContentLoaded", function () {
    const textarea = this.document.getElementsByTagName("textarea")[0];
    const history = this.document.getElementById("history");

    const accepted = [...'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890+- ', 'Enter', 'Backspace'];

    textarea.addEventListener("keydown", function (ev) {
        if (accepted.indexOf(ev.key) == -1) ev.preventDefault();
        if (ev.key != "Enter" || textarea.value.trim() == "") return;
        ev.preventDefault();

        let line = document.createElement("div");
        line.textContent = textarea.value.trim();
        line.className = "line";

        fetch("/process/" + encodeURIComponent(line.textContent)).then(async function (response) {
            if (!response.ok) {
                line.textContent += " = NetworkError!";
                return;
            }

            line.textContent += await response.text();
        });

        if (history.children.length > 0) {
            history.insertBefore(line, history.children[0]);
        }
        else {
            history.appendChild(line);
        }

        history.scrollTop = 0;

        textarea.value = "";
    })
})