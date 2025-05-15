document.getElementById("dicom-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const statusDiv = document.getElementById("dicom-status");
  const kiContainer = document.getElementById("ki-list");
  const aiBox = document.getElementById("ai-result");
  const kiTitle = document.getElementById("ki-title");

  statusDiv.innerText = "⏳ Upload gestartet...";
  statusDiv.style.color = "#ffd700";

  // Simulierter Upload
  setTimeout(async () => {
    statusDiv.innerText = "✅ Upload erfolgreich abgeschlossen.";
    statusDiv.style.color = "#00cc66";

    // KI-Liste aus echtem Backend holen
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      if (!res.ok) throw new Error(await res.text());
      const containers = await res.json();

      kiContainer.innerHTML = "";
      aiBox.classList.add("hidden");
      kiTitle.classList.remove("hidden");

      containers.forEach((container) => {
        const card = document.createElement("div");
        card.className = "ki-card";

        card.innerHTML = `
          <div class="ki-card-icon">🧠</div>
          <h3>${container.image_name}:${container.image_tag}</h3>
          <p>Container-ID: ${container.image_id}</p>
          <button class="select-btn" onclick='showResult("KI-Prozess wurde gestartet für Container ID ${container.image_id}")'>Auswählen</button>
        `;

        kiContainer.appendChild(card);
      });

      kiContainer.classList.remove("hidden");
    } catch (err) {
      kiContainer.innerHTML = `<p style="color:red;">❌ Fehler beim Laden der Container: ${err.message}</p>`;
    }
  }, 1500);
});

function showResult(diagnoseText) {
  const resultBox = document.getElementById("ai-result");
  const content = document.getElementById("result-content");
  content.textContent = JSON.stringify({ diagnose: diagnoseText }, null, 2);
  resultBox.classList.remove("hidden");
}
