document.addEventListener("DOMContentLoaded", () => {
    loadContainers();
    loadKIImages();
  
    const kiForm = document.getElementById("ki-upload-form");
    if (kiForm) {
      kiForm.addEventListener("submit", uploadKIImage);
    }
  });
  
  // -------------------------------
  // 📦 Containerfunktionen
  // -------------------------------
  
  async function loadContainers() {
    const display = document.getElementById("container-list");
    if (!display) return;
  
    display.innerHTML = "Container werden geladen...";
  
    try {
      const res = await fetch("http://localhost:8000/containers");
      const data = await res.json();
  
      if (!data.length) {
        display.innerHTML = "Keine Container gefunden.";
        return;
      }
  
      let html = "<table><tr><th>Name</th><th>Status</th><th>Aktion</th></tr>";
      data.forEach(c => {
        html += `
          <tr>
            <td>${c.name}</td>
            <td>${c.status}</td>
            <td>
              <button onclick="startContainer('${c.container_id}')">▶ Start</button>
              <button onclick="stopContainer('${c.container_id}')">⏸ Stop</button>
              <button onclick="deleteContainer('${c.container_id}')">🗑 Löschen</button>
            </td>
          </tr>`;
      });
      html += "</table>";
      display.innerHTML = html;
    } catch (err) {
      display.innerHTML = `Fehler beim Laden: ${err.message}`;
    }
  }
  
  async function startContainer(id) {
    await fetch(`http://localhost:8000/containers/${id}/start`, { method: "POST" });
    loadContainers();
  }
  
  async function stopContainer(id) {
    await fetch(`http://localhost:8000/containers/${id}/stop`, { method: "POST" });
    loadContainers();
  }
  
  async function deleteContainer(id) {
    if (confirm("Container wirklich löschen?")) {
      await fetch(`http://localhost:8000/containers/${id}`, { method: "DELETE" });
      loadContainers();
    }
  }
  
  // -------------------------------
  // 🧠 KI-Image-Funktionen
  // -------------------------------
  
  async function loadKIImages() {
    const display = document.getElementById("ki-image-list");
    if (!display) return;
  
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      const data = await res.json();
  
      if (!data.length) {
        display.innerHTML = "Keine KI-Images vorhanden.";
        return;
      }
  
      let html = "<table><tr><th>Name</th><th>Tag</th><th>Aktion</th></tr>";
      data.forEach(img => {
        html += `
          <tr>
            <td>${img.image_name}</td>
            <td>${img.image_tag}</td>
            <td>
              <button onclick="deleteKIImage(${img.image_id})">🗑 Löschen</button>
            </td>
          </tr>`;
      });
      html += "</table>";
      display.innerHTML = html;
    } catch (err) {
      display.innerHTML = `Fehler: ${err.message}`;
    }
  }
  
  async function uploadKIImage(e) {
    e.preventDefault();
    const form = e.target;
  
    const payload = {
      image_name: form.image_name.value,
      image_tag: form.image_tag.value,
      description: form.description?.value || null,
      image_path: form.image_path?.value || null,
      local_image_name: form.local_image_name?.value || null,
      provider_id: parseInt(form.provider_id.value)
    };
  
    try {
      const res = await fetch("http://localhost:8000/ki-images", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
  
      if (res.ok) {
        alert("KI-Image erfolgreich hochgeladen");
        form.reset();
        loadKIImages();
      } else {
        const err = await res.text();
        alert("Fehler: " + err);
      }
    } catch (err) {
      alert("Verbindungsfehler: " + err.message);
    }
  }
  
  async function deleteKIImage(id) {
    if (confirm("KI-Image wirklich löschen?")) {
      await fetch(`http://localhost:8000/ki-images/${id}`, { method: "DELETE" });
      loadKIImages();
    }
  }
  