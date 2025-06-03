document.addEventListener("DOMContentLoaded", async () => {
  await i18n.loadTranslations(i18n.currentLang);
  i18n.applyTranslations();

  const hubForm = document.getElementById("hub-upload-form");
  const localForm = document.getElementById("local-upload-form");

  // ---------- Fehlerbehandlung ----------
  function interpretErrorMessage(rawMsg, source = "") {
    if (!rawMsg) return i18n.translations.upload_error_generic;
    const msg = rawMsg.toLowerCase();

    if (source === "local" && msg.includes("file") && msg.includes("invalid")) {
      return i18n.translations.upload_error_invalid_tar;
    }
    if (source === "hub" && (msg.includes("invalid") || msg.includes("format") || msg.includes("reference"))) {
      return i18n.translations.upload_error_invalid_hub;
    }
    if (msg.includes("missing") || msg.includes("required") || msg.includes("feld fehlt")) {
      return i18n.translations.fill_required;
    }
    if (msg.includes("already exists") || msg.includes("existiert bereits")) {
      return i18n.translations.already_exists;
    }
    if (msg.includes("not found") || msg.includes("nicht gefunden")) {
      return i18n.translations.not_found;
    }

    return `${i18n.translations.upload_error_prefix}${rawMsg}`;
  }

  // ---------- Docker Hub Upload ----------
  if (hubForm) {
    const spinner = document.createElement("div");
    spinner.id = "hub-spinner";
    spinner.innerHTML = `<div class="spinner"></div><span>${i18n.translations.upload_processing}</span>`;
    spinner.style.display = "none";
    spinner.style.marginTop = "10px";
    hubForm.appendChild(spinner);

    hubForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData(hubForm);
      const statusDiv = document.getElementById("hub-status");

      statusDiv.textContent = "";
      statusDiv.className = "upload-status";
      spinner.style.display = "flex";

      try {
        const res = await fetch("http://localhost:8000/ki-images/hub", {
          method: "POST",
          body: formData
        });

        spinner.style.display = "none";
        let errText = "";

        if (res.ok) {
          const result = await res.json();
          statusDiv.textContent = `${i18n.translations.upload_success}${result.image_name || result.id}`;
          statusDiv.className = "upload-status success";
          hubForm.reset();
        } else {
          try {
            const errJson = await res.json();
            errText = errJson.detail || JSON.stringify(errJson);
          } catch {
            errText = await res.text();
          }
          statusDiv.textContent = interpretErrorMessage(errText, "hub");
          statusDiv.className = "upload-status error";
        }
      } catch (err) {
        spinner.style.display = "none";
        statusDiv.textContent = interpretErrorMessage(err.message, "hub");
        statusDiv.className = "upload-status error";
      }
    });
  }

  // ---------- Lokaler Upload ----------
  if (localForm) {
    const progress = document.createElement("progress");
    progress.id = "local-progress";
    progress.value = 0;
    progress.max = 100;
    progress.style.width = "100%";
    progress.style.display = "none";
    localForm.appendChild(progress);

    const percentLabel = document.createElement("span");
    percentLabel.id = "local-progress-label";
    percentLabel.textContent = "0%";
    percentLabel.style.marginLeft = "10px";
    percentLabel.style.color = "#fff";
    percentLabel.style.fontSize = "0.9rem";
    percentLabel.style.display = "none";
    localForm.appendChild(percentLabel);

    const spinner = document.createElement("div");
    spinner.id = "local-spinner";
    spinner.innerHTML = `<div class="spinner"></div><span>${i18n.translations.upload_processing}</span>`;
    spinner.style.display = "none";
    spinner.style.marginTop = "10px";
    localForm.appendChild(spinner);

    const dropZone = document.getElementById("drop-local");
    const fileInput = document.getElementById("fileInput-local");
    const dropLabel = document.querySelector("#drop-local span");
    const statusDiv = document.getElementById("local-status");

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
      if (e.dataTransfer.files.length) {
        const file = e.dataTransfer.files[0];
        fileInput.files = e.dataTransfer.files;
        previewText.textContent = `📄 ${file.name}`;
      }
    });

    dropZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) {
        previewText.textContent = `📄 ${fileInput.files[0].name}`;
      } else {
        previewText.textContent = "";
      }
    });

    localForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const file = fileInput.files[0];
      statusDiv.textContent = "";
      statusDiv.className = "upload-status";

      if (!file || !file.name.toLowerCase().endsWith(".tar")) {
        statusDiv.textContent = i18n.translations.upload_error_invalid_tar;
        statusDiv.className = "upload-status error";
        return;
      }

      progress.value = 0;
      progress.style.display = "block";
      percentLabel.style.display = "inline";
      percentLabel.textContent = "0%";
      spinner.style.display = "none";

      let fakeProgress = 0;
      let slowInterval;

      try {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "http://localhost:8000/ki-images/local");

        xhr.upload.addEventListener("progress", (event) => {
          if (event.lengthComputable) {
            const percent = Math.round((event.loaded / event.total) * 100);
            if (percent < 95) {
              progress.value = percent;
              percentLabel.textContent = `${percent}%`;
              fakeProgress = percent;
            } else {
              clearInterval(slowInterval);
              slowInterval = setInterval(() => {
                if (fakeProgress < 99) {
                  fakeProgress += 0.5;
                  progress.value = fakeProgress;
                  percentLabel.textContent = `${Math.round(fakeProgress)}%`;
                } else {
                  clearInterval(slowInterval);
                }
              }, 100);
            }
          }
        });

        xhr.onload = () => {
          clearInterval(slowInterval);
          progress.value = 100;
          percentLabel.textContent = "100%";
          progress.style.display = "none";
          percentLabel.style.display = "none";
          spinner.style.display = "flex";

          setTimeout(() => {
            spinner.style.display = "none";
            if (xhr.status >= 200 && xhr.status < 300) {
              const result = JSON.parse(xhr.responseText);
              statusDiv.textContent = `${i18n.translations.upload_success}${result.image_name || result.id}`;
              statusDiv.className = "upload-status success";
              localForm.reset();
              previewText.textContent = "";
              dropLabel.textContent = i18n.translations.container_upload_drag_drop_local;
            } else {
              statusDiv.textContent = interpretErrorMessage(xhr.responseText, "local");
              statusDiv.className = "upload-status error";
            }
          }, 1000);
        };

        xhr.onerror = () => {
          clearInterval(slowInterval);
          progress.style.display = "none";
          percentLabel.style.display = "none";
          spinner.style.display = "none";
          statusDiv.textContent = i18n.translations.upload_error_network;
          statusDiv.className = "upload-status error";
        };

        const formData = new FormData();
        formData.append("file", file);
        xhr.send(formData);
      } catch (err) {
        clearInterval(slowInterval);
        progress.style.display = "none";
        percentLabel.style.display = "none";
        spinner.style.display = "none";
        statusDiv.textContent = interpretErrorMessage(err.message, "local");
        statusDiv.className = "upload-status error";
      }
    });

    // 🔁 Sprachwechsel
    document.addEventListener("languageChanged", () => {
      i18n.applyTranslations();

      const dropLabel = document.querySelector("#drop-local span");
      if (dropLabel) {
        dropLabel.textContent = i18n.translations.container_upload_drag_drop_local;
      }

      spinner.querySelector("span").textContent = i18n.translations.upload_processing;
    });
  }
});
