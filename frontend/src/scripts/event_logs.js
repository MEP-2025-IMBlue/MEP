document.addEventListener("DOMContentLoaded", () => {
  const logContainer = document.getElementById("log-container");
  const levelSelect = document.getElementById("level-select");
  const sourceSelect = document.getElementById("source-select");
  const actionInput = document.getElementById("action-input");
  const logTableBody = document.getElementById("log-table-body");

  if (!logContainer || !logTableBody) return;

  // Funktion für autorisierte Fetch-Anfragen (mit Keycloak-Token)
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

  // Lädt die Logs mit Filterparametern (Level, Source, Action)
  function loadLogs() {
    const level = levelSelect?.value || "";
    const source = sourceSelect?.value || "";
    const action = actionInput?.value.trim() || "";
    let url = `/logs/events?limit=10`;

    const params = [];
    if (level) params.push(`level=${level}`);
    if (source) params.push(`source=${source}`);
    if (action) params.push(`action=${action}`);
    if (params.length > 0) url += "&" + params.join("&");

    fetchWithAuth(url)
      .then((res) => {
        if (!res.ok) throw new Error("Fehler beim Laden der Logs.");
        return res.json();
      })
      .then((data) => {
        logTableBody.innerHTML = "";
        if (!data.logs || data.logs.length === 0) {
          const row = document.createElement("tr");
          row.innerHTML = `<td colspan="3">Keine Logs verfügbar.</td>`;
          logTableBody.appendChild(row);
        } else {
          data.logs.forEach((log) => {
            const row = document.createElement("tr");
            row.innerHTML = `
              <td>${log.timestamp || "-"}</td>
              <td>${log.level || "-"}</td>
              <td>${log.message || "-"}</td>
            `;
            logTableBody.appendChild(row);
          });
        }
      })
      .catch((err) => {
        console.error(err);
        logTableBody.innerHTML = `<tr><td colspan="3">Fehler beim Laden der Logs.</td></tr>`;
      });
  }

  //  Filteränderung → lädt automatisch neue Logs
  [levelSelect, sourceSelect, actionInput].forEach(el => {
    if (el) el.addEventListener("change", loadLogs);
    if (el?.tagName === "INPUT") el.addEventListener("input", loadLogs);
  });

  // ⏱ Automatische Aktualisierung alle 30 Sekunden
  setInterval(loadLogs, 30000);

  // Initialer Ladevorgang
  loadLogs();
});
