document.addEventListener("DOMContentLoaded", () => {
  const dicomForm = document.getElementById("dicom-form");
  const fileInput = document.getElementById("dicom_file");
  const dropZone = document.getElementById("drop-dicom");
  const statusDiv = document.getElementById("dicom-status");
  const fileList = document.getElementById("dicom-list");

  // 🔍 Vorschau-Element für Dateiname
  const previewText = document.createElement("div");
  previewText.className = "preview-text";
  dropZone.appendChild(previewText);

  // 🟨 Drag & Drop Verhalten
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "#00cc66";
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.style.borderColor = "#ffd700";
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.style.borderColor = "#ffd700";
    const file = e.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith(".dcm")) {
      fileInput.files = e.dataTransfer.files;
      previewText.textContent = `📄 ${file.name}`;
    } else {
      previewText.textContent = "";
      statusDiv.textContent = "❌ Nur .dcm-Dateien erlaubt.";
      statusDiv.style.color = "#ff4d4d";
    }
  });

  dropZone.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file && file.name.toLowerCase().endsWith(".dcm")) {
      previewText.textContent = `📄 ${file.name}`;
      statusDiv.textContent = "";
    } else {
      fileInput.value = ""; // ungültige Datei löschen
      previewText.textContent = "";
      statusDiv.textContent = "❌ Nur .dcm-Dateien erlaubt.";
      statusDiv.style.color = "#ff4d4d";
    }
  });

  // 📥 GET: Liste der DICOM-Dateien
  function fetchDicomList() {
    fetch("/dicom/files")
      .then(res => res.json())
      .then(data => {
        fileList.innerHTML = "";
        data.forEach(file => {
          const li = document.createElement("li");
          li.textContent = `${file.filename} (ID: ${file.id})`;

          const deleteBtn = document.createElement("button");
          deleteBtn.textContent = "🗑️ Löschen";
          deleteBtn.onclick = () => deleteDicom(file.id);

          li.appendChild(deleteBtn);
          fileList.appendChild(li);
        });
      });
  }

  // 🗑️ DELETE
  function deleteDicom(id) {
    fetch(`/dicom/delete/${id}`, { method: "DELETE" })
      .then(res => {
        if (res.ok) {
          statusDiv.textContent = `✅ Datei mit ID ${id} gelöscht.`;
          statusDiv.style.color = "#00cc66";
          fetchDicomList();
        } else {
          statusDiv.textContent = `❌ Fehler beim Löschen der Datei ${id}`;
          statusDiv.style.color = "#ff4d4d";
        }
      });
  }

  // 🚀 POST: Upload
  dicomForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];

    statusDiv.className = "upload-status";
    statusDiv.style.color = "#ffd700";
    statusDiv.textContent = "";

    if (!file) {
      statusDiv.textContent = "❌ Bitte wählen Sie eine DICOM-Datei aus.";
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    if (!file.name.toLowerCase().endsWith(".dcm")) {
      statusDiv.textContent = "❌ Ungültiges Format. Bitte nur `.dcm`-Dateien hochladen.";
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    const formData = new FormData();
    formData.append("dicom_file", file);

    statusDiv.textContent = "⏳ Upload läuft...";

    try {
      const uploadRes = await fetch("/dicom/upload", {
        method: "POST",
        body: formData
      });

      const uploadText = await uploadRes.text();
      if (!uploadRes.ok) throw new Error(uploadText);

      statusDiv.textContent = "✅ Upload erfolgreich abgeschlossen.";
      statusDiv.style.color = "#00cc66";
      dicomForm.reset();
      previewText.textContent = "";
      fetchDicomList();
    } catch (err) {
      statusDiv.textContent = `❌ Fehler beim Upload: ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
    }
  });

  fetchDicomList(); // beim Laden starten
});
