const BASE_URL = "http://localhost:8000";

// Hilfsfunktion: Autorisierte Fetch-Anfrage mit Keycloak-Token im Header
function fetchWithAuth(url, options = {}) {
  const token = sessionStorage.getItem("kc_token");
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  });
}

// Frontend-Logging-Funktion – sendet Fehler an das Backend-Endpoint /frontend-log
function logFrontendError(action, message, level = "ERROR") {
  fetchWithAuth(`${BASE_URL}/frontend-log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, message, level }),
  }).catch((err) => {
    console.error("Fehler beim Senden des Logs an das Backend:", err);
  });
}

// Lädt die Logs und den Status eines ausgewählten Containers
async function loadLogs() {
  const containerId = document.getElementById("container-select").value;
  const logOutput = document.getElementById("log-output");
  const statusField = document.getElementById("container-status");
  const healthField = document.getElementById("container-health");

  if (!containerId || containerId === "Please select a container") {
    alert("Bitte wähle einen gültigen Container aus.");
    logOutput.textContent = "Kein Container ausgewählt.";
    logFrontendError("LogFetch", "Kein Container ausgewählt.");
    return;
  }

  const stdout = document.getElementById("chk-stdout").checked;
  const stderr = document.getElementById("chk-stderr").checked;
  const timestamps = document.getElementById("chk-timestamps").checked;
  const tailInput = document.getElementById("log-tail");
  let tail = parseInt(tailInput.value, 10) || 100;

  logOutput.textContent = "Lade Container-Logs...";

  try {
    const statusRes = await fetchWithAuth(`${BASE_URL}/containers/${containerId}/status`);
    const statusData = await statusRes.json();

    statusField.textContent = statusData.status || "unbekannt";
    healthField.textContent = statusData.health || "undefiniert";

    healthField.style.color =
      statusData.health === "healthy" ? "green" :
      statusData.health === "unhealthy" ? "red" : "gray";

  } catch (err) {
    statusField.textContent = "Fehler";
    healthField.textContent = "Fehler";
    console.error("Fehler beim Abrufen des Container-Status:", err);
    logFrontendError("StatusFetch", err.message);
  }

  try {
    const url = `${BASE_URL}/containers/${containerId}/logs?tail=${tail}&stdout=${stdout}&stderr=${stderr}&timestamps=${timestamps}`;
    const res = await fetchWithAuth(url);

    if (!res.ok) throw new Error("Fehler beim Abrufen der Logs.");

    const data = await res.json();
    logOutput.textContent = data.logs.length > 0 ? data.logs.join("\n") : "Keine Logs gefunden.";

    const moreBtn = document.getElementById("load-more-logs");
    if (data.logs.length > 0 && moreBtn) {
      moreBtn.style.display = "inline-block";
      moreBtn.onclick = () => {
        tail += 100;
        tailInput.value = tail;
        loadLogs();
      };
    }

  } catch (err) {
    logOutput.textContent = "Fehler beim Abrufen der Logs.";
    console.error("Fehler beim Log-Abruf:", err);
    logFrontendError("LogFetch", err.message);
  }
}

// Lädt die System-Logs (Event-Logger) als Tabelle und zeigt sie im Dashboard an
async function loadSystemLogsTable() {
  const logCount = 50;
  const tbody = document.getElementById("log-table-body");
  tbody.innerHTML = "<tr><td colspan='3'>Lade Logs...</td></tr>";

  try {
    const level = document.getElementById("level-select")?.value;
    const source = document.getElementById("source-select")?.value;
    const action = document.getElementById("action-input")?.value;

    let url = `${BASE_URL}/logs/events?limit=${logCount}`;
    if (level) url += `&level=${encodeURIComponent(level)}`;
    if (source) url += `&source=${encodeURIComponent(source)}`;
    if (action) url += `&action=${encodeURIComponent(action)}`;

    const res = await fetchWithAuth(url);
    const data = await res.json();

    if (!data.logs || !data.logs.length) {
      tbody.innerHTML = "<tr><td colspan='3'>Keine Logs gefunden.</td></tr>";
      return;
    }

    tbody.innerHTML = "";
    data.logs.forEach(log => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${log.timestamp || ""}</td>
        <td>${log.level || ""}</td>
        <td>${log.message || ""}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = "<tr><td colspan='3'>Fehler beim Laden der Logs.</td></tr>";
    logFrontendError("SystemLogFetch", err.message);
  }
}

// DOM hazır olduğunda işlemleri başlat
document.addEventListener("DOMContentLoaded", async () => {
  const select = document.getElementById("container-select");

  try {
    const res = await fetchWithAuth(`${BASE_URL}/containers/list`);
    const data = await res.json();

    if (!Array.isArray(data)) {
      throw new Error("Backend-Fehler: '/containers/list' hat kein Array zurückgegeben.");
    }

    select.innerHTML = "";

    const placeholder = document.createElement("option");
    placeholder.text = (typeof i18n !== "undefined" && i18n.translations["select_placeholder"]) || "Bitte Container auswählen";
    placeholder.disabled = true;
    placeholder.selected = true;
    select.appendChild(placeholder);

    data.forEach(id => {
      const opt = document.createElement("option");
      opt.value = id;
      opt.textContent = id;
      select.appendChild(opt);
    });

    const logOutputEl = document.getElementById("log-output");
    if (logOutputEl && !document.getElementById("load-more-logs")) {
      const loadMoreBtn = document.createElement("button");
      loadMoreBtn.id = "load-more-logs";
      loadMoreBtn.style.display = "none";
      loadMoreBtn.style.marginTop = "10px";
      loadMoreBtn.setAttribute("data-i18n-key", "log_button_more");
      loadMoreBtn.textContent = (typeof i18n !== "undefined" && i18n.translations["log_button_more"]) || "🔁 Mehr anzeigen";
      logOutputEl.parentNode.insertBefore(loadMoreBtn, logOutputEl.nextSibling);
    }

  } catch (err) {
    select.innerHTML = "";
    const errorOption = document.createElement("option");
    errorOption.text = (typeof i18n !== "undefined" && i18n.translations["container_list_error"]) || "Fehler beim Laden der Containerliste";
    errorOption.disabled = true;
    select.appendChild(errorOption);

    console.error("Fehler beim Laden der Containerliste:", err);
    logFrontendError("ContainerListLoad", err.message);
  }

  loadSystemLogsTable();

  const refreshBtn = document.getElementById("refresh-logs");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      loadLogs();
      loadSystemLogsTable();
    });
  }

  window.loadLogs = loadLogs;
  window.loadSystemLogsTable = loadSystemLogsTable;

  ["level-select", "source-select", "action-input"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", loadSystemLogsTable);
      if (id === "action-input") el.addEventListener("input", loadSystemLogsTable);
    }
  });
});
