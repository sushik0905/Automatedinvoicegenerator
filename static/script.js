const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("fileInput");
const preview = document.getElementById("preview");

// Click to upload
dropZone.addEventListener("click", () => fileInput.click());

// Preview + Upload
fileInput.addEventListener("change", async () => {
    const file = fileInput.files[0];

    if (!file) return;

    // ✅ Show preview
    const reader = new FileReader();
    reader.onload = function (e) {
        preview.src = e.target.result;
        preview.style.display = "block";
    };
    reader.readAsDataURL(file);

    // ✅ Upload to backend
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(
            "https://yashasvi0409-automated-invoice-generator.hf.space/upload",
            {
                method: "POST",
                body: formData
            }
        );

        const resultHTML = await response.text();

        // ✅ Replace page with result
        document.open();
        document.write(resultHTML);
        document.close();

    } catch (error) {
        console.error("Upload failed:", error);
        alert("❌ Upload failed. Check backend connection.");
    }
});
