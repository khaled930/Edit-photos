document.addEventListener("DOMContentLoaded", () => {

    /* ====== Popup Control ====== */
    function openPopup(id) {
        closePopup();
        document.getElementById(id).style.display = "block";
    }

    function closePopup() {
        let popups = document.querySelectorAll(".popup");
        popups.forEach(popup => {
            popup.style.display = "none";
        });
    }

    window.openPopup = openPopup;   // لجعلها متاحة في HTML
    window.closePopup = closePopup;


    /* ===== Crop Elements ===== */
    const cropBox = document.getElementById("crop-box");
    const img = document.getElementById("image");
    const fileInput = document.getElementById("fileInput");

    let startX, startY, mode;
    let box = {};
    const MIN_SIZE = 40;


    /* ===== Enable Crop ===== */
    window.enableCrop = function () {
        cropBox.style.display = "block";
        cropBox.style.left = "50px";
        cropBox.style.top = "50px";
        cropBox.style.width = "200px";
        cropBox.style.height = "150px";
    };


    /* ===== Allow clicking on floating buttons even if cropBox is above ===== */
    cropBox.style.pointerEvents = "auto";
    document.querySelectorAll(".floating-btn, .fab-item").forEach(btn => {
        btn.style.pointerEvents = "auto";
    });


    /* ===== Mouse Down ===== */
    cropBox.addEventListener("mousedown", e => {
        e.preventDefault();
        e.stopPropagation();   // مهم جداً — يمنع تعطيل أزرار الواجهة العائمة

        mode = e.target.classList.contains("handle")
            ? e.target.classList[1]
            : "move";

        startX = e.clientX;
        startY = e.clientY;

        box = {
            x: cropBox.offsetLeft,
            y: cropBox.offsetTop,
            w: cropBox.offsetWidth,
            h: cropBox.offsetHeight
        };

        document.addEventListener("mousemove", resize);
        document.addEventListener("mouseup", stop);
    });


    /* ===== Resize / Move ===== */
    function resize(e) {
        let dx = e.clientX - startX;
        let dy = e.clientY - startY;

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

        cropBox.style.left = x + "px";
        cropBox.style.top = y + "px";
        cropBox.style.width = w + "px";
        cropBox.style.height = h + "px";
    }


    /* ===== Stop ===== */
    function stop() {
        document.removeEventListener("mousemove", resize);
        document.removeEventListener("mouseup", stop);
    }


    /* ===== Submit Crop ===== */
    window.submitCrop = function () {
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


    /* ===== Save Changes ===== */
    window.saveChanges = function (popupId) {
        alert("Changes in " + popupId + " saved successfully!");
    };

});



