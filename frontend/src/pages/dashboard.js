// -------------------------------
// DOM Ready
// -------------------------------

let imageIdToDelete = null;

document.addEventListener("DOMContentLoaded", () => {
  loadContainers();
  loadKIImages();

  const kiForm = document.getElementById("ki-upload-form");
  if (kiForm) {
    kiForm.addEventListener("submit", uploadKIImage);
  }

  const confirmBtn = document.getElementById("confirm-delete");
  const cancelBtn = document.getElementById("cancel-delete");

  if (confirmBtn && cancelBtn) {
    confirmBtn.addEventListener("click", async () => {
      if (!imageIdToDelete) return;

      try {
        const res = await fetch(`http://localhost:8000/ki-images/${imageIdToDelete}`, {
          method: "DELETE"
        });

        if (res.ok) {
          alert(`KI-Image mit ID ${imageIdToDelete} wurde erfolgreich gelöscht.`);
          loadKIImages();
        } else {
          const err = await res.json();
          alert(`Fehler: ${err.detail || "Unbekannter Fehler beim Löschen"}`);
        }
      } catch (err) {
        alert(`Verbindungsfehler: ${err.message}`);
      }

      imageIdToDelete = null;
      document.getElementById("delete-modal").classList.add("hidden");
    });

    cancelBtn.addEventListener("click", () => {
      imageIdToDelete = null;
      document.getElementById("delete-modal").classList.add("hidden");
    });
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

    let html = "<table><tr><th>Name</th><th>Tag</th><th>Status</th><th>Aktion</th></tr>";
    data.forEach(c => {
      html += `
        <tr>
          <td>${c.name}</td><td>${c.tag || '-'}</td><td>${c.status}</td>
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
let imageIdToDelete = null;

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

    let html = "<table><thead><tr><th>ID</th><th>Name</th><th>Tag</th><th>Beschreibung</th><th>Aktionen</th></tr></thead><tbody>";
    data.forEach(img => {
      html += `<tr>
        <td>${img.image_id}</td>
        <td>${img.image_name}</td>
        <td>${img.image_tag || '-'}</td>
        <td>${img.description || '-'}</td>
        <td class="action-links">
          <span class="edit" onclick="alert('Bearbeiten: ${img.image_id}')">✏ bearbeiten</span> |
          <span class="delete" onclick="deleteKIImage(${img.image_id})">🗑 löschen</span> |
          <span class="test" onclick="alert('Testen: ${img.image_id}')">🧪 testen</span>
        </td>
      </tr>`;
    });
    html += "</tbody></table>";
    display.innerHTML = html;
  } catch (err) {
    display.innerHTML = `<p style="color:red;">Fehler: ${err.message}</p>`;
  }
}

function deleteKIImage(imageId) {
  imageIdToDelete = imageId;
  const modal = document.getElementById("delete-modal");
  if (modal) modal.classList.remove("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
  loadContainers();
  loadKIImages();

  const kiForm = document.getElementById("ki-upload-form");
  if (kiForm) {
    kiForm.addEventListener("submit", uploadKIImage);
  }

  const confirmBtn = document.getElementById("confirm-delete");
  const cancelBtn = document.getElementById("cancel-delete");

  if (confirmBtn && cancelBtn) {
    confirmBtn.addEventListener("click", async () => {
      if (!imageIdToDelete) return;

      try {
        const res = await fetch(`http://localhost:8000/ki-images/${imageIdToDelete}`, {
          method: "DELETE"
        });

        if (res.ok) {
          alert(`KI-Image mit ID ${imageIdToDelete} wurde erfolgreich gelöscht.`);
          loadKIImages();
        } else {
          const err = await res.json();
          alert(`Fehler: ${err.detail || "Unbekannter Fehler beim Löschen"}`);
        }
      } catch (err) {
        alert(`Verbindungsfehler: ${err.message}`);
      }

      imageIdToDelete = null;
      document.getElementById("delete-modal").classList.add("hidden");
    });

    cancelBtn.addEventListener("click", () => {
      imageIdToDelete = null;
      document.getElementById("delete-modal").classList.add("hidden");
    });
  }
});
