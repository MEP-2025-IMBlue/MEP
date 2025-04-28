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

// liste der KIS
/*

document.getElementById('send-button').addEventListener('click', function() {
  const fileInput = document.getElementById('file-input');
  const kiList = document.getElementById('ki-list');

  if (fileInput.files.length > 0) {
    // Für jede hochgeladene Datei füge einen neuen Eintrag hinzu
    for (let i = 0; i < fileInput.files.length; i++) {
      const file = fileInput.files[i];
      const option = document.createElement('option');
      option.text = file.name;  // Anzeigename = Dateiname
      option.value = file.name;
      kiList.appendChild(option);
    }

    // Optional: Datei-Eingabefeld wieder leeren
    fileInput.value = '';
  }
});
*/ 
/*
// Drag n Drop funktion
// Funktion zum Umgehen der Standardverhalten von Drag-and-Drop
const dragDropArea = document.getElementById("drag-drop-area");
const fileInput = document.getElementById("file-input");

// Event Listener für das Dragging von Dateien
dragDropArea.addEventListener("dragover", (event) => {
  event.preventDefault(); // Verhindert das Standardverhalten, das die Datei nicht erlaubt
  dragDropArea.classList.add("drag-over"); // Zeigt an, dass die Datei im Drop-Bereich ist
});

dragDropArea.addEventListener("dragleave", () => {
  dragDropArea.classList.remove("drag-over"); // Entfernt die visuelle Drag-Over-Klasse
});

dragDropArea.addEventListener("drop", (event) => {
  event.preventDefault();
  dragDropArea.classList.remove("drag-over"); // Entfernt die visuelle Drag-Over-Klasse

  // Die Datei(s) aus dem Drop-Event extrahieren
  const file = event.dataTransfer.files[0]; // Nimmt die erste Datei im Drop
  if (file && file.type === "application/dicom" || file.name.endsWith(".dcm")) {
    // Setzt die Datei ins Input-Feld und löst den Upload aus
    fileInput.files = event.dataTransfer.files;
    handleFileUpload();
  } else {
    alert("Bitte eine gültige DICOM-Datei (.dicom, .dcm) hochladen.");
  }
});

// Funktion für den Datei-Upload (behandelt sowohl Drag-and-Drop als auch manuelles Hochladen)
fileInput.addEventListener("change", handleFileUpload);

// Funktion für die Handhabung des Datei-Uploads
function handleFileUpload() {
  if (fileInput.files && fileInput.files[0]) {
    const file = fileInput.files[0];
    
    // Hier kannst du eine Funktion aufrufen, um die DICOM-Datei zu verarbeiten
    console.log("Datei hochgeladen: ", file.name);

    // Du kannst hier die Logik zum Hinzufügen der KI-Namen oder zum Verarbeiten der DICOM-Datei einbauen
    document.getElementById("ki-list").style.display = "block"; // Zeigt das Drop-Down an
    const kiSelect = document.getElementById("ki-list");
    const optionDefault = document.createElement("option");
    optionDefault.value = "";
    optionDefault.disabled = true;
    optionDefault.selected = true;
    optionDefault.text = "Bitte KI auswählen";
    kiSelect.innerHTML = ""; // Entfernt alle aktuellen Optionen
    kiSelect.appendChild(optionDefault);

    // KIs zur Liste hinzufügen (hier statisch, kann dynamisch angepasst werden)
    const kiNames = ["KI 1", "KI 2", "KI 3"]; // Dies kannst du dynamisch nach Bedarf anpassen
    kiNames.forEach(function(ki) {
      const option = document.createElement("option");
      option.value = ki.toLowerCase();
      option.text = ki;
      kiSelect.appendChild(option);
    });
  }
}
*/

// Funktion zur Überprüfung der Dateiendung
function validateFileExtension(file) {
  // Erlaubte Dateiendungen (zum Beispiel: .jpg, .png, .pdf)
  const allowedExtensions = ['.dcm', '.dicom'];

  // Holen der Dateiendung
  const fileExtension = file.name.split('.').pop().toLowerCase();

  // Überprüfen, ob die Dateiendung erlaubt ist
  if (!allowedExtensions.includes('.' + fileExtension)) {
    alert('Ungültige Datei! Bitte laden Sie eine Datei mit den folgenden Endungen hoch: ' + allowedExtensions.join(', '));
    return false;
  }

  return true;
}

// Event-Listener für das manuelle Dateiupload-Feld
document.getElementById('file-input').addEventListener('change', function(event) {
  const file = event.target.files[0];

  // Wenn die Datei nicht den erlaubten Endungen entspricht, verhindere den Upload
  if (!validateFileExtension(file)) {
    // Setze das Datei-Feld zurück (optional)
    event.target.value = '';
  } else {
    // Datei ist validiert, hier kann der Upload-Prozess fortgesetzt werden
    console.log('Datei ist gültig:', file.name);
  }
});

// Event-Listener für das Drag-and-Drop (wenn es implementiert ist)
document.querySelector('.drag-drop-area').addEventListener('drop', function(event) {
  event.preventDefault();
  const file = event.dataTransfer.files[0];

  // Wenn die Datei nicht den erlaubten Endungen entspricht, verhindere den Upload
  if (!validateFileExtension(file)) {
    // Optional: Zeige eine Fehlermeldung oder setze das Drag-and-Drop zurück
    console.log('Ungültige Datei!');
  } else {
    // Datei ist validiert, hier kann der Upload-Prozess fortgesetzt werden
    console.log('Datei ist gültig:', file.name);
  }
});
