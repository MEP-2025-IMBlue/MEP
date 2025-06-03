const BASE_URL = "http://localhost:8000";  // Backend URL

// Frontend-Logging-Funktion – schickt Fehler an das Backend-Endpoint /frontend-log
function logFrontendError(action, message, level = "ERROR") {
  fetch(`${BASE_URL}/frontend-log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, message, level }),
  }).catch((err) => {
    console.error("Fehler beim Senden des Logs an das Backend:", err);
  });
}

// Führt die Log-Anzeige und Statusabfrage für einen ausgewählten Container aus
async function loadLogs() {
  const containerId = document.getElementById("container-select").value;
  const logOutput = document.getElementById("log-output");
  const statusField = document.getElementById("container-status");
  const healthField = document.getElementById("container-health");

  if (!containerId || containerId === "Please select a container") {
    alert("Please select a valid container.");
    logOutput.textContent = "No container selected.";
    logFrontendError("LogFetch", "No container selected.");
    return;
  }

  const stdout = document.getElementById("chk-stdout").checked;
  const stderr = document.getElementById("chk-stderr").checked;
  const timestamps = document.getElementById("chk-timestamps").checked;
  const tailInput = document.getElementById("log-tail");
  let tail = parseInt(tailInput.value, 10) || 100;

  logOutput.textContent = "Loading logs...";

  try {
    const statusRes = await fetch(`${BASE_URL}/containers/${containerId}/status`);
    const statusData = await statusRes.json();

    statusField.textContent = statusData.status || "unknown";
    healthField.textContent = statusData.health || "undefined";

    healthField.style.color =
      statusData.health === "healthy" ? "green" :
      statusData.health === "unhealthy" ? "red" : "gray";

  } catch (err) {
    statusField.textContent = "Error";
    healthField.textContent = "Error";
    console.error("Error while fetching container status:", err);
    logFrontendError("StatusFetch", err.message);
  }

  try {
    const url = `${BASE_URL}/containers/${containerId}/logs?tail=${tail}&stdout=${stdout}&stderr=${stderr}&timestamps=${timestamps}`;
    const res = await fetch(url);

    if (!res.ok) throw new Error("Failed to fetch logs.");

    const data = await res.json();
    logOutput.textContent = data.logs.length > 0 ? data.logs.join("\n") : "No logs found.";

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
    logOutput.textContent = "Error while fetching logs.";
    console.error("Log fetch error:", err);
    logFrontendError("LogFetch", err.message);
  }
}

// Containerliste beim ersten Laden abrufen
document.addEventListener("DOMContentLoaded", async () => {
  const select = document.getElementById("container-select");

  try {
    const res = await fetch(`${BASE_URL}/containers/list`);
    const data = await res.json();

    select.innerHTML = "";

    const placeholder = document.createElement("option");
    placeholder.text = "Please select a container";
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
    errorOption.text = "Failed to load containers";
    errorOption.disabled = true;
    select.appendChild(errorOption);

    console.error("Error loading container list:", err);
    logFrontendError("ContainerListLoad", err.message);
  }

  const refreshBtn = document.getElementById("refresh-logs");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", loadLogs);
  }

  window.loadLogs = loadLogs;
});
