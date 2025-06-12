document.addEventListener("DOMContentLoaded", async () => {
  await i18n.loadTranslations(i18n.currentLang);
  i18n.applyTranslations();

  const dicomForm = document.getElementById("dicom-form");
  const fileInput = document.getElementById("dicom_file");
  const dropZone = document.getElementById("drop-dicom");
  const statusDiv = document.getElementById("dicom-status");
  const tableBody = document.getElementById("dicom-table-body");

  const dropText = document.createElement("p");
  dropText.className = "drop-text";
  dropText.textContent = i18n.translations.dicom_drag_drop_text || "📁 Datei hierher ziehen oder klicken";
  dropZone.appendChild(dropText);

  const previewText = document.createElement("div");
  previewText.className = "preview-text";
  dropZone.appendChild(previewText);

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
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
      statusDiv.textContent = `❌ ${i18n.translations.dicom_only_dcm_allowed || "Nur .dcm-Dateien erlaubt!"}`;
      statusDiv.style.color = "#ff4d4d";
    }
  }

  dicomForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    statusDiv.textContent = "";
    statusDiv.style.color = "#ffd700";

    if (!file) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_status_no_file || "Keine Datei ausgewählt."}`;
      statusDiv.style.color = "#ff4d4d";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    statusDiv.textContent = `⏳ ${i18n.translations.dicom_upload_running || "Upload läuft..."}`;

    try {
      const res = await fetch("http://localhost:8000/dicoms/uploads", {
        method: "POST",
        body: formData
      });

      const result = await res.json();
      if (!res.ok) throw new Error(result.detail || "Fehler beim Upload");

      statusDiv.textContent = `✅ ${i18n.translations.dicom_upload_success || "Upload erfolgreich."}`;
      statusDiv.style.color = "#00cc66";

      dicomForm.reset();
      previewText.textContent = "";
      await renderDicomTableFromBackend();
      await displayKiImages();
    } catch (err) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_upload_error || "Fehler beim Hochladen"}: ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
    }
  });

  function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return "-";
    const utcDate = new Date(dateTimeStr.endsWith("Z") ? dateTimeStr : `${dateTimeStr}Z`);
    if (isNaN(utcDate)) return "-";
    const berlinDate = new Date(utcDate.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));
    const timeStr = berlinDate.toLocaleTimeString(i18n.currentLang === "de" ? "de-DE" : "en-GB", { hour: "2-digit", minute: "2-digit" });
    const dateStr = berlinDate.toLocaleDateString(i18n.currentLang === "de" ? "de-DE" : "en-GB");

    return `${dateStr}, ${timeStr} ${i18n.translations.clock || "Uhr"}`;
  }

  async function renderDicomTableFromBackend() {
    tableBody.innerHTML = "";

    try {
      const res = await fetch("http://localhost:8000/dicoms/uploads");
      const dicoms = await res.json();
      if (!res.ok || !Array.isArray(dicoms)) throw new Error("Fehler beim Laden");

      if (dicoms.length === 0) {
        const row = document.createElement("tr");
        row.innerHTML = `<td colspan="3" style="text-align:center; color:#888;">${i18n.translations.dicom_table_empty || "Noch keine DICOM-Dateien hochgeladen."}</td>`;
        tableBody.appendChild(row);
        return;
      }

      dicoms.forEach((entry) => {
        const sop_uid = entry.sop_uid || entry.filename?.replace("_reupload.dcm", "") || "???";
        const timestamp = formatDateTime(entry.uploaded_at);
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${entry.filename}</td>
          <td>${timestamp}</td>
          <td>
            <button class="btn-reuse" onclick="reuseDicomFromBackend('${sop_uid}')">${i18n.translations.reuse_button || "🔁 Wiederverwenden"}</button>
            <button class="btn-delete" onclick="deleteDicomFromBackend('${sop_uid}')">${i18n.translations.delete_button || "🗑 Löschen"}</button>
          </td>
        `;
        tableBody.appendChild(row);
      });
    } catch (err) {
      const row = document.createElement("tr");
      row.innerHTML = `<td colspan="3" style="text-align:center; color:#f44;">❌ ${i18n.translations.load_error || "Fehler beim Laden"}</td>`;
      tableBody.appendChild(row);
    }
  }

  window.deleteDicomFromBackend = async function (sop_uid) {
    try {
      const res = await fetch(`http://localhost:8000/dicoms/uploads/${sop_uid}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Löschen fehlgeschlagen");

      statusDiv.textContent = `✅ ${i18n.translations.delete_success || "Gelöscht"}`;
      statusDiv.style.color = "#00cc66";
      await renderDicomTableFromBackend();
    } catch (err) {
      statusDiv.textContent = `❌ ${i18n.translations.delete_failed || "Löschen fehlgeschlagen"}: ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
    }
  };

  window.reuseDicomFromBackend = async function (sop_uid) {
    try {
      const res = await fetch(`http://localhost:8000/dicoms/uploads/${sop_uid}`);
      const blob = await res.blob();
      const file = new File([blob], `${sop_uid}_reupload.dcm`, { type: "application/dicom" });

      const formData = new FormData();
      formData.append("file", file);

      statusDiv.textContent = `⏳ ${i18n.translations.reuse_uploading || "Wiederverwenden..."}`;
      statusDiv.style.color = "#ffd700";

      const uploadRes = await fetch("http://localhost:8000/dicoms/uploads", {
        method: "POST",
        body: formData
      });

      const result = await uploadRes.json();
      if (!uploadRes.ok) throw new Error(result.detail || "Upload fehlgeschlagen");

      statusDiv.textContent = `✅ ${i18n.translations.reuse_success || "Erneut hochgeladen."}`;
      statusDiv.style.color = "#00cc66";

      await renderDicomTableFromBackend();
      await displayKiImages();
    } catch (err) {
      statusDiv.textContent = `❌ ${i18n.translations.reuse_error || "Fehler"}: ${err.message}`;
      statusDiv.style.color = "#ff4d4d";
    }
  };

  async function displayKiImages() {
    const kiContainer = document.getElementById("ki-list");
    const kiTitle = document.getElementById("ki-title");
    if (!kiContainer || !kiTitle) return;

    try {
      const res = await fetch("http://localhost:8000/ki-images");
      const containers = await res.json();
      if (!res.ok) throw new Error("Fehler beim Laden der KI");

      kiContainer.innerHTML = "";
      kiTitle.classList.remove("hidden");

      if (containers.length === 0) {
        kiContainer.textContent = i18n.translations.no_ki_images || "⚠️ Keine KI-Images verfügbar.";
        return;
      }

      containers.forEach((container) => {
        const card = document.createElement("div");
        card.className = "ki-card";
        card.innerHTML = `
          <div class="ki-card-icon">🧠</div>
          <h3>${container.image_name}:${container.image_tag}</h3>
          <p>ID: ${container.image_id}</p>
          <button class="select-btn" onclick='displayDiagnosis("${i18n.translations.dicom_ki_response_title || "Diagnose"}: ${container.image_name}:${container.image_tag}")'>
            ${i18n.translations.select || "Auswählen"}
          </button>
        `;
        kiContainer.appendChild(card);
      });

      kiContainer.classList.remove("hidden");
    } catch (err) {
      statusDiv.textContent = `❌ ${i18n.translations.dicom_error_loading_ki || "Fehler beim Laden der KI-Systeme"}: ${err.message}`;
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

  await renderDicomTableFromBackend();

  document.addEventListener("languageChanged", async () => {
    i18n.applyTranslations();
    await renderDicomTableFromBackend();
  });
});
