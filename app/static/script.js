/* =========================================
   Global Variables
   ========================================= */
window.currentImageUrl = '';
window.currentEditedUrl = '';

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

// Update image in all places
function updateImage(newUrl) {
    window.currentEditedUrl = newUrl;
    localStorage.setItem('currentEditedUrl', newUrl);
    
    // Update main preview image in modal
    const mainImg = document.getElementById('modal-image');
    if (mainImg) {
        mainImg.src = newUrl + '?t=' + Date.now(); // Add timestamp to force reload
    }
    
    // Update crop workspace image
    const cropImg = document.getElementById('image');
    if (cropImg) {
        cropImg.src = newUrl + '?t=' + Date.now();
    }
    
    // Update preview card image (outside modal)
    const previewImg = document.getElementById('preview-image');
    if (previewImg) {
        previewImg.src = newUrl + '?t=' + Date.now();
    }
    
    // Update download link
    const downloadLink = document.getElementById('download-link');
    if (downloadLink) {
        downloadLink.href = newUrl;
        downloadLink.classList.remove('hidden');
    }
    
    // Update all hidden inputs with new image URL
    document.querySelectorAll('.image-url-input, #brightness-image-url').forEach(input => {
        input.value = newUrl;
    });
}

// AJAX helper function
async function applyEdit(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const result = await response.json();
        
        if (result.edited_url) {
            updateImage(result.edited_url);
        }
        
        if (result.histogram_url) {
            // Handle histogram separately
            const histogramContainer = document.getElementById('histogram-container');
            const histogramImage = document.getElementById('histogram-image');
            
            if (histogramContainer && histogramImage) {
                histogramImage.src = result.histogram_url + '?t=' + Date.now();
                histogramContainer.classList.remove('hidden');
            }
        }
        
        if (result.stats) {
            // Show compression stats
            const compressStats = document.getElementById('compress-stats');
            const beforeKb = document.getElementById('before-kb');
            const afterKb = document.getElementById('after-kb');
            
            if (compressStats && beforeKb && afterKb) {
                beforeKb.textContent = result.stats.before_kb;
                afterKb.textContent = result.stats.after_kb;
                compressStats.classList.remove('hidden');
            }
        }
        
        return result;
    } catch (error) {
        console.error('Error applying edit:', error);
        alert('حدث خطأ أثناء التعديل. يرجى المحاولة مرة أخرى.');
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

function switchTab(tabName,event) {
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

async function submitCrop() {
    const img = document.getElementById("image");
    const cropBox = document.getElementById("crop-box");
    
    if (!img || !cropBox) return;

    const imgRect = img.getBoundingClientRect();
    const boxRect = cropBox.getBoundingClientRect();

    const scaleX = img.naturalWidth / imgRect.width;
    const scaleY = img.naturalHeight / imgRect.height;

    const x = Math.round((boxRect.left - imgRect.left) * scaleX);
    const y = Math.round((boxRect.top - imgRect.top) * scaleY);
    const width = Math.round(boxRect.width * scaleX);
    const height = Math.round(boxRect.height * scaleY);

    const imageUrl = window.currentEditedUrl || window.currentImageUrl || document.querySelector('input[name="image_url"]')?.value;
    
    if (!imageUrl) {
        alert('لا توجد صورة للقص');
        return;
    }

    await applyEdit('/api/crop', {
        image_url: imageUrl,
        x: x,
        y: y,
        width: width,
        height: height
    });
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

    // Initialize current image URLs
    const imageUrlInput = document.querySelector('input[name="image_url"]');
    if (imageUrlInput && imageUrlInput.value) {
        window.currentImageUrl = imageUrlInput.value;
        window.currentEditedUrl = imageUrlInput.value;
    }

    // Setup AJAX for all edit forms
    setupAjaxForms();
});

function setupAjaxForms() {
    // Brightness form
    const brightnessForm = document.querySelector('form[action="/brightness"]');
    if (brightnessForm) {
        brightnessForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(brightnessForm);
            const imageUrl = window.currentEditedUrl || formData.get('image_url');
            const factor = parseFloat(formData.get('factor'));
            
            window.currentImageUrl = imageUrl;
            await applyEdit('/api/brightness', {
                image_url: imageUrl,
                factor: factor
            });
        });
    }

    // Contrast form
    const contrastForm = document.querySelector('form[action="/contrast"]');
    if (contrastForm) {
        contrastForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(contrastForm);
            const imageUrl = window.currentEditedUrl || formData.get('image_url');
            const factor = parseFloat(formData.get('factor'));
            
            window.currentImageUrl = imageUrl;
            await applyEdit('/api/contrast', {
                image_url: imageUrl,
                factor: factor
            });
        });
    }

    // Sharpen form
    const sharpenForm = document.querySelector('form[action="/sharpen"]');
    if (sharpenForm) {
        sharpenForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(sharpenForm);
            const imageUrl = window.currentEditedUrl || formData.get('image_url');
            
            window.currentImageUrl = imageUrl;
            await applyEdit('/api/sharpen', {
                image_url: imageUrl
            });
        });
    }

    // Smooth form
    const smoothForm = document.querySelector('form[action="/smooth"]');
    if (smoothForm) {
        smoothForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(smoothForm);
            const imageUrl = window.currentEditedUrl || formData.get('image_url');
            
            window.currentImageUrl = imageUrl;
            await applyEdit('/api/smooth', {
                image_url: imageUrl
            });
        });
    }

    // Rotate form
    const rotateForm = document.querySelector('form[action="/rotate"]');
    if (rotateForm) {
        rotateForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(rotateForm);
            const imageUrl = window.currentEditedUrl || formData.get('image_url');
            const angle = parseInt(formData.get('angle'));
            
            window.currentImageUrl = imageUrl;
            
            // Try API endpoint first, fallback to regular endpoint
            try {
                await applyEdit('/api/rotate', {
                    image_url: imageUrl,
                    angle: angle
                });
            } catch (error) {
                // Fallback to regular form submission
                const response = await fetch('/rotate', {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    const result = await response.json();
                    if (result.edited_url) {
                        updateImage(result.edited_url);
                    }
                }
            }
        });
    }

    // Compress form
    const compressForm = document.querySelector('form[action="/compress"]');
    if (compressForm) {
        compressForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(compressForm);
            const imageUrl = window.currentEditedUrl || formData.get('image_url');
            const quality = parseInt(formData.get('quality'));
            
            window.currentImageUrl = imageUrl;
            
            // Try API endpoint first, fallback to regular endpoint
            try {
                await applyEdit('/api/compress', {
                    image_url: imageUrl,
                    quality: quality
                });
            } catch (error) {
                // Fallback to regular form submission
                const response = await fetch('/compress', {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    const result = await response.json();
                    if (result.edited_url) {
                        updateImage(result.edited_url);
                    }
                    if (result.stats) {
                        const compressStats = document.getElementById('compress-stats');
                        const beforeKb = document.getElementById('before-kb');
                        const afterKb = document.getElementById('after-kb');
                        if (compressStats && beforeKb && afterKb) {
                            beforeKb.textContent = result.stats.before_kb;
                            afterKb.textContent = result.stats.after_kb;
                            compressStats.classList.remove('hidden');
                        }
                    }
                }
            }
        });
    }

    // Histogram form
    const histogramForm = document.querySelector('form[action="/histogram"]');
    if (histogramForm) {
        histogramForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(histogramForm);
            const imageUrl = window.currentEditedUrl || formData.get('image_url');
            
            window.currentImageUrl = imageUrl;
            
            // Try API endpoint first, fallback to regular endpoint
            try {
                await applyEdit('/api/histogram', {
                    image_url: imageUrl
                });
            } catch (error) {
                // Fallback to regular form submission
                const response = await fetch('/histogram', {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    const result = await response.json();
                    if (result.histogram_url) {
                        const histogramContainer = document.getElementById('histogram-container');
                        const histogramImage = document.getElementById('histogram-image');
                        if (histogramContainer && histogramImage) {
                            histogramImage.src = result.histogram_url + '?t=' + Date.now();
                            histogramContainer.classList.remove('hidden');
                        }
                    }
                }
            }
        });
    }
}