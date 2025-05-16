document.addEventListener("DOMContentLoaded", () => {
  const dicomForm = document.getElementById("dicom-form");
  const fileInput = document.getElementById("dicom_file");
  const dropZone = document.getElementById("drop-dicom");
  const statusDiv = document.getElementById("dicom-status");
  const kiContainer = document.getElementById("ki-list");
  const aiBox = document.getElementById("ai-result");
  const kiTitle = document.getElementById("ki-title");

  // Vorschau
  const previewText = document.createElement("div");
  previewText.className = "preview-text";
  dropZone.appendChild(previewText);

  // Drag & Drop Verhalten
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
    if (file) {
      fileInput.files = e.dataTransfer.files;
      previewText.textContent = `📄 ${file.name}`;
    }
  });

  dropZone.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
      previewText.textContent = `📄 ${fileInput.files[0].name}`;
    } else {
      previewText.textContent = "";
    }
  });

  dicomForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const file = fileInput.files[0];
    statusDiv.className = "upload-status";
    statusDiv.style.color = "#ffd700";
    statusDiv.textContent = "";
    aiBox.classList.add("hidden");

    if (!file) {
      statusDiv.textContent = "❌ Bitte wählen Sie eine DICOM-Datei aus.";
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    // 🧪 TEMPORÄR deaktiviert für Tests – auch .pdf, .zip etc. erlaubt
    // if (!file.name.toLowerCase().endsWith(".dcm")) {
    //   statusDiv.textContent = "❌ Ungültiges Format. Bitte nur `.dcm`-Dateien hochladen.";
    //   statusDiv.style.color = "#ff4d4d";
    //   return;
    // }


    const formData = new FormData();
    formData.append("dicom_file", file);

    statusDiv.textContent = "⏳ Upload läuft...";
    statusDiv.style.color = "#ffd700";

    // Simulierter Upload + Containerliste laden
    setTimeout(async () => {
      statusDiv.textContent = "✅ Upload erfolgreich abgeschlossen.";
      statusDiv.style.color = "#00cc66";

      try {
        const res = await fetch("http://localhost:8000/ki-images");
        if (!res.ok) throw new Error(await res.text());
        const containers = await res.json();

        kiContainer.innerHTML = "";
        kiTitle.classList.remove("hidden");

        containers.forEach((container) => {
          const card = document.createElement("div");
          card.className = "ki-card";
          card.innerHTML = `
            <div class="ki-card-icon">🧠</div>
            <h3>${container.image_name}:${container.image_tag}</h3>
            <p>ID: ${container.image_id}</p>
            <button class="select-btn" onclick='showResult("Container ausgewählt: ${container.image_name}:${container.image_tag}")'>Auswählen</button>
          `;
          kiContainer.appendChild(card);
        });

        kiContainer.classList.remove("hidden");
      } catch (err) {
        kiContainer.innerHTML = `<p style="color:red;">❌ Fehler beim Laden der Container: ${err.message}</p>`;
      }
    }, 1000);
  });

  window.showResult = function (diagnoseText) {
    const resultBox = document.getElementById("ai-result");
    const content = document.getElementById("result-content");
    content.textContent = JSON.stringify({ diagnose: diagnoseText }, null, 2);
    resultBox.classList.remove("hidden");
  };
});
