// Führt den Code aus, sobald das DOM vollständig geladen ist
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("upload-form");// Referenz auf das Formular
    const statusDiv = document.getElementById("upload-status");// Element für Statusanzeige

    // Event-Handler für das Absenden des Formulars
    form.addEventListener("submit", function (e) {
      e.preventDefault();// Standardverhalten (Seitenreload) verhindern
  
      const formData = new FormData(form);// Formulardaten vorbereiten
      const xhr = new XMLHttpRequest();// Neues XMLHttpRequest-Objekt

      // Ziel-URL aus dem Formular-Attribut „action“ oder als Platzhalter („#“)
      xhr.open("POST", form.getAttribute("action") || "#", true);

      // Zeigt den Fortschritt während des Uploads
      xhr.upload.addEventListener("progress", function (e) {
        if (e.lengthComputable) {
          const percent = Math.round((e.loaded / e.total) * 100);// Prozentzahl berechnen
          statusDiv.innerText = `\u{1F504} Wird hochgeladen... ${percent}%`;// Status aktualisieren
        }
      });
      // Wird ausgelöst, wenn der Upload abgeschlossen ist
      xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) {
          statusDiv.innerText = "\u2705 Upload erfolgreich!";
          statusDiv.style.color = "#00cc66";
        } else {
          statusDiv.innerText = `\u274C Fehler beim Hochladen (${xhr.status})`;
          statusDiv.style.color = "#ff4d4d";
        }
      };

       // Wird ausgelöst, wenn die Verbindung fehlschlägt
      xhr.onerror = function () {
        statusDiv.innerText = "\u274C Upload fehlgeschlagen (Verbindungsfehler)";
        statusDiv.style.color = "#ff4d4d";
      };
      // Starte den Upload
      xhr.send(formData);
      // Initiale Anzeige beim Start des Uploads
      statusDiv.style.color = "#ffd700";
      statusDiv.innerText = "\u23F3 Upload gestartet...";
    });
  });
  