document.addEventListener("DOMContentLoaded", () => {
  const dicomForm = document.getElementById("dicom-form");
  const fileInput = document.getElementById("dicom_file");
  const dropZone = document.getElementById("drop-dicom");
  const statusDiv = document.getElementById("dicom-status");
  const fileList = document.getElementById("dicom-list");

  // Vorschau-Element für Dateiname
  const previewText = document.createElement("div");
  previewText.className = "preview-text";
  dropZone.appendChild(previewText);

  //  Drag & Drop Verhalten
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
      previewText.textContent = `\u{1F4C4} ${file.name}`;
    } else {
      previewText.textContent = "";
      statusDiv.textContent = "\u274C Nur .dcm-Dateien erlaubt.";
      statusDiv.style.color = "#ff4d4d";
    }
  });

  dropZone.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file && file.name.toLowerCase().endsWith(".dcm")) {
      previewText.textContent = `\u{1F4C4} ${file.name}`;
      statusDiv.textContent = "";
    } else {
      fileInput.value = ""; // ungültige Datei löschen
      previewText.textContent = "";
      statusDiv.textContent = "\u274C Nur .dcm-Dateien erlaubt.";
      statusDiv.style.color = "#ff4d4d";
    }
  });

  //  POST: Upload
  dicomForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];

    statusDiv.className = "upload-status";
    statusDiv.style.color = "#ffd700";
    statusDiv.textContent = "";

    if (!file) {
      statusDiv.textContent = "\u274C Bitte wählen Sie eine Datei aus.";
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    if (!file.name.toLowerCase().endsWith(".dcm") && !file.name.toLowerCase().endsWith(".zip")) {
      statusDiv.textContent = "\u274C Ungültiges Format. Nur `.dcm` oder `.zip` erlaubt.";
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    statusDiv.textContent = "\u23F3 Upload läuft...";

    try {
      const uploadRes = await fetch("http://localhost:8000/dicom", {
        method: "POST",
        body: formData
      });

      let result;
      try {
        result = await uploadRes.json();
      } catch {
        throw new Error("Server returned an unexpected response format");
      }

      if (!uploadRes.ok) throw new Error(result.detail || `HTTP ${uploadRes.status}: ${uploadRes.statusText}`);

      statusDiv.textContent = `\u2705 ${result.message}`;
      statusDiv.style.color = "#00cc66";
      dicomForm.reset();
      previewText.textContent = "";
      // fetchDicomList();
      displayKiImages(); // KI-Images nach Upload anzeigen
    } catch (err) {
      statusDiv.textContent = `\u274C Fehler beim Upload: ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
    }
  });

  //  KI-Images abrufen und anzeigen
  async function displayKiImages() {
    const kiContainer = document.getElementById("ki-list");
    const kiTitle = document.getElementById("ki-title");
    const statusDiv = document.getElementById("dicom-status");

    if (!kiContainer || !kiTitle) {
      console.error("DOM elements for KI list not found");
      statusDiv.textContent = "\u274C Fehler: KI-Liste nicht gefunden.";
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/ki-images", {
        method: "GET"
      });

      let containers;
      try {
        containers = await response.json();
      } catch {
        throw new Error("Failed to parse KI images response");
      }

      if (!response.ok) throw new Error(containers.detail || `HTTP ${response.status}: ${response.statusText}`);

      kiContainer.innerHTML = ""; // Alte Liste leeren
      kiTitle.classList.remove("hidden");

      if (containers.length === 0) {
        kiContainer.textContent = "Keine KI-Images verfügbar.";
        kiContainer.classList.remove("hidden");
        return;
      }

      containers.forEach((container) => {
        const card = document.createElement("div");
        card.className = "ki-card";
        card.innerHTML = `
        <div class="ki-card-icon">\uD83E\uDDE0</div>
        <h3>${container.image_name}:${container.image_tag}</h3>
        <p>ID: ${container.image_id}</p>
        <button class="select-btn" onclick='displayDiagnosis("Container ausgewählt: ${container.image_name}:${container.image_tag}")'>Auswählen</button>
      `;
        kiContainer.appendChild(card);
      });

      kiContainer.classList.remove("hidden");
    } catch (err) {
      statusDiv.textContent = `\u274C Fehler beim Laden der KI-Images: ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
      kiContainer.innerHTML = "";
      kiContainer.textContent = "Fehler beim Laden der KI-Images.";
    }

    //  Ergebnisanzeige aktivieren 
    window.displayDiagnosis = function (text) {
      const resultBox = document.getElementById("ai-result");
      const content = document.getElementById("result-content");

      if (!resultBox || !content) {
        console.warn("Fehler: Ergebnisbox nicht gefunden.");
        return;
      }

      content.textContent = JSON.stringify({ diagnose: text }, null, 2);
      resultBox.classList.remove("hidden");
    };

  }
});

//  DICOM-Liste abrufen und anzeigen
//async function fetchDicomList() {
  // try {
  //   const response = await fetch("http://localhost:8000/dicoms", {
  //     method: "GET"
  //   });

  //   let dicoms;
  //   try {
  //     dicoms = await response.json();
  //   } catch {
  //     throw new Error("Failed to parse DICOM list");
  //   }

  //   if (!response.ok) throw new Error(dicoms.detail || `HTTP ${response.status}: ${response.statusText}`);

  //   // Liste im HTML-Element anzeigen
  //   const fileList = document.getElementById("dicom-list");
  //   fileList.innerHTML = ""; // Alte Liste leeren
  //   if (dicoms.length === 0) {
  //     fileList.textContent = "Keine DICOM-Datensätze verfügbar.";
  //     return;
  //   }

  //   dicoms.forEach(dicom => {
  //     const listItem = document.createElement("div");
  //     listItem.textContent = `📄 ${dicom.dicom_uuid} (${dicom.dicom_modality})`;
  //     fileList.appendChild(listItem);
  //   });
  // } catch (err) {
  //   const statusDiv = document.getElementById("dicom-status");
  //   statusDiv.textContent = `❌ Fehler beim Laden der DICOM-Liste: ${err.message}`;
  //   statusDiv.style.color = "#ff4d4d";
  // }
//}

//fetchDicomList(); // Beim Laden starten
//displayKiImages();


