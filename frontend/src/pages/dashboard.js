document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("ki-image-list");

  async function fetchKIImages() {
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();

      if (data.length === 0) {
        container.innerHTML = "<p>Keine KI-Images vorhanden.</p>";
        return;
      }

      // Tabelle erstellen
      const table = document.createElement("table");
      table.classList.add("ki-image-table");

      const thead = document.createElement("thead");
      thead.innerHTML = `
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Tag</th>
          <th>Hochgeladen am</th>
          <th>Beschreibung</th>
          <th>Aktionen</th>
        </tr>
      `;
      table.appendChild(thead);

      const tbody = document.createElement("tbody");
      data.forEach((img) => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
          <td>${img.image_id}</td>
          <td>${img.image_name}</td>
          <td>${img.tag}</td>
          <td>${formatDateTime(img.created_at)}</td>
          <td>${img.repository || "-"}</td>
          <td>
            <button class="btn-edit" onclick="editImage(${img.image_id})">Bearbeiten</button>
            <button class="btn-delete" onclick="deleteImage(${img.image_id})">Löschen</button>
            <button class="btn-test" onclick="testImage(${img.image_id})">Testen</button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      table.appendChild(tbody);
      container.innerHTML = "";
      container.appendChild(table);
    } catch (err) {
      container.innerHTML = `<p>❌ Fehler beim Laden: ${err.message}</p>`;
    }
  }

  async function deleteImage(id) {
    if (!confirm(`Soll das KI-Image mit ID ${id} wirklich gelöscht werden?`)) return;

    try {
      const res = await fetch(`http://localhost:8000/ki-images/${id}`, {
        method: "DELETE"
      });
      if (!res.ok) throw new Error(await res.text());
      alert("✅ Erfolgreich gelöscht!");
      fetchKIImages(); // Neu laden
    } catch (err) {
      alert("❌ Fehler beim Löschen: " + err.message);
    }
  }

  window.deleteImage = deleteImage;

  window.editImage = function(id) {
    alert("🛠 Bearbeiten noch nicht implementiert. ID: " + id);
    // Hier könntest du z. B. auf eine Bearbeitungsseite weiterleiten
    // window.location.href = `container_bearbeiten.html?id=${id}`;
  };

  window.testImage = function(id) {
    alert("🧪 Test gestartet für Image ID: " + id);
    // Beispielhafter Platzhalter für Test-Funktionalität
  };

  function formatDateTime(dateTimeStr) {
    const dt = new Date(dateTimeStr);
    return dt.toLocaleString("de-DE", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    });
  }

  fetchKIImages();
});
