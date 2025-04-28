document.getElementById("submit").addEventListener("click", function (event) {
  event.preventDefault(); // Wichtig, verhindert Standardverhalten wie Form-Submit

  const rolle = document.getElementById("Rolle").value;
  const errorMessage = document.getElementById("error-message");

  if (rolle !== "admin") {
    errorMessage.style.display = "inline"; // Zeige Fehlermeldung
  } else {
    errorMessage.style.display = "none";  // Verstecke Fehlermeldung
    window.location.href = "dicom_upload.html"; // Weiterleitung nur für Admins
  }
});


// Optional: Skript, um die Datei und den Button für die Eingabe zu handhaben (falls du es brauchst)
document.getElementById("file-input").addEventListener("change", function(event) {
  const fileName = event.target.files[0] ? event.target.files[0].name : "Keine Datei ausgewählt";
  document.getElementById("file-label").textContent = fileName;
});
document.getElementById("input-text").addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    event.preventDefault(); // verhindert Zeilenumbruch
    document.getElementById("send-button").click(); // klickt den Senden-Button
  }
});


function toggleMenu() {
  const menu = document.getElementById("menu");
  
  // Menü-Items ein- oder ausblenden
  if (menu.style.display === "none" || menu.style.display === "") {
    menu.style.display = "flex"; // Zeige das Menü an, wenn es verborgen ist
  } else {
    menu.style.display = "none"; // Verberge das Menü, wenn es sichtbar ist
  }
}
//47.1
// Beispiel-Daten
const containerData = [
  { name: "CT_Analyse", image: "ct_image", version: "1.2.3", date: "2024-12-01", status: "Aktiv" },
  { name: "MRI_Konvertierer", image: "mri_tool", version: "2.0.0", date: "2025-01-15", status: "Inaktiv" },
  { name: "PET_Filter", image: "pet_filter", version: "0.9.8", date: "2024-11-23", status: "Aktiv" }
];

// Container-Tabelle befüllen
function loadContainerTable() {
  const tbody = document.getElementById("containerBody");
  tbody.innerHTML = "";

  containerData.forEach((container, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${container.name}</td>
      <td>${container.image}</td>
      <td>${container.version}</td>
      <td>${container.date}</td>
      <td>${container.status}</td>
      <td><button onclick="viewLogs(${index})">Logs</button></td>
    `;
    tbody.appendChild(row);
  });
}

// Filterfunktion
function filterTable() {
  const input = document.getElementById("searchInput").value.toLowerCase();
  const rows = document.querySelectorAll("#containerTable tbody tr");

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(input) ? "" : "none";
  });
}

// Logs anzeigen (optional)
function viewLogs(index) {
  alert(`Zeige Logs für Container: ${containerData[index].name}`);
}

// Klick auf "Container bearbeiten"
document.addEventListener("DOMContentLoaded", () => {
  const containerLink = document.querySelector("#menu a:nth-child(3)");
  containerLink.addEventListener("click", (e) => {
    e.preventDefault();
    document.getElementById("containerSection").style.display = "block";
    loadContainerTable();
  });
});