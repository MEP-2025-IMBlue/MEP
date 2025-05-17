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
      const formattedDate = img.image_created_at
        ? formatDateTime(img.image_created_at)
        : "-";
      
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${img.image_id}</td>
        <td>${img.image_name}</td>
        <td>${img.image_tag}</td>
        <td>${formattedDate}</td>
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

  // Zeitstempel formatieren
  function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return "-";

    // Eingabedatum in UTC parsen
    const utcDate = new Date(dateTimeStr);

    // Sicherstellen, dass das Datum gültig ist
    if (isNaN(utcDate)) return "-";

    // Aktuelles Datum in Berlin-Zeit
    const now = new Date();
    const nowBerlin = new Date(
      now.toLocaleString("en-US", { timeZone: "Europe/Berlin" })
    );

    // Eingabedatum in Berlin-Zeit konvertieren
    const berlinDate = new Date(
      utcDate.toLocaleString("en-US", { timeZone: "Europe/Berlin" })
    );

    // Zeit für Anzeige (HH:MM)
    const timeStr = berlinDate.toLocaleTimeString("de-DE", {
      hour: "2-digit",
      minute: "2-digit",
    });

    // Datumsvergleich (nur Jahr, Monat, Tag)
    const isSameDay = (date1, date2) =>
      date1.getFullYear() === date2.getFullYear() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getDate() === date2.getDate();

    // Heute prüfen
    if (isSameDay(berlinDate, nowBerlin)) {
      return `Heute, ${timeStr} Uhr`;
    }

    // Gestern prüfen
    const yesterdayBerlin = new Date(nowBerlin);
    yesterdayBerlin.setDate(nowBerlin.getDate() - 1);
    if (isSameDay(berlinDate, yesterdayBerlin)) {
      return `Gestern, ${timeStr} Uhr`;
    }

    // Standardformat
    return `${berlinDate.toLocaleDateString("de-DE")}, ${timeStr} Uhr`;
  }

  // Filter-Funktion
  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    const field = filterSelect.value;

    const filtered = allData.filter((img) => {
      if (!field) {
        const uploadTime = localStorage.getItem(`uploadTime_${img.image_id}`)?.toLowerCase() || "";
        return (
          img.image_name?.toLowerCase().includes(query) ||
          img.image_tag?.toLowerCase().includes(query) ||
          uploadTime.includes(query)
        );
      }

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

  fetchKIImages();
});