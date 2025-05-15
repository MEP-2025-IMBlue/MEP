document.addEventListener("DOMContentLoaded", () => {
  const hubForm = document.getElementById("hub-upload-form");
  const localForm = document.getElementById("local-upload-form");

  // DockerHub Upload mit Spinner
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
          statusDiv.style.color = "#00cc66";
          hubForm.reset();
        } else {
          const errText = await res.text();
          statusDiv.textContent = `❌ Fehler: ${errText}`;
          statusDiv.style.color = "#ff4d4d";
        }
      } catch (err) {
        spinner.style.display = "none";
        statusDiv.textContent = `❌ Verbindungsfehler: ${err.message}`;
        statusDiv.style.color = "#ff4d4d";
      }
    });
  }

  // Lokaler Upload mit Fortschrittsbalken, Prozent und Spinner
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

      const formData = new FormData(localForm);
      const statusDiv = document.getElementById("local-status");

      statusDiv.textContent = "";
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
              statusDiv.style.color = "#00cc66";
              localForm.reset();
            } else {
              statusDiv.textContent = `❌ Fehler: ${xhr.responseText}`;
              statusDiv.style.color = "#ff4d4d";
            }
          }, 1000);
        };

        xhr.onerror = () => {
          clearInterval(slowInterval);
          progress.style.display = "none";
          percentLabel.style.display = "none";
          spinner.style.display = "none";
          statusDiv.textContent = `❌ Upload-Fehler`;
          statusDiv.style.color = "#ff4d4d";
        };

        xhr.send(formData);
      } catch (err) {
        clearInterval(slowInterval);
        progress.style.display = "none";
        percentLabel.style.display = "none";
        spinner.style.display = "none";
        statusDiv.textContent = `❌ Fehler: ${err.message}`;
        statusDiv.style.color = "#ff4d4d";
      }
    });
  }
});
