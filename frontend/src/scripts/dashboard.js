// Hauptfunktion: Wird ausgeführt, sobald das DOM vollständig geladen ist
document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("ki-image-list");// Container für KI-Image-Tabelle
  const searchInput = document.getElementById("searchInput");// Texteingabe für Filter
  const filterSelect = document.getElementById("filterSelect");// Dropdown für Filterfeld

  let allData = []; // globale Liste aller geladenen KI-Images

  // Funktion zum Laden aller KI-Images vom Backend
  async function fetchKIImages() {
  container.innerHTML = `<p style="color: #fff; padding: 1rem;">Lade KI-Images...</p>`;
  try {
    const res = await fetch("http://localhost:8000/ki-images");
    if (!res.ok) throw new Error(await res.text());
    allData = await res.json();
    console.log("DEBUG: ki-images Daten:", allData);
    container.innerHTML = allData.length === 0
      ? `<p>\u2139\uFE0F Keine KI-Images verfügbar. Lade ein neues Image hoch!</p>`
      : "";
    if (allData.length > 0) renderTable(allData);// Wenn Daten vorhanden: Tabelle anzeigen
  } catch (err) {
    console.log("DEBUG: Fehler in fetchKIImages:", err.message);
    const errorMsg = err.message.includes("keine KI-Bilder")
      ? "\u2139\uFE0F Keine KI-Images verfügbar. Lade ein neues Image hoch!"
      : "\u274C Fehler beim Laden der Images. Bitte später erneut versuchen.";
    container.innerHTML = `<p>${errorMsg}</p>`;
  }
}
// Tabelle dynamisch erzeugen und befüllen
  function renderTable(data) {
    const table = document.createElement("table");
    table.className = "ki-image-table";

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Tag</th>
        <th>Hochgeladen am</th>
        <th>Beschreibung</th>
        <th>Aktionen</th>
        <th>Teststatus</th>
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
          <button class="btn-test" onclick="testContainer(${img.image_id}, '${img.image_name}')">\uD83E\uDDEA testen</button>
        </td>
        <td>
          <span id="test-status-${img.image_id}" class="test-status"></span>
        </td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.innerHTML = "";
    container.appendChild(table);
  }

 // Datum lesbar formatieren (inkl. "heute", "gestern")
function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return "-";

  // Parse die Zeit als UTC (füge "Z" hinzu, falls nicht vorhanden)
  const utcDate = new Date(dateTimeStr.endsWith("Z") ? dateTimeStr : `${dateTimeStr}Z`);
  if (isNaN(utcDate)) return "-";

  // Konvertiere nach Europe/Berlin
  const berlinDate = new Date(utcDate.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));

  // Formatierung für Stunden und Minuten
  const timeStr = berlinDate.toLocaleTimeString("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  });

  // Vergleiche mit aktuellem Datum in Europe/Berlin
  const now = new Date();
  const nowBerlin = new Date(now.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));

  const isSameDay = (date1, date2) =>
    date1.getFullYear() === date2.getFullYear() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate();

  if (isSameDay(berlinDate, nowBerlin)) return `heute, ${timeStr} Uhr`;
  const yesterdayBerlin = new Date(nowBerlin);
  yesterdayBerlin.setDate(nowBerlin.getDate() - 1);
  if (isSameDay(berlinDate, yesterdayBerlin)) return `gestern, ${timeStr} Uhr`;
  return `${berlinDate.toLocaleDateString("de-DE")}, ${timeStr} Uhr`;
}

  // Funktion zum Testen eines Containers
  async function testContainer(imageId, imageName) {
    const statusElement = document.getElementById(`test-status-${imageId}`);

    //Visuelle Statusanzeige aktualisieren
    const updateStatus = (message, status = "info", tooltip = "") => {
      console.log(`DEBUG: Status für Image ${imageName} (ID: ${imageId}): ${message}`);
      if (!statusElement) return;

      statusElement.innerHTML = "";
      const badge = document.createElement("span");
      badge.className = `status-badge status-${status}`;
      badge.textContent = status === "running" ? `\u23F3 ${message}` : status === "success" ? `\u2705 ${message}` : `\u274C ${message}`;

      if (status === "running") {
        const progress = document.createElement("div");
        progress.className = "progress-bar";
        badge.appendChild(progress);
      }

      if (tooltip) {
        const tooltipDiv = document.createElement("div");
        tooltipDiv.className = "tooltip";
        tooltipDiv.textContent = tooltip;
        badge.appendChild(tooltipDiv);
      }

      statusElement.appendChild(badge);
    };

    try {
      //Validierung der imageId
      if (!imageId || isNaN(imageId)) {
        console.log("DEBUG: Ungültige imageId:", imageId);
        throw new Error("Ungültige Image-ID.");
      }

      console.log("DEBUG: allData Inhalt:", allData);
      if (!allData || allData.length === 0) {
        console.log("DEBUG: allData ist leer oder nicht geladen");
        throw new Error("Keine Images geladen. Bitte Seite neu laden.");
      }

      const img = allData.find((i) => i.image_id === parseInt(imageId));
      if (!img) {
        console.log("DEBUG: Image nicht gefunden für imageId:", imageId);
        throw new Error(`Image mit ID ${imageId} nicht gefunden.`);
      }

      const userId = img.image_provider_id;
      if (!userId || isNaN(userId)) {
        console.log("DEBUG: Ungültige userId/image_provider_id:", userId);
        throw new Error("Ungültige Benutzer-ID (image_provider_id).");
      }

      updateStatus("Container wird gestartet...", "running");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const formData = new FormData();
      formData.append("user_id", parseInt(userId));
      formData.append("image_id", parseInt(imageId));
      console.log("DEBUG: FormData POST /containers/start mit: user_id=", userId, "image_id=", imageId);
      const formDataRes = await fetch("http://localhost:8000/containers/start", {
        method: "POST",
        body: formData,
      });
      if (!formDataRes.ok) {
        const formDataErrorText = await formDataRes.text();
        console.log("DEBUG: FormData Fehlerantwort:", formDataErrorText);
        throw new Error(`Start fehlgeschlagen: ${formDataErrorText}`);
      }

      const formDataResult = await formDataRes.json();
      console.log("DEBUG: FormData Start-Antwort:", formDataResult);
      const containerId = formDataResult.container_id;
      if (!containerId) {
        console.log("DEBUG: Keine container_id in FormData-Antwort:", formDataResult);
        throw new Error("Keine Container-ID in der Antwort erhalten.");
      }

      updateStatus("Container läuft...", "running");
      await new Promise((resolve) => setTimeout(resolve, 5000));

      updateStatus("Container wird gestoppt...", "running");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const stopRes = await fetch(`http://localhost:8000/containers/${containerId}/stop`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!stopRes.ok) {
        const errorText = await stopRes.text();
        console.log("DEBUG: Fehlerantwort von POST /containers/.../stop:", errorText);
        throw new Error(`Stoppen fehlgeschlagen: ${errorText}`);
      }

      updateStatus("Container wird gelöscht...", "running");
      const deleteRes = await fetch(`http://localhost:8000/containers/${containerId}`, {
        method: "DELETE",
      });
      if (!deleteRes.ok) {
        const errorText = await deleteRes.text();
        console.log("DEBUG: Fehlerantwort von DELETE /containers/...:", errorText);
        throw new Error(`Löschen fehlgeschlagen: ${errorText}`);
      }
      updateStatus("Test erfolgreich", "success", `Container-ID: ${containerId}`);
    } catch (err) {
      updateStatus("Test fehlgeschlagen", "error", err.message);
      console.log("DEBUG: Fehler in testContainer:", err);
    }
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

  // Löscht KI-Image nach Benutzerbestätigung
  async function deleteImage(id) {
    if (!confirm(`Soll das KI-Image mit ID ${id} wirklich gelöscht werden?`)) return;
    try {
      const res = await fetch(`http://localhost:8000/ki-images/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(await res.text());
      alert("\u2705 Erfolgreich gelöscht!");
      fetchKIImages();// Tabelle neu laden
    } catch (err) {
      alert("\u274C Fehler beim Löschen: " + err.message);
    }
  }
  // Methoden global verfügbar machen
  window.deleteImage = deleteImage;
  window.testContainer = testContainer;
  fetchKIImages();
});