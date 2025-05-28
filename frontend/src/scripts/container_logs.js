// Wird ausgeführt, sobald das DOM vollständig geladen ist
window.addEventListener("DOMContentLoaded", () => {
  // Referenz auf das <select>-Element
  const select = document.getElementById("container-select");

  // Abruf der Containerliste vom FastAPI-Backend
  fetch("http://localhost:8000/containers/list")
    .then((res) => res.json()) // Antwort in JSON umwandeln
    .then((containers) => {
      // Vorherige Optionen zurücksetzen
      select.innerHTML = "";

      // Erste, nicht auswählbare Platzhalter-Option
      const defaultOption = document.createElement("option");
      defaultOption.text = "Bitte Container wählen";
      defaultOption.disabled = true;
      defaultOption.selected = true;
      select.appendChild(defaultOption);

      // Container-IDs dynamisch als Optionen einfügen
      containers.forEach((id) => {
        const option = document.createElement("option");
        option.value = id;
        option.textContent = id;
        select.appendChild(option);
      });
    })
    .catch((error) => {
      // Fehlerbehandlung: Auswahlfeld mit Fehlermeldung füllen
      select.innerHTML = "";
      const errorOption = document.createElement("option");
      errorOption.text = "Fehler beim Laden der Containerliste";
      errorOption.disabled = true;
      select.appendChild(errorOption);

      // Fehler in der Konsole ausgeben
      console.error("Fehler beim Laden der Containerliste:", error);
    });
});
