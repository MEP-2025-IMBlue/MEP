document.addEventListener("DOMContentLoaded", () => {
    const localForm = document.getElementById("local-upload-form");
    const hubForm = document.getElementById("hub-upload-form");
  
    if (localForm) {
      localForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(localForm);
        const statusDiv = document.getElementById("local-status");
  
        try {
          const res = await fetch("http://localhost:8000/containers/upload-local", {
            method: "POST",
            body: formData
          });
  
          if (res.ok) {
            const result = await res.json();
            statusDiv.textContent = `✅ Hochgeladen: ${result.name || result.container_id}`;
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
  
    if (hubForm) {
      hubForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const imageRef = hubForm.image_reference.value;
        const providerId = hubForm.provider_id.value;
        const statusDiv = document.getElementById("hub-status");
  
        const payload = {
          image_reference: imageRef,
          provider_id: parseInt(providerId)
        };
  
        try {
          const res = await fetch("http://localhost:8000/containers/upload-hub", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
  
          if (res.ok) {
            const result = await res.json();
            statusDiv.textContent = `✅ Referenziert: ${result.name || result.container_id}`;
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
  });
  