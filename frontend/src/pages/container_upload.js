document.addEventListener("DOMContentLoaded", () => {
  const hubForm = document.getElementById("hub-upload-form");
  const localForm = document.getElementById("local-upload-form");

  if (hubForm) {
    hubForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData(hubForm);
      const statusDiv = document.getElementById("hub-status");

      try {
        const res = await fetch("http://localhost:8000/ki-images/hub", {
          method: "POST",
          body: formData
        });

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
        statusDiv.textContent = `❌ Verbindungsfehler: ${err.message}`;
        statusDiv.style.color = "#ff4d4d";
      }
    });
  }

  if (localForm) {
    localForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData(localForm);
      const statusDiv = document.getElementById("local-status");

      try {
        const res = await fetch("http://localhost:8000/ki-images/local", {
          method: "POST",
          body: formData
        });

        if (res.ok) {
          const result = await res.json();
          statusDiv.textContent = `✅ Hochgeladen: ${result.image_name || result.id}`;
          statusDiv.style.color = "#00cc66";
          localForm.reset();
        } else {
          const errText = await res.text();
          statusDiv.textContent = `❌ Fehler: ${errText}`;
          statusDiv.style.color = "#ff4d4d";
        }
      } catch (err) {
        statusDiv.textContent = `❌ Verbindungsfehler: ${err.message}`;
        statusDiv.style.color = "#ff4d4d";
      }
    });
  }
});
