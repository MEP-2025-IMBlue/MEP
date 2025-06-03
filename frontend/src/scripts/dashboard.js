// Wird ausgeführt, sobald das DOM vollständig geladen ist
document.addEventListener("DOMContentLoaded", async () => {
  // DOM-Elemente referenzieren
  const container = document.getElementById("ki-image-list");
  const searchInput = document.getElementById("searchInput");
  const filterSelect = document.getElementById("filterSelect");
  const infoBox = document.getElementById("dashboard-info");
  const logOutput = document.getElementById("system-log-output");
  const logCountInput = document.getElementById("log-count");
  const refreshButton = document.getElementById("refresh-logs");
  let allData = []; // globale Liste aller KI-Images

  // Daten vom Backend laden
  async function fetchKIImages() {
    container.innerHTML = "<p style='color: #fff; padding: 1rem;'>Lade KI-Images...</p>";
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      if (!res.ok) throw new Error(await res.text());
      allData = await res.json();
      container.innerHTML = allData.length === 0
        ? "<p>&#8505;&#xFE0F; Keine KI-Images verfügbar. Lade ein neues Image hoch!</p>"
        : "";
      if (allData.length > 0) renderTable(allData);
    } catch (err) {
      console.log("Fehler beim Laden:", err.message);
      const errorMsg = err.message.includes("keine KI-Bilder")
        ? "&#8505;&#xFE0F; Keine KI-Images verfügbar. Lade ein neues Image hoch!"
        : "&#10060; Fehler beim Laden der Images. Bitte später erneut versuchen.";
      container.innerHTML = "<p>" + errorMsg + "</p>";
    }
  }

  // Tabelle dynamisch erzeugen
  function renderTable(data) {
    const table = document.createElement("table");
    table.className = "ki-image-table";

    // Tabellenkopf
    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Tag</th>
        <th>Hochgeladen am</th>
        <th>Beschreibung</th>
        <th>Aktionen</th>
        <th>Status</th>
      </tr>
    `;
    table.appendChild(thead);

    // Tabellendaten
    const tbody = document.createElement("tbody");
    data.forEach((img) => {
      const formattedDate = img.image_created_at ? formatDateTime(img.image_created_at) : "-";
      const containerId = img.running_container_id || null;
      const isRunning = !!containerId;
      const toggleText = isRunning ? "\u23F9 Stoppen" : "\u25B6 Starten";
      const toggleStatus = isRunning ? "running" : "stopped";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${img.image_id}</td>
        <td>${img.image_name}</td>
        <td>${img.image_tag}</td>
        <td>${formattedDate}</td>
        <td>${img.repository || "-"}</td>
        <td>
          <button class="btn-edit" onclick="alert('Bearbeiten: ${img.image_id}')">✏ bearbeiten</button> |
          <button class="btn-delete" onclick="deleteImage(${img.image_id})">\uD83D\uDDD1 löschen</button> |
          <button class="btn-test" onclick="testContainer(${img.image_id}, '${img.image_name}')">\uD83E\uDDEA testen</button> |
          <button class="btn-toggle"
                  data-id="${img.image_id}"
                  data-name="${img.image_name}"
                  data-status="${toggleStatus}"
                  ${containerId ? `data-container-id="${containerId}"` : ""}>
              ${toggleText}
          </button>
        </td>
        <td><span id="test-status-${img.image_id}" class="test-status"></span></td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.innerHTML = "";
    container.appendChild(table);

    // Infobox unterhalb aktualisieren
    renderInfoBox(data);
  }

  // Infobox mit Gesamt-, Aktiv- und Inaktiv-Zählung anzeigen
  function renderInfoBox(data) {
    if (!infoBox) return;
    const active = data.filter((img) => !!img.running_container_id).length;
    const total = data.length;
    const inactive = total - active;

    infoBox.innerHTML = `
      <div class="dashboard-info">
        <strong>&#128230; Gesamt:</strong> ${total} |
        <span style="color:#28a745"><strong>&#128994; Aktiv:</strong> ${active}</span> |
        <span style="color:#ff4d4d"><strong>&#128308; Inaktiv:</strong> ${inactive}</span>
      </div>
    `;
  }

  // Datum lesbar formatieren (inkl. heute/gestern)
  function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return "-";
    const utcDate = new Date(dateTimeStr.endsWith("Z") ? dateTimeStr : `${dateTimeStr}Z`);
    if (isNaN(utcDate)) return "-";
    const berlinDate = new Date(utcDate.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));
    const timeStr = berlinDate.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
    const now = new Date();
    const nowBerlin = new Date(now.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));
    const isSameDay = (d1, d2) => d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getDate() === d2.getDate();
    const yesterdayBerlin = new Date(nowBerlin); yesterdayBerlin.setDate(nowBerlin.getDate() - 1);
    if (isSameDay(berlinDate, nowBerlin)) return `heute, ${timeStr} Uhr`;
    if (isSameDay(berlinDate, yesterdayBerlin)) return `gestern, ${timeStr} Uhr`;
    return `${berlinDate.toLocaleDateString("de-DE")}, ${timeStr} Uhr`;
  }

  // Systemlogs anzeigen (nach Tail Count)
  async function fetchAndDisplaySystemLogs(count = 5) {
    if (!logOutput) return;
    logOutput.textContent = "⏳ Lade Logs...";

    if (!Array.isArray(allData) || allData.length === 0) {
      logOutput.textContent = "⚠️ Keine Containerinformationen verfügbar.";
      return;
    }

    const activeImage = allData.find((img) => !!img.running_container_id);
    if (!activeImage) {
      logOutput.textContent = "ℹ️ Kein aktiver Container vorhanden.";
      return;
    }

    const containerId = activeImage.running_container_id;
    try {
      const res = await fetch(`http://localhost:8000/containers/${containerId}/logs?tail=${count}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      logOutput.textContent = data.logs.length > 0 ? data.logs.join("\n") : "ℹ️ Keine Logs gefunden.";
    } catch (err) {
      logOutput.textContent = "❌ Fehler beim Laden der Logs: " + err.message;
    }
  }

  // Log-Refresh Button mit Tail Count verbinden
  if (refreshButton && logCountInput) {
    refreshButton.addEventListener("click", () => {
      const count = parseInt(logCountInput.value, 10) || 5;
      fetchAndDisplaySystemLogs(count);
    });
  }

  // Filterfunktion für Suchleiste
  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    const field = filterSelect.value;

    const filtered = allData.filter((img) => {
      const uploadTime = localStorage.getItem("uploadTime_" + img.image_id)?.toLowerCase() || "";
      if (!field) {
        return (
          img.image_name?.toLowerCase().includes(query) ||
          img.image_tag?.toLowerCase().includes(query) ||
          uploadTime.includes(query)
        );
      }
      if (field === "created_at") return uploadTime.includes(query);
      return img[field]?.toLowerCase().includes(query);
    });

    renderTable(filtered);
  });

  // Globale Methoden bereitstellen
  window.deleteImage = deleteImage;
  window.testContainer = testContainer;

  // Initiales Laden
  await fetchKIImages();
  await fetchAndDisplaySystemLogs();
});
