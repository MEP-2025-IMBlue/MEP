// Wird ausgeführt, sobald das DOM vollständig geladen ist
// Erweiterung: Unterstützung für Mehrsprachigkeit (i18n)
document.addEventListener("DOMContentLoaded", async () => {
  // DOM-Elemente referenzieren
  const container = document.getElementById("ki-image-list");
  const searchInput = document.getElementById("searchInput");
  const filterSelect = document.getElementById("filterSelect");
  const infoBox = document.getElementById("dashboard-info");
  const logOutput = document.getElementById("system-log-output");
  const logCountInput = document.getElementById("log-count");
  const refreshButton = document.getElementById("refresh-logs");
  const langBtn = document.getElementById("lang-toggle-btn");
  let allData = []; // globale Liste aller KI-Images

  // i18n: Übersetzungen laden und anwenden
  await i18n.loadTranslations(i18n.currentLang);
  i18n.applyTranslations();

  // Sprache-Umschalt-Button initialisieren
  if (langBtn) {
    langBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";
    langBtn.addEventListener("click", () => {
      i18n.toggleLang();
    });
  }

  // Bei Sprachwechsel Übersetzungen neu anwenden
  window.addEventListener("languageChanged", () => {
    i18n.applyTranslations();
    fetchKIImages();
    if (filterSelect) {
      filterSelect.innerHTML = `
        <option value="">${i18n.translations.dashboard_filter_option}</option>
        <option value="image_name">${i18n.translations.name}</option>
        <option value="image_tag">${i18n.translations.tag}</option>
        <option value="created_at">${i18n.translations.uploaded_at}</option>
      `;
    }
    if (searchInput) {
      searchInput.placeholder = i18n.translations.dashboard_filter_placeholder;
    }
    if (langBtn) {
      langBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";
    }
  });

  // Daten vom Backend laden
  async function fetchKIImages() {
    container.innerHTML = `<p style='color: #fff; padding: 1rem;'>${i18n.translations.loading_ki_images}</p>`;
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      if (!res.ok) throw new Error(await res.text());
      allData = await res.json();
      container.innerHTML = allData.length === 0
        ? `<p>&#8505;&#xFE0F; ${i18n.translations.no_ki_images}</p>`
        : "";
      if (allData.length > 0) renderTable(allData);
    } catch (err) {
      container.innerHTML = `<p>&#10060; ${i18n.translations.load_images_error}</p>`;
    }
  }

  // Tabelle dynamisch erzeugen
  function renderTable(data) {
    const table = document.createElement("table");
    table.className = "ki-image-table";

    // Tabellenkopf mit Übersetzungen
    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>${i18n.translations.id}</th>
        <th>${i18n.translations.name}</th>
        <th>${i18n.translations.tag}</th>
        <th>${i18n.translations.uploaded_at}</th>
        <th>${i18n.translations.description}</th>
        <th>${i18n.translations.actions}</th>
        <th>${i18n.translations.test_status}</th>
      </tr>
    `;
    table.appendChild(thead);

    // Tabellendaten
    const tbody = document.createElement("tbody");
    data.forEach((img) => {
      const formattedDate = img.image_created_at ? formatDateTime(img.image_created_at) : "-";
      const containerId = img.running_container_id || null;
      const isRunning = !!containerId;
      const toggleText = isRunning ? i18n.translations.stop : i18n.translations.start;
      const toggleStatus = isRunning ? "running" : "stopped";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${img.image_id}</td>
        <td>${img.image_name}</td>
        <td>${img.image_tag}</td>
        <td>${formattedDate}</td>
        <td>${img.repository || "-"}</td>
        <td>
          <button class="btn-edit" onclick="alert('Bearbeiten: ${img.image_id}')">✏ ${i18n.translations.edit}</button> |
          <button class="btn-delete" onclick="deleteImage(${img.image_id})">🗑 ${i18n.translations.delete}</button> |
          <button class="btn-test" onclick="testContainer(${img.image_id}, '${img.image_name}')">🧪 ${i18n.translations.test}</button> |
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

    // Infobox aktualisieren
    renderInfoBox(data);
  }

  // Infobox mit Zählung anzeigen
  function renderInfoBox(data) {
    if (!infoBox) return;
    const active = data.filter((img) => !!img.running_container_id).length;
    const total = data.length;
    const inactive = total - active;

    infoBox.innerHTML = `
      <div class="dashboard-info">
        <strong>&#128230; ${i18n.translations.dashboard_total}:</strong> ${total} |
        <span style="color:#28a745"><strong>&#128994; ${i18n.translations.dashboard_active}:</strong> ${active}</span> |
        <span style="color:#ff4d4d"><strong>&#128308; ${i18n.translations.dashboard_inactive}:</strong> ${inactive}</span>
      </div>
    `;
  }

  // Datum formatieren mit Unterstützung für heute/gestern in aktueller Sprache
  function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return "-";
    const utcDate = new Date(dateTimeStr.endsWith("Z") ? dateTimeStr : `${dateTimeStr}Z`);
    if (isNaN(utcDate)) return "-";
    const berlinDate = new Date(utcDate.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));
    const timeStr = berlinDate.toLocaleTimeString(i18n.currentLang === "de" ? "de-DE" : "en-GB", { hour: "2-digit", minute: "2-digit" });
    const now = new Date();
    const nowBerlin = new Date(now.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));
    const isSameDay = (d1, d2) => d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth() && d1.getDate() === d2.getDate();
    const yesterdayBerlin = new Date(nowBerlin);
    yesterdayBerlin.setDate(nowBerlin.getDate() - 1);
    if (isSameDay(berlinDate, nowBerlin)) return `${i18n.translations.today}, ${timeStr} ${i18n.translations.clock}`;
    if (isSameDay(berlinDate, yesterdayBerlin)) return `${i18n.translations.yesterday}, ${timeStr} ${i18n.translations.clock}`;
    return `${berlinDate.toLocaleDateString(i18n.currentLang === "de" ? "de-DE" : "en-GB")}, ${timeStr} ${i18n.translations.clock}`;
  }

  // Logs anzeigen (mit Tail Count)
  async function fetchAndDisplaySystemLogs(count = 5) {
    if (!logOutput) return;
    logOutput.textContent = `⏳ ${i18n.translations.loading_logs}`;

    if (!Array.isArray(allData) || allData.length === 0) {
      logOutput.textContent = `⚠️ ${i18n.translations.no_container_info}`;
      return;
    }

    const activeImage = allData.find((img) => !!img.running_container_id);
    if (!activeImage) {
      logOutput.textContent = `ℹ️ ${i18n.translations.no_active_container}`;
      return;
    }

    const containerId = activeImage.running_container_id;
    try {
      const res = await fetch(`http://localhost:8000/containers/${containerId}/logs?tail=${count}`);
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      logOutput.textContent = data.logs.length > 0 ? data.logs.join("\n") : `ℹ️ ${i18n.translations.no_logs_found}`;
    } catch (err) {
      logOutput.textContent = `❌ ${i18n.translations.load_logs_error}: ${err.message}`;
    }
  }

  // Button zum Neuladen der Logs (mit Tail Count)
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

  // 🔁 Funktion zum Löschen eines KI-Images
  async function deleteImage(imageId) {
    const bestätigen = confirm(`${i18n.translations.confirm_delete} ${imageId}?`);
    if (!bestätigen) return;
    try {
      const res = await fetch(`http://localhost:8000/ki-images/${imageId}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(await res.text());
      alert(`✅ ${i18n.translations.successfully_deleted}`);
      await fetchKIImages();
    } catch (err) {
      alert(`❌ ${i18n.translations.delete_failed}: ${err.message}`);
    }
  }

  // Globale Methoden verfügbar machen
  window.deleteImage = deleteImage;
  window.testContainer = testContainer;

  // Initiales Laden
  await fetchKIImages();
  await fetchAndDisplaySystemLogs();
});
