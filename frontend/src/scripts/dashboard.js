document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("ki-image-list");
  const searchInput = document.getElementById("searchInput");
  const filterSelect = document.getElementById("filterSelect");
  const infoBox = document.getElementById("dashboard-info");
  const langBtn = document.getElementById("lang-toggle-btn");
  let allData = [];

  await i18n.loadTranslations(i18n.currentLang);
  i18n.applyTranslations();

  if (langBtn) {
    langBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";
    langBtn.addEventListener("click", () => {
      i18n.toggleLang();
    });
  }

  window.addEventListener("languageChanged", () => {
    i18n.applyTranslations();
    fetchKIImages();
    if (filterSelect) {
      filterSelect.innerHTML = `
        <option value="">${i18n.translations.dashboard_filter_option}</option>
        <option value="image_name">${i18n.translations.name}</option>
        <option value="image_tag">${i18n.translations.tag}</option>
        <option value="created_at">${i18n.translations.uploaded_at}</option>
      `;
    }
    if (searchInput) {
      searchInput.placeholder = i18n.translations.dashboard_filter_placeholder;
    }
    if (langBtn) {
      langBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";
    }
  });

  function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return "-";
    const utcDate = new Date(dateTimeStr.endsWith("Z") ? dateTimeStr : `${dateTimeStr}Z`);
    if (isNaN(utcDate)) return "-";
    const berlinDate = new Date(utcDate.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));
    const timeStr = berlinDate.toLocaleTimeString(i18n.currentLang === "de" ? "de-DE" : "en-GB", { hour: "2-digit", minute: "2-digit" });
    const now = new Date();
    const nowBerlin = new Date(now.toLocaleString("en-US", { timeZone: "Europe/Berlin" }));

    const isSameDay = (d1, d2) => d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth() === d2.getMonth() &&
      d1.getDate() === d2.getDate();

    const yesterdayBerlin = new Date(nowBerlin);
    yesterdayBerlin.setDate(nowBerlin.getDate() - 1);

    if (isSameDay(berlinDate, nowBerlin)) return `${i18n.translations.today}, ${timeStr} ${i18n.translations.clock}`;
    if (isSameDay(berlinDate, yesterdayBerlin)) return `${i18n.translations.yesterday}, ${timeStr} ${i18n.translations.clock}`;
    return `${berlinDate.toLocaleDateString(i18n.currentLang === "de" ? "de-DE" : "en-GB")}, ${timeStr} ${i18n.translations.clock}`;
  }

  function renderTable(data) {
    const table = document.createElement("table");
    table.className = "ki-image-table";

    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>${i18n.translations.id}</th>
        <th>${i18n.translations.name}</th>
        <th>${i18n.translations.tag}</th>
        <th>${i18n.translations.uploaded_at}</th>
        <th>${i18n.translations.description}</th>
        <th>${i18n.translations.actions}</th>
        <th>${i18n.translations.test_status}</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.forEach((img) => {
      const formattedDate = formatDateTime(img.image_created_at);
      const containerId = img.running_container_id || null;
      const isRunning = !!containerId;
      const toggleText = isRunning ? i18n.translations.stop : i18n.translations.start;
      const toggleStatus = isRunning ? "running" : "stopped";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${img.image_id}</td>
        <td>${img.image_name}</td>
        <td>${img.image_tag}</td>
        <td>${formattedDate}</td>
        <td>${img.repository || "-"}</td>
        <td>
          <button class="btn-edit" onclick="alert('Edit: ${img.image_id}')">&#9998; ${i18n.translations.edit}</button> |
          <button class="btn-delete" onclick="deleteImage(${img.image_id})">&#128465; ${i18n.translations.delete}</button> |
          <button class="btn-test" onclick="testContainer(${img.image_id}, '${img.image_name}')">&#129514; ${i18n.translations.test}</button> |
          <button class="btn-toggle"
                  data-id="${img.image_id}"
                  data-name="${img.image_name}"
                  data-status="${toggleStatus}"
                  ${containerId ? `data-container-id="${containerId}"` : ""}>
              ${toggleText}
          </button>
        </td>
        <td><span id="test-status-${img.image_id}" class="test-status"></span></td>
      `;
      tbody.appendChild(tr);
    });

    table.appendChild(tbody);
    container.innerHTML = "";
    container.appendChild(table);
    renderInfoBox(data);
  }

  // START/STOP CLICK LOGIK 
  container.addEventListener("click", async (event) => {
    if (event.target.classList.contains("btn-toggle")) {
      const btn = event.target;
      const imageId = btn.dataset.id;
      const imageName = btn.dataset.name;
      const currentStatus = btn.dataset.status;
      let containerId = btn.dataset.containerId;

      try {
        const img = allData.find((i) => i.image_id === parseInt(imageId));
        const userId = img.image_provider_id;
        if (!userId) throw new Error("Benutzer-ID nicht verfügbar");

        const statusElement = document.getElementById("test-status-" + imageId);

        if (currentStatus === "stopped") {
          const formData = new FormData();
          formData.append("user_id", userId);
          formData.append("image_id", imageId);

          const res = await fetch("http://localhost:8000/containers/start", {
            method: "POST",
            body: formData,
          });
          if (!res.ok) throw new Error(await res.text());

          const result = await res.json();
          containerId = result.container_id;

          btn.textContent = i18n.translations.stop;
          btn.dataset.status = "running";
          btn.dataset.containerId = containerId;

          img.running_container_id = containerId;
          alert("\u2705 " + i18n.translations.container_started + " (ID: " + containerId + ")");
          renderInfoBox(allData);

        } else {
          if (!containerId) throw new Error("Container-ID fehlt");

          if (statusElement) {
            statusElement.innerHTML = `
              <span class="status-badge status-running">
                &#9203; ${i18n.translations.container_stopping}...
              </span>
            `;
          }

          await fetch(`http://localhost:8000/containers/${containerId}/stop`, { method: "POST" });
          btn.textContent = i18n.translations.start;
          btn.dataset.status = "stopped";
          delete btn.dataset.containerId;
          img.running_container_id = null;

          alert("\u26D4 " + i18n.translations.container_stopped);
          renderInfoBox(allData);

          if (statusElement) statusElement.innerHTML = "";
        }

      } catch (err) {
        alert("\u26A0\uFE0F Fehler: " + err.message);
      }
    }
  });

  function renderInfoBox(data) {
    if (!infoBox) return;
    const active = data.filter((img) => !!img.running_container_id).length;
    const total = data.length;
    const inactive = total - active;

    infoBox.innerHTML = `
      <div class="dashboard-info">
        <strong>&#128197; ${i18n.translations.dashboard_total}:</strong> ${total} |
        <span style="color:#28a745"><strong>&#11044; ${i18n.translations.dashboard_active}:</strong> ${active}</span> |
        <span style="color:#ff4d4d"><strong>&#11044; ${i18n.translations.dashboard_inactive}:</strong> ${inactive}</span>
      </div>
    `;
  }

  async function fetchKIImages() {
    container.innerHTML = `<p style="color: #fff; padding: 1rem;">${i18n.translations.loading_ki_images}</p>`;
    try {
      const res = await fetch("http://localhost:8000/ki-images");
      if (!res.ok) throw new Error(await res.text());
      allData = await res.json();
      container.innerHTML = allData.length === 0
        ? `<p>&#8505;&#xFE0F; ${i18n.translations.no_ki_images}</p>`
        : "";
      if (allData.length > 0) renderTable(allData);
    } catch (err) {
      container.innerHTML = `<p>&#10060; ${i18n.translations.load_images_error}</p>`;
    }
  }

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim().toLowerCase();
    const field = filterSelect.value;
    const filtered = allData.filter((img) => {
      const uploadTime = localStorage.getItem("uploadTime_" + img.image_id)?.toLowerCase() || "";
      if (!field) {
        return (
          img.image_name?.toLowerCase().includes(query) ||
          img.image_tag?.toLowerCase().includes(query) ||
          uploadTime.includes(query)
        );
      }
      if (field === "created_at") return uploadTime.includes(query);
      return img[field]?.toLowerCase().includes(query);
    });
    renderTable(filtered);
  });

  window.deleteImage = async function (id) {
    if (!confirm(`${i18n.translations.confirm_delete} ${id}${i18n.translations.confirm_delete_continue}`)) return;
    try {
      const res = await fetch(`http://localhost:8000/ki-images/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(await res.text());
      alert(i18n.translations.delete_success);
      await fetchKIImages();
    } catch (err) {
      alert(`${i18n.translations.delete_error_prefix} ${err.message}`);
    }
  };

  window.testContainer = async function (imageId, imageName) {
    const statusElement = document.getElementById("test-status-" + imageId);
    const updateStatus = (message, status = "info") => {
      if (!statusElement) return;
      statusElement.innerHTML = "";
      const badge = document.createElement("span");
      badge.className = "status-badge status-" + status;
      const icon = status === "running" ? "\u23F3" : status === "success" ? "\u2705" : "\u274C";
      badge.textContent = `${icon} ${message}`;
      statusElement.appendChild(badge);
    };

    try {
      const img = allData.find((i) => i.image_id === parseInt(imageId));
      const userId = img.image_provider_id;

      updateStatus(i18n.translations.container_starting, "running");
      await new Promise((r) => setTimeout(r, 1000));

      const formData = new FormData();
      formData.append("user_id", userId);
      formData.append("image_id", imageId);

      const startRes = await fetch("http://localhost:8000/containers/start", {
        method: "POST",
        body: formData,
      });
      if (!startRes.ok) throw new Error(await startRes.text());

      const { container_id } = await startRes.json();

      updateStatus(i18n.translations.container_running, "running");
      await new Promise((r) => setTimeout(r, 5000));

      await fetch(`http://localhost:8000/containers/${container_id}/stop`, { method: "POST" });
      await fetch(`http://localhost:8000/containers/${container_id}`, { method: "DELETE" });

      updateStatus(i18n.translations.test_success, "success");
    } catch (err) {
      updateStatus(i18n.translations.test_failed, "error");
    }
  };

  await fetchKIImages();
});
