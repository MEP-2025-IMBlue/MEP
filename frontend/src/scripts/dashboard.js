// Wird ausgeführt, sobald das DOM vollständig geladen ist
document.addEventListener("DOMContentLoaded", async () => {
  // DOM-Elemente referenzieren
  const container = document.getElementById("ki-image-list");
  const searchInput = document.getElementById("searchInput");
  const filterSelect = document.getElementById("filterSelect");
  const infoBox = document.getElementById("dashboard-info");
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

  // Event Listener für Start/Stop Button
  container.addEventListener("click", async (event) => {
    if (event.target.classList.contains("btn-toggle")) {
      const btn = event.target;
      const imageId = btn.dataset.id;
      const imageName = btn.dataset.name;
      const currentStatus = btn.dataset.status;
      let containerId = btn.dataset.containerId;

      try {
        const img = allData.find((i) => i.image_id === parseInt(imageId));
        const userId = img.image_provider_id;
        if (!userId) throw new Error("Benutzer-ID nicht verfügbar");

        if (currentStatus === "stopped") {
          // Container STARTEN
          const formData = new FormData();
          formData.append("user_id", userId);
          formData.append("image_id", imageId);

          const res = await fetch("http://localhost:8000/containers/start", {
            method: "POST",
            body: formData,
          });
          if (!res.ok) throw new Error(await res.text());

          const result = await res.json();
          containerId = result.container_id;

          btn.textContent = "\u23F9 Stoppen";
          btn.dataset.status = "running";
          btn.dataset.containerId = containerId;

          // Lokalen Status anpassen
          img.running_container_id = containerId;

          alert("\u2705 Container gestartet (ID: " + containerId + ")");
          renderInfoBox(allData);

        } else {
          // Container STOPPEN

          if (!containerId) throw new Error("Container-ID fehlt");

          // ⏳ Ladeanzeige im Statusfeld
          const statusElement = document.getElementById("test-status-" + imageId);
          if (statusElement) {
            statusElement.innerHTML = `
            <span class="status-badge status-running">
              ⏳ Wird gestoppt...
              <div class="progress-bar"></div>
            </span>
          `;
          }

          // Stop-Anfrage
          const stopRes = await fetch(`http://localhost:8000/containers/${containerId}/stop`, {
            method: "POST",
          });
          if (!stopRes.ok) throw new Error(await stopRes.text());

          // Button anpassen
          btn.textContent = "\u25B6 Starten";
          btn.dataset.status = "stopped";
          delete btn.dataset.containerId;

          // Lokalen Status zurücksetzen
          img.running_container_id = null;

          alert("\u26D4 Container gestoppt");

          // Infobox neu berechnen
          renderInfoBox(allData);

          // Ladeanzeige wieder leeren
          if (statusElement) statusElement.innerHTML = "";
        }

      } catch (err) {
        alert("\u26A0 Fehler: " + err.message);
        console.error("Fehler beim Start/Stopp:", err);
      }
    }
  });


  // Container testen (temporär starten → stoppen → löschen)
  async function testContainer(imageId, imageName) {
    const statusElement = document.getElementById("test-status-" + imageId);
    const updateStatus = (message, status = "info", tooltip = "") => {
      if (!statusElement) return;
      statusElement.innerHTML = "";
      const badge = document.createElement("span");
      badge.className = "status-badge status-" + status;
      badge.textContent = status === "running" ? "\u23F3 " + message : status === "success" ? "\u2705 " + message : "\u274C " + message;
      statusElement.appendChild(badge);
    };

    try {
      const img = allData.find((i) => i.image_id === parseInt(imageId));
      const userId = img.image_provider_id;

      updateStatus("Container wird gestartet...", "running");
      await new Promise((r) => setTimeout(r, 1000));

      const formData = new FormData();
      formData.append("user_id", userId);
      formData.append("image_id", imageId);

      const startRes = await fetch("http://localhost:8000/containers/start", {
        method: "POST",
        body: formData,
      });
      if (!startRes.ok) throw new Error(await startRes.text());

      const startResult = await startRes.json();
      const containerId = startResult.container_id;

      updateStatus("Container läuft...", "running");
      await new Promise((r) => setTimeout(r, 5000));

      await fetch(`http://localhost:8000/containers/${containerId}/stop`, {
        method: "POST",
      });
      await fetch(`http://localhost:8000/containers/${containerId}`, {
        method: "DELETE",
      });

      updateStatus("Test erfolgreich", "success", "Container-ID: " + containerId);
    } catch (err) {
      updateStatus("Test fehlgeschlagen", "error", err.message);
    }
  }

  // Container löschen mit Bestätigung
  async function deleteImage(id) {
    if (!confirm("Soll das KI-Image mit ID " + id + " wirklich gelöscht werden?")) return;
    try {
      const res = await fetch("http://localhost:8000/ki-images/" + id, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(await res.text());
      alert("\u2705 Erfolgreich gelöscht!");
      await fetchKIImages(); // Daten neu laden nach Löschen
    } catch (err) {
      alert("\u274C Fehler beim Löschen: " + err.message);
    }
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

  async function fetchAndDisplaySystemLogs() {
    const infoSection = document.querySelector(".details-card:last-of-type");
    if (!infoSection) return;
  
    const logContainer = document.createElement("pre");
    logContainer.id = "system-log-output";
    logContainer.style.maxHeight = "200px";
    logContainer.style.overflowY = "auto";
    logContainer.style.backgroundColor = "#1c1c1c";
    logContainer.style.color = "#00ffcc";
    logContainer.style.padding = "1rem";
    logContainer.style.fontSize = "0.85rem";
    logContainer.style.border = "1px solid #444";
    logContainer.style.borderRadius = "6px";
    logContainer.textContent = "⏳ Lade Logs...";
    infoSection.appendChild(logContainer);
  
    console.log("🧠 Logfunktion gestartet");
  
    // Warten bis allData gefüllt ist
    if (!Array.isArray(allData) || allData.length === 0) {
      logContainer.textContent = "⚠️ Keine Containerinformationen verfügbar.";
      return;
    }
  
    // Suche ersten Container mit laufendem Zustand
    const activeImage = allData.find((img) => !!img.running_container_id);
    if (!activeImage) {
      logContainer.textContent = "ℹ️ Kein aktiver Container vorhanden.";
      return;
    }
  
    const containerId = activeImage.running_container_id;
    console.log("🚀 Aktiver Container:", containerId);
  
    try {
      const res = await fetch(`http://localhost:8000/containers/${containerId}/logs?tail=50`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      logContainer.textContent = data.logs.length > 0 ? data.logs.join("\n") : "ℹ️ Keine Logs gefunden.";
    } catch (err) {
      logContainer.textContent = "❌ Fehler beim Laden der Logs: " + err.message;
    }
  }
  
    // Logs sofort beim Laden abrufen
    await fetchAndDisplaySystemLogs();
  

});
