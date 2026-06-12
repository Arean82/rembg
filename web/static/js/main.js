document.addEventListener("DOMContentLoaded", () => {
    // --- Theming & UI Controls ---
    const htmlElement = document.documentElement;
    const themeSelector = document.getElementById("theme-selector");
    const modeToggle = document.getElementById("mode-toggle");
    
    themeSelector.addEventListener("change", (e) => {
        htmlElement.setAttribute("data-theme", e.target.value);
    });

    modeToggle.addEventListener("click", () => {
        const currentMode = htmlElement.getAttribute("data-mode");
        const newMode = currentMode === "dark" ? "light" : "dark";
        htmlElement.setAttribute("data-mode", newMode);
        // If we are in dark mode, show sun. If in light mode, show moon.
        modeToggle.textContent = newMode === "dark" ? "☀️" : "🌙";
    });
    
    // --- Language Selector ---
    const langSelector = document.getElementById("lang-selector");
    
    // Set dropdown to current cookie value if it exists
    const match = document.cookie.match(new RegExp('(^| )lang=([^;]+)'));
    if (match) langSelector.value = match[2];

    langSelector.addEventListener("change", (e) => {
        document.cookie = `lang=${e.target.value}; path=/`;
        window.location.reload();
    });

    // --- API Modal ---
    const apiBtn = document.getElementById("api-btn");
    const apiModal = document.getElementById("api-modal");
    const closeModal = document.getElementById("close-modal");

    apiBtn.addEventListener("click", () => apiModal.classList.remove("hidden"));
    closeModal.addEventListener("click", () => apiModal.classList.add("hidden"));

    // --- Slider & Number Input Sync ---
    const syncInputs = (sliderId, numId) => {
        const slider = document.getElementById(sliderId);
        const num = document.getElementById(numId);
        slider.addEventListener("input", () => num.value = slider.value);
        num.addEventListener("input", () => slider.value = num.value);
    };
    syncInputs("af-slider", "af");
    syncInputs("ab-slider", "ab");
    syncInputs("ae-slider", "ae");

    // --- State Management ---
    let currentFile = null;
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const submitBtn = document.getElementById('submit-btn');
    const clearBtn = document.getElementById('clear-btn');
    const loading = document.getElementById('loading');
    const resultContainer = document.getElementById('result-container');
    const resultImage = document.getElementById('result-image');
    const downloadBtn = document.getElementById('download-btn');
    const dropText = document.getElementById('drop-text');

    // --- Webcam Logic ---
    const webcamBtn = document.getElementById("webcam-btn");
    const webcamVideo = document.getElementById("webcam-video");
    const webcamCanvas = document.getElementById("webcam-canvas");
    let stream = null;

    webcamBtn.addEventListener("click", async () => {
        if (!stream) {
            // Start Webcam
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                webcamVideo.srcObject = stream;
                webcamVideo.style.display = "block";
                dropText.style.display = "none";
                webcamBtn.textContent = TRANSLATIONS["Snap Photo"];
            } catch (err) {
                alert(TRANSLATIONS["WebcamError"] + " " + err.message);
            }
        } else {
            // Snap Photo
            webcamCanvas.width = webcamVideo.videoWidth;
            webcamCanvas.height = webcamVideo.videoHeight;
            const ctx = webcamCanvas.getContext("2d");
            ctx.drawImage(webcamVideo, 0, 0);
            
            webcamCanvas.toBlob((blob) => {
                currentFile = new File([blob], "webcam_snap.png", { type: "image/png" });
                webcamVideo.style.display = "none";
                dropText.style.display = "block";
                dropText.textContent = TRANSLATIONS["WebcamReady"];
            }, "image/png");

            // Stop Webcam
            stream.getTracks().forEach(track => track.stop());
            stream = null;
            webcamBtn.textContent = TRANSLATIONS["Webcam"];
        }
    });

    // --- Clipboard Logic ---
    document.addEventListener("paste", (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let index in items) {
            const item = items[index];
            if (item.kind === 'file') {
                currentFile = item.getAsFile();
                dropText.textContent = `${TRANSLATIONS["Pasted"]} ${currentFile.name}`;
            }
        }
    });

    // --- Drag and Drop Logic ---
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            currentFile = e.dataTransfer.files[0];
            dropText.textContent = `${TRANSLATIONS["Selected"]} ${currentFile.name}`;
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            currentFile = e.target.files[0];
            dropText.textContent = `${TRANSLATIONS["Selected"]} ${currentFile.name}`;
        }
    });

    // --- Submission Logic ---
    clearBtn.addEventListener("click", () => {
        currentFile = null;
        dropText.innerHTML = TRANSLATIONS["DragDrop"];
        resultContainer.classList.add("hidden");
    });

    submitBtn.addEventListener("click", async () => {
        if (!currentFile) {
            alert(TRANSLATIONS["SelectError"]);
            return;
        }

        const formData = new FormData();
        formData.append("file", currentFile);
        
        // Append all parameters to perfectly match FastAPI requirements
        formData.append("model", document.getElementById("model").value);
        formData.append("a", document.getElementById("a").checked ? "true" : "false");
        formData.append("af", document.getElementById("af").value);
        formData.append("ab", document.getElementById("ab").value);
        formData.append("ae", document.getElementById("ae").value);
        formData.append("om", document.getElementById("om").checked);
        formData.append("ppm", document.getElementById("ppm").checked);
        formData.append("grayscale", document.getElementById("grayscale").checked);
        
        const extras = document.getElementById("extras").value;
        if (extras) formData.append("extras", extras);

        loading.classList.remove("hidden");
        resultContainer.classList.add("hidden");
        dropZone.style.display = "none";

        try {
            const response = await fetch("/api/remove", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const error = await response.text();
                throw new Error(error);
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            resultImage.src = url;
            resultContainer.classList.remove("hidden");
            
            downloadBtn.onclick = () => {
                const a = document.createElement("a");
                a.href = url;
                a.download = `nobg_${currentFile.name}`;
                a.click();
            };
        } catch (error) {
            alert(`${TRANSLATIONS["Error"]} ${error.message}`);
        } finally {
            loading.classList.add("hidden");
            dropZone.style.display = "flex";
        }
    });
});
