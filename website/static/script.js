const fileInput = document.getElementById('fileInput');
const selectImageBtn = document.getElementById('selectImageBtn');
const resultBoxes = document.getElementById('resultBoxes');
const removeBtn = document.getElementById('removeBackgroundBtn');
const originalImage = document.getElementById('originalImage');
const processedImage = document.getElementById('processedImage');
const loading = document.getElementById('loading');

const dropZone = document.getElementById('dropZone');

const downloadPreviewBtn = document.getElementById("downloadPreviewBtn");
const downloadHdBtn = document.getElementById("downloadHdBtn");

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB

let currentFile = null;



/* --- FIX DOUBLE TRIGGER --- */
selectImageBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

/* --- Click dropZone opens file input --- */
dropZone.addEventListener('click', () => fileInput.click());

/* --- Drag & Drop Support --- */
dropZone.addEventListener('dragover', (e) => e.preventDefault());

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (!file) return;
    handleSelectedFile(file);
});

/* --- File Input Listener --- */
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    handleSelectedFile(file);
});


/* -----------------------------------------------------
   Handle File Selection
----------------------------------------------------- */
function handleSelectedFile(file) {
    if (file.size > MAX_FILE_SIZE) {
        alert("File too large! Max size is 5MB.");
        return;
    }

    currentFile = file;

    originalImage.src = URL.createObjectURL(file);
    originalImage.classList.remove('hidden');

    processedImage.classList.add('hidden');

    // Hide both download buttons at start
    downloadPreviewBtn.classList.add("hidden");
    downloadHdBtn.classList.add("hidden");

    resultBoxes.classList.remove('hidden');
    removeBtn.classList.remove('hidden');

    document.getElementById('processedBox').classList.add('hidden');
}


/* -----------------------------------------------------
   Remove Background
----------------------------------------------------- */
removeBtn.addEventListener('click', async () => {
    if (!currentFile) return;

    loading.classList.remove('hidden');
    const processedBox = document.getElementById('processedBox');
    processedBox.classList.remove('hidden');
    processedImage.classList.add('hidden');

    // Hide both buttons during processing
    downloadPreviewBtn.classList.add("hidden");
    downloadHdBtn.classList.add("hidden");

    const form = new FormData();
    form.append('image', currentFile);

    try {
        const resp = await fetch('/process', {
            method: 'POST',
            body: form
        });

        const data = await resp.json();

        if (!data.ok) {
            alert(data.error || "Processing failed");
            loading.classList.add('hidden');
            return;
        }

        /* ---- SHOW PREVIEW IMAGE ---- */
        processedImage.src = data.result;
        processedImage.classList.remove('hidden');

        const id = data.image_id;


        /* -----------------------------------------------------
           1️⃣ PREVIEW DOWNLOAD (Free)
        ----------------------------------------------------- */
        downloadPreviewBtn.href = `/download/preview/${id}`;
        downloadPreviewBtn.classList.remove("hidden");
      

        /* -----------------------------------------------------
           2️⃣ HD DOWNLOAD (Login required)
        ----------------------------------------------------- */
        if (data.is_logged_in) {
            // User logged in → allow HD download
            downloadHdBtn.href = `/download/hd/${id}`;
        } else {
            // Not logged in → redirect to login first
            downloadHdBtn.href = `/login?next=/download/hd/${id}`;
        }

        downloadHdBtn.classList.remove("hidden");


        /* ---- Hide Remove Button ---- */
        removeBtn.classList.add('hidden');

        loading.classList.add('hidden');

    } catch (err) {
        console.error(err);
        alert("Error processing image.");
        loading.classList.add('hidden');
    }
});

