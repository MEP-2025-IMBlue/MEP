document.getElementById("dicom-form").addEventListener("submit", function(e) {
    e.preventDefault();
  
    const statusDiv = document.getElementById("dicom-status");
    const kiContainer = document.getElementById("ki-list");
    const aiBox = document.getElementById("ai-result");
  
    statusDiv.innerText = "⏳ Upload gestartet...";
    statusDiv.style.color = "#ffd700";
  
    // Simulierter Uploadprozess
    setTimeout(() => {
      statusDiv.innerText = "✅ Upload erfolgreich abgeschlossen.";
      statusDiv.style.color = "#00cc66";
  
      // Beispiel-Provider-KI-Systeme laden
      const providerKIs = [
        {
          name: "BrainScan AI",
          diagnose: "Keine Auffälligkeiten im Gehirn."
        },
        {
          name: "LungMatcher",
          diagnose: "Lungeninfiltrate erkannt."
        },
        {
          name: "CT Analyzer",
          diagnose: "CT unauffällig."
        }
      ];
  
      // Bestehende leeren
      kiContainer.innerHTML = "";
      aiBox.classList.add("hidden");
  
      // Anzeigen & dynamisch aufbauen
      providerKIs.forEach((ki) => {
        const card = document.createElement("div");
        card.className = "ki-card";
  
        card.innerHTML = `
          <img src="${ki.image}" alt="${ki.name}" />
          <h3>${ki.name}</h3>
          <button class="select-btn" onclick='showResult(${JSON.stringify(ki.diagnose)})'>Auswählen</button>
        `;
  
        kiContainer.appendChild(card);
      });
  
      kiContainer.classList.remove("hidden");
    }, 2000);
  });
  
  function showResult(diagnoseText) {
    const resultBox = document.getElementById("ai-result");
    const content = document.getElementById("result-content");
    content.textContent = JSON.stringify({ diagnose: diagnoseText }, null, 2);
    resultBox.classList.remove("hidden");
  }
  