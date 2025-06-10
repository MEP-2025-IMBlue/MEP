document.addEventListener("DOMContentLoaded", async () => {
  await i18n.loadTranslations(i18n.currentLang);
  i18n.applyTranslations();

  const dicomForm = document.getElementById("dicom-form");
  const fileInput = document.getElementById("dicom_file");
  const dropZone = document.getElementById("drop-dicom");
  const statusDiv = document.getElementById("dicom-status");

  // Drop-Zone-Text hinzufügen (wird später dynamisch ersetzt)
  const dropText = document.createElement("p");
  dropText.className = "drop-text";
  dropText.textContent = i18n.translations.dicom_drag_drop_text;
  dropZone.appendChild(dropText);

  const previewText = document.createElement("div");
  previewText.className = "preview-text";
  dropZone.appendChild(previewText);

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
    handleFileSelection(file);
  });

  dropZone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", () => handleFileSelection(fileInput.files[0]));

  function handleFileSelection(file) {
    if (file && file.name.toLowerCase().endsWith(".dcm")) {
      fileInput.files = [file];
      previewText.textContent = `📄 ${file.name}`;
      statusDiv.textContent = "";
    } else {
      fileInput.value = "";
      previewText.textContent = "";
      statusDiv.textContent = `❌ ${i18n.translations.dicom_only_dcm_allowed}`;
      statusDiv.style.color = "#ff4d4d";
    }
  }

  dicomForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];

    statusDiv.className = "upload-status";
    statusDiv.style.color = "#ffd700";
    statusDiv.textContent = "";

    if (!file) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_status_no_file}`;
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    if (!file.name.toLowerCase().endsWith(".dcm") && !file.name.toLowerCase().endsWith(".zip")) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_status_invalid_format}`;
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    statusDiv.textContent = `⏳ ${i18n.translations.dicom_upload_running}`;

    try {
      const res = await fetch("http://localhost:8000/dicom", { method: "POST", body: formData });
      const result = await res.json();

      if (!res.ok) throw new Error(result.detail || `HTTP ${res.status}: ${res.statusText}`);

      statusDiv.textContent = `✅ ${i18n.translations.dicom_upload_success}`;
      statusDiv.style.color = "#00cc66";
      dicomForm.reset();
      previewText.textContent = "";
      displayKiImages();
    } catch (err) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_upload_error} ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
    }
  });

  async function displayKiImages() {
    const kiContainer = document.getElementById("ki-list");
    const kiTitle = document.getElementById("ki-title");

    if (!kiContainer || !kiTitle) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_error_ki_list_missing}`;
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/ki-images");
      const containers = await response.json();
      if (!response.ok) throw new Error(containers.detail || `HTTP ${response.status}: ${response.statusText}`);

      kiContainer.innerHTML = "";
      kiTitle.classList.remove("hidden");

      if (containers.length === 0) {
        kiContainer.textContent = i18n.translations.no_ki_images;
        kiContainer.classList.remove("hidden");
        return;
      }

      containers.forEach((container) => {
        const card = document.createElement("div");
        card.className = "ki-card";
        card.innerHTML = `
          <div class="ki-card-icon">🧠</div>
          <h3>${container.image_name}:${container.image_tag}</h3>
          <p>${i18n.translations.description || "Beschreibung"}: ${container.repository || "-"}</p>
          <button class="select-btn" onclick='displayDiagnosis("${i18n.translations.dicom_ki_response_title}: ${container.image_name}:${container.image_tag}")'>
            ${i18n.translations.select || "Auswählen"}
          </button>
        `;
        kiContainer.appendChild(card);
      });
      

      kiContainer.classList.remove("hidden");
      updateTranslationTexts();
    } catch (err) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_error_loading_ki} ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
    }
  }

  window.displayDiagnosis = function (text) {
    const resultBox = document.getElementById("ai-result");
    const content = document.getElementById("result-content");
    if (!resultBox || !content) return;
    content.textContent = JSON.stringify({ diagnose: text }, null, 2);
    resultBox.classList.remove("hidden");
  };

  function updateTranslationTexts() {
    dropText.textContent = i18n.translations.dicom_drag_drop_text;
    document.querySelectorAll(".select-btn").forEach(btn => {
      btn.textContent = i18n.translations.select || "Auswählen";
    });
  }

  document.addEventListener("languageChanged", () => {
    i18n.applyTranslations();
    updateTranslationTexts();
    if (fileInput.files.length > 0) {
      handleFileSelection(fileInput.files[0]);
    }
  });
});
