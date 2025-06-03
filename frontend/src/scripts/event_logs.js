// 📋 Event Logs abrufen und anzeigen
document.addEventListener("DOMContentLoaded", () => {
  const logContainer = document.getElementById("log-container");
  if (!logContainer) return;

  fetch("/logs/events?limit=10")
    .then((response) => {
      if (!response.ok) throw new Error("Fehler beim Laden der Logs.");
      return response.json();
    })
    .then((data) => {
      logContainer.innerHTML = "";
      if (data.logs.length === 0) {
        logContainer.textContent = "Keine Logs verfügbar.";
      } else {
        data.logs.forEach((logLine) => {
          const p = document.createElement("p");
          p.textContent = logLine;
          logContainer.appendChild(p);
        });
      }
    })
    .catch((error) => {
      logContainer.textContent = "Fehler beim Laden der Logs.";
      console.error(error);
    });
});
