/* =========================================
   Global Functions
   ========================================= */

function openEditor() {
    const modal = document.getElementById('editor-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        // Small delay to allow display:flex to apply before opacity transition
        setTimeout(() => {
            modal.classList.remove('opacity-0');
        }, 10);
    }
}

function closeEditor() {
    const modal = document.getElementById('editor-modal');
    if (modal) {
        modal.classList.add('opacity-0');
        // Wait for transition to finish before hiding
        setTimeout(() => {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }, 300);
    }
}

function switchTab(tabName) {
    // Hide all panels
    document.querySelectorAll('.control-panel').forEach(panel => {
        panel.classList.add('hidden');
    });
    
    // Show selected panel
    const selectedPanel = document.getElementById('tab-' + tabName);
    if (selectedPanel) selectedPanel.classList.remove('hidden');

    // Update Sidebar Buttons
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.classList.remove('active');
        // Reset icons color
        const iconBox = btn.querySelector('div:first-child');
        if(iconBox) {
            iconBox.classList.remove('bg-primary', 'text-white');
            iconBox.classList.add('bg-gray-200', 'dark:bg-white/5');
        }
    });
    
    // Highlight clicked button
    if (event && event.currentTarget) {
        const btn = event.currentTarget;
        btn.classList.add('active');
        const iconBox = btn.querySelector('div:first-child');
        if(iconBox) {
            iconBox.classList.remove('bg-gray-200', 'dark:bg-white/5');
            iconBox.classList.add('bg-primary', 'text-white');
        }
    }

    // View Switching (Crop vs Normal)
    const cropWorkspace = document.getElementById('crop-workspace');
    const normalView = document.getElementById('normal-view');

    if (tabName === 'crop') {
        if(cropWorkspace) cropWorkspace.classList.remove('hidden');
        if(normalView) normalView.classList.add('hidden');
    } else {
        if(cropWorkspace) cropWorkspace.classList.add('hidden');
        if(normalView) normalView.classList.remove('hidden');
    }
}

/* Crop Logic Variables */
let startX, startY, mode;
let box = {};
const MIN_SIZE = 40;

function enableCrop() {
    const cropBox = document.getElementById("crop-box");
    if (cropBox) {
        cropBox.style.display = "block";
        cropBox.style.left = "25%";
        cropBox.style.top = "25%";
        cropBox.style.width = "50%";
        cropBox.style.height = "50%";
    }
}

function submitCrop() {
    const img = document.getElementById("image");
    const cropBox = document.getElementById("crop-box");
    
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
}


/* =========================================
   DOM Loaded Logic
   ========================================= */
document.addEventListener("DOMContentLoaded", () => {

    /* Theme Logic */
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    if (localStorage.getItem('theme') === 'dark' || 
       (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        htmlElement.classList.add('dark');
    } else {
        htmlElement.classList.remove('dark');
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            htmlElement.classList.toggle('dark');
            if (htmlElement.classList.contains('dark')) {
                localStorage.setItem('theme', 'dark');
            } else {
                localStorage.setItem('theme', 'light');
            }
        });
    }

    /* Crop Box Interaction */
    const cropBox = document.getElementById("crop-box");

    if (cropBox) {
        cropBox.addEventListener("mousedown", e => {
            e.preventDefault();
            e.stopPropagation();

            mode = e.target.classList.contains("handle") ? e.target.classList[1] : "move";

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
        let dx = e.clientX - startX;
        let dy = e.clientY - startY;

        let x = box.x;
        let y = box.y;
        let w = box.w;
        let h = box.h;

        if (mode === "move") {
            x += dx;
            y += dy;
        } else {
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
});