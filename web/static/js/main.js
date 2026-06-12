const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const resultContainer = document.getElementById('result-container');
const resultImage = document.getElementById('result-image');
const downloadBtn = document.getElementById('download-btn');
const resetBtn = document.getElementById('reset-btn');

let currentBlob = null;
let currentFilename = 'image.png';

// Handle Drag and Drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
        processFile(e.dataTransfer.files[0]);
    }
});

// Handle Click
dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        processFile(e.target.files[0]);
    }
});

function processFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }

    currentFilename = `nobg_${file.name}`;
    
    // UI State
    dropZone.classList.add('hidden');
    loading.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/remove', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to process image');
        return response.blob();
    })
    .then(blob => {
        currentBlob = blob;
        const url = URL.createObjectURL(blob);
        resultImage.src = url;
        
        loading.classList.add('hidden');
        resultContainer.classList.remove('hidden');
    })
    .catch(error => {
        alert(error.message);
        loading.classList.add('hidden');
        dropZone.classList.remove('hidden');
    });
}

// Download Button
downloadBtn.addEventListener('click', () => {
    if (currentBlob) {
        const url = URL.createObjectURL(currentBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = currentFilename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
});

// Reset Button
resetBtn.addEventListener('click', () => {
    resultContainer.classList.add('hidden');
    dropZone.classList.remove('hidden');
    fileInput.value = '';
    currentBlob = null;
    resultImage.src = '';
});
