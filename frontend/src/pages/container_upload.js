document.addEventListener("DOMContentLoaded", () => {
  const hubForm = document.getElementById("hub-upload-form");
  const localForm = document.getElementById("local-upload-form");

  // 🔧 Fehlermeldung interpretieren
  function interpretErrorMessage(rawMsg, source = "") {
    if (!rawMsg) return "❌ Ein unbekannter Fehler ist aufgetreten.";

    const msg = rawMsg.toLowerCase();

    if (source === "local" && msg.includes("file") && msg.includes("invalid")) {
      return "❌ Ungültiges Dateiformat. Bitte laden Sie eine `.tar`-Datei hoch.";
    }

    if (source === "hub" && (msg.includes("invalid") || msg.includes("format"))) {
      return "❌ Ungültiges Format. Bitte geben Sie z. B. ein Image im Format `nginx:latest` ein.";
    }

    if (msg.includes("missing") || msg.includes("required")) {
      return "❌ Bitte füllen Sie alle Pflichtfelder aus.";
    }

    if (msg.includes("already exists")) {
      return "❌ Dieses Image wurde bereits hochgeladen.";
    }

    if (msg.includes("not found")) {
      return "❌ Das angegebene Image konnte nicht gefunden werden.";
    }

    return `❌ Fehler: ${rawMsg}`;
  }

  // 🐳 DockerHub Upload
  if (hubForm) {
    const spinner = document.createElement("div");
    spinner.id = "hub-spinner";
    spinner.innerHTML = `<div class="spinner"></div><span>Verarbeitung läuft...</span>`;
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

        if (res.ok) {
          const result = await res.json();
          statusDiv.textContent = `✅ Referenziert: ${result.image_name || result.id}`;
          statusDiv.className = "upload-status success";
          hubForm.reset();
        } else {
          const errText = await res.text();
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

  // 💻 Lokaler Upload mit .tar-Prüfung, Fortschritt, Spinner, Fehlertext
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
    spinner.innerHTML = `<div class="spinner"></div><span>Verarbeitung läuft...</span>`;
    spinner.style.display = "none";
    spinner.style.marginTop = "10px";
    localForm.appendChild(spinner);

    localForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const fileInput = localForm.querySelector('input[type="file"]');
      const file = fileInput.files[0];
      const statusDiv = document.getElementById("local-status");

      statusDiv.textContent = "";
      statusDiv.className = "upload-status";

      // ❗ Typprüfung: nur .tar erlaubt
      if (!file || !file.name.toLowerCase().endsWith(".tar")) {
        statusDiv.textContent = "❌ Ungültiges Dateiformat. Bitte laden Sie eine `.tar`-Datei hoch.";
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
              statusDiv.textContent = `✅ Hochgeladen: ${result.image_name || result.id}`;
              statusDiv.className = "upload-status success";
              localForm.reset();
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
          statusDiv.textContent = "❌ Upload-Fehler";
          statusDiv.className = "upload-status error";
        };

        xhr.send(new FormData(localForm));
      } catch (err) {
        clearInterval(slowInterval);
        progress.style.display = "none";
        percentLabel.style.display = "none";
        spinner.style.display = "none";
        statusDiv.textContent = interpretErrorMessage(err.message, "local");
        statusDiv.className = "upload-status error";
      }
    });
  }
});
