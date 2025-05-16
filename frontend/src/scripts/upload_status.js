document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("upload-form");
    const statusDiv = document.getElementById("upload-status");
  
    form.addEventListener("submit", function (e) {
      e.preventDefault();
  
      const formData = new FormData(form);
      const xhr = new XMLHttpRequest();
  
      xhr.open("POST", form.getAttribute("action") || "#", true);
  
      xhr.upload.addEventListener("progress", function (e) {
        if (e.lengthComputable) {
          const percent = Math.round((e.loaded / e.total) * 100);
          statusDiv.innerText = `🔄 Wird hochgeladen... ${percent}%`;
        }
      });
  
      xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
          statusDiv.innerText = "✅ Upload erfolgreich!";
          statusDiv.style.color = "#00cc66";
        } else {
          statusDiv.innerText = `❌ Fehler beim Hochladen (${xhr.status})`;
          statusDiv.style.color = "#ff4d4d";
        }
      };
  
      xhr.onerror = function () {
        statusDiv.innerText = "❌ Upload fehlgeschlagen (Verbindungsfehler)";
        statusDiv.style.color = "#ff4d4d";
      };
  
      xhr.send(formData);
      statusDiv.style.color = "#ffd700";
      statusDiv.innerText = "⏳ Upload gestartet...";
    });
  });
  