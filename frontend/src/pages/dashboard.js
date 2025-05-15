document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("ki-image-list");
  const searchInput = document.getElementById("searchInput");
  const filterSelect = document.getElementById("filterSelect");

  let allData = []; // wird global gespeichert

  async function fetchKIImages() {
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      if (!res.ok) throw new Error(await res.text());
      allData = await res.json(); // global speichern
      renderTable(allData); // initial anzeigen
    } catch (err) {
      container.innerHTML = `<p>❌ Fehler beim Laden: ${err.message}</p>`;
    }
  }

  function renderTable(data) {
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
        <td>${img.image_tag}</td>
        <td>${formatDateTime(localStorage.getItem(`uploadTime_${img.image_id}`) || new Date())}</td>
        <td>${img.repository || "-"}</td>
        <td>
          <button class="btn-edit" onclick="alert('Bearbeiten: ${img.image_id}')">✏ bearbeiten</button> |
          <button class="btn-delete" onclick="deleteImage(${img.image_id})">🗑 löschen</button> |
          <button class="btn-test" onclick="alert('Testen: ${img.image_id}')">🧪 testen</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.innerHTML = "";
    container.appendChild(table);
  }

  //filter funktion
  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    const field = filterSelect.value;

    const filtered = allData.filter((img) => {
      // Wenn kein Filter gewählt ist: Suche in allen Feldern
      if (!field) {
        const uploadTime = localStorage.getItem(`uploadTime_${img.image_id}`)?.toLowerCase() || "";
        return (
          img.image_name?.toLowerCase().includes(query) ||
          img.image_tag?.toLowerCase().includes(query) ||
          uploadTime.includes(query)
        );
      }

      // Mit gesetztem Filter
      if (field === "created_at") {
        const uploadTime = localStorage.getItem(`uploadTime_${img.image_id}`);
        return uploadTime?.toLowerCase().includes(query);
      }

      return img[field]?.toLowerCase().includes(query);
    });

    renderTable(filtered);
  });



  async function deleteImage(id) {
    if (!confirm(`Soll das KI-Image mit ID ${id} wirklich gelöscht werden?`)) return;
    try {
      const res = await fetch(`http://localhost:8000/ki-images/${id}`, {
        method: "DELETE"
      });
      if (!res.ok) throw new Error(await res.text());
      alert("✅ Erfolgreich gelöscht!");
      fetchKIImages(); // aktualisieren
    } catch (err) {
      alert("❌ Fehler beim Löschen: " + err.message);
    }
  }

  window.deleteImage = deleteImage;

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
