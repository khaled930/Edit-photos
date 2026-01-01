document.addEventListener("DOMContentLoaded", () => {

    /* ================= Popup Control ================= */
    window.openPopup = function (id) {
        closePopup();
        document.getElementById(id).style.display = "block";
    };

    window.closePopup = function () {
        document.querySelectorAll(".popup").forEach(p => {
            p.style.display = "none";
        });
    };


    /* ================= Crop Elements ================= */
    const cropBox = document.getElementById("crop-box");
    const img = document.getElementById("image");

    let startX = 0, startY = 0;
    let box = {};
    let mode = "move";
    const MIN_SIZE = 40;


    /* ================= Enable Crop ================= */
    window.enableCrop = function () {
        if (!img.complete) return;

        cropBox.style.display = "block";
        cropBox.style.left = "40px";
        cropBox.style.top = "40px";
        cropBox.style.width = "200px";
        cropBox.style.height = "150px";
    };


    /* ================= Helpers ================= */
    function getPoint(e) {
        if (e.touches) {
            return {
                x: e.touches[0].clientX,
                y: e.touches[0].clientY
            };
        }
        return { x: e.clientX, y: e.clientY };
    }

    function clamp(val, min, max) {
        return Math.max(min, Math.min(max, val));
    }


    /* ================= Start Drag ================= */
    function start(e) {
        e.preventDefault();
        e.stopPropagation();

        const point = getPoint(e);

        mode = e.target.classList.contains("handle")
            ? e.target.classList[1]
            : "move";

        startX = point.x;
        startY = point.y;

        box = {
            x: cropBox.offsetLeft,
            y: cropBox.offsetTop,
            w: cropBox.offsetWidth,
            h: cropBox.offsetHeight
        };

        document.addEventListener("mousemove", move);
        document.addEventListener("mouseup", stop);
        document.addEventListener("touchmove", move, { passive: false });
        document.addEventListener("touchend", stop);
    }


    /* ================= Move / Resize ================= */
    function move(e) {
        e.preventDefault();
        const point = getPoint(e);

        let dx = point.x - startX;
        let dy = point.y - startY;

        const imgRect = img.getBoundingClientRect();

        let x = box.x;
        let y = box.y;
        let w = box.w;
        let h = box.h;

        if (mode === "move") {
            x += dx;
            y += dy;
        }

        if (mode.includes("r")) w = Math.max(MIN_SIZE, box.w + dx);
        if (mode.includes("l")) {
            w = Math.max(MIN_SIZE, box.w - dx);
            x = box.x + dx;
        }

        if (mode.includes("b")) h = Math.max(MIN_SIZE, box.h + dy);
        if (mode.includes("t")) {
            h = Math.max(MIN_SIZE, box.h - dy);
            y = box.y + dy;
        }

        /* ===== Keep inside image ===== */
        x = clamp(x, 0, imgRect.width - w);
        y = clamp(y, 0, imgRect.height - h);

        cropBox.style.left = x + "px";
        cropBox.style.top = y + "px";
        cropBox.style.width = w + "px";
        cropBox.style.height = h + "px";
    }


    /* ================= Stop ================= */
    function stop() {
        document.removeEventListener("mousemove", move);
        document.removeEventListener("mouseup", stop);
        document.removeEventListener("touchmove", move);
        document.removeEventListener("touchend", stop);
    }


    cropBox.addEventListener("mousedown", start);
    cropBox.addEventListener("touchstart", start, { passive: false });


    /* ================= Submit Crop ================= */
    window.submitCrop = function () {
        if (!img.complete) return;

        const imgRect = img.getBoundingClientRect();
        const boxRect = cropBox.getBoundingClientRect();

        const scaleX = img.naturalWidth / imgRect.width;
        const scaleY = img.naturalHeight / imgRect.height;

        document.getElementById("x").value =
            Math.round((boxRect.left - imgRect.left) * scaleX);

        document.getElementById("y").value =
            Math.round((boxRect.top - imgRect.top) * scaleY);

        document.getElementById("width").value =
            Math.round(boxRect.width * scaleX);

        document.getElementById("height").value =
            Math.round(boxRect.height * scaleY);

        document.getElementById("crop-form").submit();
    };


    /* ================= Save Changes ================= */
    window.saveChanges = function (popupId) {
        closePopup();
    };

});
