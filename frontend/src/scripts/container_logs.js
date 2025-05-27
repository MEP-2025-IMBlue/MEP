// Lädt die Liste aller laufenden Container beim Laden der Seite
window.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("container-select");

  fetch("http://localhost:8000/containers/list")
    .then((res) => res.json())
    .then((containers) => {
      select.innerHTML = ""; // Entfernt die Ladeoption
      containers.forEach((c) => {
        const option = document.createElement("option");
        option.value = c.container_id;
        option.textContent = c.container_id.substring(0, 12); // Zeigt nur die ersten 12 Zeichen der ID
        select.appendChild(option);
      });
    })
    .catch((err) => {
      select.innerHTML = "<option>Fehler beim Laden</option>";
      console.error("Fehler beim Abrufen der Containerliste:", err);
    });
});

// Holt die Logs des ausgewählten Containers und zeigt sie an
function loadLogs() {
  const id = document.getElementById("container-select").value;
  const output = document.getElementById("log-output");
  output.textContent = "Lade Logs...";

  fetch(`http://localhost:8000/containers/${id}/logs?tail=100`)
    .then((res) => {
      if (!res.ok) throw new Error("Serverfehler");
      return res.json();
    })
    .then((data) => {
      output.textContent = data.logs.join("\n");
    })
    .catch((err) => {
      output.textContent = "Fehler: " + err;
    });
}
