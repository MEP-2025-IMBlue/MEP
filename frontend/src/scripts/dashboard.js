document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("ki-image-list");
  const searchInput = document.getElementById("searchInput");
  const filterSelect = document.getElementById("filterSelect");

  let allData = []; // wird global gespeichert

  async function fetchKIImages() {
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      if (!res.ok) throw new Error(await res.text());
      allData = await res.json();
      console.log("DEBUG: ki-images Daten:", allData);
      renderTable(allData);
    } catch (err) {
      container.innerHTML = `<p style="color: #ff4d4d; padding: 1rem;">❌ Fehler beim Laden: ${err.message}</p>`;
    }
  }

  function renderTable(data) {
    const table = document.createElement("table");
    table.className = "ki-image-table";

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Tag</th>
        <th>Hochgeladen am</th>
        <th>Beschreibung</th>
        <th>Aktionen</th>
        <th>Teststatus</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.forEach((img) => {
      const formattedDate = img.image_created_at
        ? formatDateTime(img.image_created_at)
        : "-";
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${img.image_id}</td>
        <td>${img.image_name}</td>
        <td>${img.image_tag}</td>
        <td>${formattedDate}</td>
        <td>${img.repository || "-"}</td>
        <td>
          <button class="btn-edit" onclick="alert('Bearbeiten: ${img.image_id}')">✏ bearbeiten</button> |
          <button class="btn-delete" onclick="deleteImage(${img.image_id})">🗑 löschen</button> |
          <button class="btn-test" onclick="testContainer(${img.image_id}, '${img.image_name}')">🧪 testen</button>
        </td>
        <td>
          <span id="test-status-${img.image_id}" class="test-status"></span>
        </td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.innerHTML = "";
    container.appendChild(table);
  }

  // Zeitstempel formatieren
  function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return "-";

    const utcDate = new Date(dateTimeStr);
    if (isNaN(utcDate)) return "-";

    const now = new Date();
    const nowBerlin = new Date(now.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));
    const berlinDate = new Date(utcDate.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));

    const timeStr = berlinDate.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });

    const isSameDay = (date1, date2) =>
      date1.getFullYear() === date2.getFullYear() &&
      date1.getMonth() === date2.getMonth() &&
      date1.getDate() === date2.getDate();

    if (isSameDay(berlinDate, nowBerlin)) return `heute, ${timeStr} Uhr`;
    const yesterdayBerlin = new Date(nowBerlin);
    yesterdayBerlin.setDate(nowBerlin.getDate() - 1);
    if (isSameDay(berlinDate, yesterdayBerlin)) return `gestern, ${timeStr} Uhr`;
    return `${berlinDate.toLocaleDateString("de-DE")}, ${timeStr} Uhr`;
  }

  // Funktion zum Testen eines Containers
  async function testContainer(imageId, imageName) {
    const statusElement = document.getElementById(`test-status-${imageId}`);

    const updateStatus = (message, status = "info", tooltip = "") => {
      console.log(`DEBUG: Status für Image ${imageName} (ID: ${imageId}): ${message}`);
      if (!statusElement) return;

      statusElement.innerHTML = "";
      const badge = document.createElement("span");
      badge.className = `status-badge status-${status}`;
      badge.textContent = status === "running" ? `⏳ ${message}` : status === "success" ? `✅ ${message}` : `❌ ${message}`;

      if (status === "running") {
        const progress = document.createElement("div");
        progress.className = "progress-bar";
        badge.appendChild(progress);
      }

      if (tooltip) {
        const tooltipDiv = document.createElement("div");
        tooltipDiv.className = "tooltip";
        tooltipDiv.textContent = tooltip;
        badge.appendChild(tooltipDiv);
      }

      statusElement.appendChild(badge);
    };

    try {
      if (!imageId || isNaN(imageId)) {
        console.log("DEBUG: Ungültige imageId:", imageId);
        throw new Error("Ungültige Image-ID.");
      }

      console.log("DEBUG: allData Inhalt:", allData);
      if (!allData || allData.length === 0) {
        console.log("DEBUG: allData ist leer oder nicht geladen");
        throw new Error("Keine Images geladen. Bitte Seite neu laden.");
      }

      const img = allData.find((i) => i.image_id === parseInt(imageId));
      if (!img) {
        console.log("DEBUG: Image nicht gefunden für imageId:", imageId);
        throw new Error(`Image mit ID ${imageId} nicht gefunden.`);
      }

      const userId = img.image_provider_id;
      if (!userId || isNaN(userId)) {
        console.log("DEBUG: Ungültige userId/image_provider_id:", userId);
        throw new Error("Ungültige Benutzer-ID (image_provider_id).");
      }

      updateStatus("Container wird gestartet...", "running");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const formData = new FormData();
      formData.append("user_id", parseInt(userId));
      formData.append("image_id", parseInt(imageId));
      console.log("DEBUG: FormData POST /containers/start mit: user_id=", userId, "image_id=", imageId);
      const formDataRes = await fetch("http://localhost:8000/containers/start", {
        method: "POST",
        body: formData,
      });
      if (!formDataRes.ok) {
        const formDataErrorText = await formDataRes.text();
        console.log("DEBUG: FormData Fehlerantwort:", formDataErrorText);
        throw new Error(`Start fehlgeschlagen: ${formDataErrorText}`);
      }

      const formDataResult = await formDataRes.json();
      console.log("DEBUG: FormData Start-Antwort:", formDataResult);
      const containerId = formDataResult.container_id;
      if (!containerId) {
        console.log("DEBUG: Keine container_id in FormData-Antwort:", formDataResult);
        throw new Error("Keine Container-ID in der Antwort erhalten.");
      }

      updateStatus("Container läuft...", "running");
      await new Promise((resolve) => setTimeout(resolve, 5000));

      updateStatus("Container wird gestoppt...", "running");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const stopRes = await fetch(`http://localhost:8000/containers/${containerId}/stop`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!stopRes.ok) {
        const errorText = await stopRes.text();
        console.log("DEBUG: Fehlerantwort von POST /containers/.../stop:", errorText);
        throw new Error(`Stoppen fehlgeschlagen: ${errorText}`);
      }

      updateStatus("Container wird gelöscht...", "running");
      const deleteRes = await fetch(`http://localhost:8000/containers/${containerId}`, {
        method: "DELETE",
      });
      if (!deleteRes.ok) {
        const errorText = await deleteRes.text();
        console.log("DEBUG: Fehlerantwort von DELETE /containers/...:", errorText);
        throw new Error(`Löschen fehlgeschlagen: ${errorText}`);
      }
      updateStatus("Test erfolgreich", "success", `Container-ID: ${containerId}`);
    } catch (err) {
      updateStatus("Test fehlgeschlagen", "error", err.message);
      console.log("DEBUG: Fehler in testContainer:", err);
    }
  }

  // Filter-Funktion
  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    const field = filterSelect.value;

    const filtered = allData.filter((img) => {
      if (!field) {
        const uploadTime = localStorage.getItem(`uploadTime_${img.image_id}`)?.toLowerCase() || "";
        return (
          img.image_name?.toLowerCase().includes(query) ||
          img.image_tag?.toLowerCase().includes(query) ||
          uploadTime.includes(query)
        );
      }

      if (field === "created_at") {
        const uploadTime = localStorage.getItem(`uploadTime_${img.image_id}`);
        return uploadTime?.toLowerCase().includes(query);
      }

      return img[field]?.toLowerCase().includes(query);
    });

    renderTable(filtered);
  });

  async function deleteImage(id) {
    if (!confirm(`Soll das KI-Image mit ID ${id} wirklich gelöscht werden?`)) return;
    try {
      const res = await fetch(`http://localhost:8000/ki-images/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(await res.text());
      alert("✅ Erfolgreich gelöscht!");
      fetchKIImages();
    } catch (err) {
      alert("❌ Fehler beim Löschen: " + err.message);
    }
  }

  window.deleteImage = deleteImage;
  window.testContainer = testContainer;

  fetchKIImages();
});