document.addEventListener("DOMContentLoaded", () => {

    const popupOverlay = document.getElementById("popupOverlay");
    const cropBox = document.getElementById("crop-box");
    const img = document.getElementById("image");
    const fileInput = document.getElementById("fileInput");
    const uploadArea = document.getElementById("uploadArea");

    let startX, startY, mode;
    let box = {};
    const MIN_SIZE = 40;

    function openPopup(id) {
        closePopup();
        const popup = document.getElementById(id);
        if (popup) {
            popup.classList.add("active");
            popup.style.display = "flex";
            popupOverlay.classList.add("active");
            document.body.style.overflow = "hidden";
        }
    }

    function closePopup() {
        const popups = document.querySelectorAll(".popup");
        popups.forEach(popup => {
            popup.classList.remove("active");
            popup.style.display = "none";
        });
        popupOverlay.classList.remove("active");
        document.body.style.overflow = "auto";
    }

    window.openPopup = openPopup;
    window.closePopup = closePopup;

    if (uploadArea) {
        uploadArea.addEventListener("click", (e) => {
            if (e.target.tagName !== "BUTTON") {
                fileInput.click();
            }
        });

        uploadArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = "var(--primary)";
            uploadArea.style.background = "rgba(14, 165, 233, 0.05)";
        });

        uploadArea.addEventListener("dragleave", () => {
            uploadArea.style.borderColor = "var(--gray-300)";
            uploadArea.style.background = "var(--white)";
        });

        uploadArea.addEventListener("drop", (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = "var(--gray-300)";
            uploadArea.style.background = "var(--white)";

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                document.getElementById("uploadForm").submit();
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", () => {
            document.getElementById("uploadForm").submit();
        });
    }

    window.updateValue = function(id, value) {
        const element = document.getElementById(`${id}-value`);
        if (element) {
            element.textContent = parseFloat(value).toFixed(1);
        }
    };

    window.enableCrop = function() {
        if (!cropBox) return;

        cropBox.style.display = "block";
        cropBox.style.left = "50px";
        cropBox.style.top = "50px";
        cropBox.style.width = "200px";
        cropBox.style.height = "150px";
    };

    if (cropBox) {
        cropBox.style.pointerEvents = "auto";

        cropBox.addEventListener("mousedown", (e) => {
            e.preventDefault();
            e.stopPropagation();

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
    }

    function resize(e) {
        if (!cropBox) return;

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

    function stop() {
        document.removeEventListener("mousemove", resize);
        document.removeEventListener("mouseup", stop);
    }

    window.submitCrop = function() {
        if (!img || !cropBox) return;

        const imgRect = img.getBoundingClientRect();
        const boxRect = cropBox.getBoundingClientRect();

        const scaleX = img.naturalWidth / imgRect.width;
        const scaleY = img.naturalHeight / imgRect.height;

        document.getElementById("x").value = Math.round((boxRect.left - imgRect.left) * scaleX);
        document.getElementById("y").value = Math.round((boxRect.top - imgRect.top) * scaleY);
        document.getElementById("width").value = Math.round(boxRect.width * scaleX);
        document.getElementById("height").value = Math.round(boxRect.height * scaleY);

        document.getElementById("crop-form").submit();
    };

    window.downloadImage = function() {
        const afterImg = document.querySelector(".compare-box:last-child .image-wrapper img");

        if (afterImg && afterImg.src) {
            const link = document.createElement("a");
            link.href = afterImg.src;
            link.download = "edited_image.png";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            showNotification("Image downloaded successfully!");
        } else {
            showNotification("Please apply some edits before downloading!", "error");
        }
    };

    function showNotification(message, type = "success") {
        const notification = document.createElement("div");
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === "success" ? "linear-gradient(135deg, #10B981 0%, #059669 100%)" : "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)"};
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            z-index: 10000;
            font-weight: 500;
            animation: slideInRight 0.4s ease-out;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = "slideOutRight 0.4s ease-out";
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 400);
        }, 3000);
    }

    const style = document.createElement("style");
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    const ranges = document.querySelectorAll('input[type="range"]');
    ranges.forEach(range => {
        range.addEventListener("input", function() {
            const value = (this.value - this.min) / (this.max - this.min) * 100;
            this.style.background = `linear-gradient(to right, #0EA5E9 0%, #10B981 ${value}%, #E2E8F0 ${value}%, #E2E8F0 100%)`;
        });

        range.dispatchEvent(new Event("input"));
    });

    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function(e) {
            const button = this.querySelector('button[type="submit"]');
            if (button) {
                button.disabled = true;
                button.style.opacity = "0.6";
                button.style.cursor = "not-allowed";

                const originalText = button.textContent;
                button.textContent = "Processing...";

                setTimeout(() => {
                    button.disabled = false;
                    button.style.opacity = "1";
                    button.style.cursor = "pointer";
                    button.textContent = originalText;
                }, 5000);
            }
        });
    });

    console.log("%cProEdit Image Editor", "color: #0EA5E9; font-size: 20px; font-weight: bold;");
    console.log("%cProfessional Image Editing Platform", "color: #10B981; font-size: 14px;");
    console.log("%cDeveloped with ❤️", "color: #64748B; font-size: 12px;");

});
