fetch('/layouts/navbar.html')
  .then(response => response.text())
  .then(data => {
    document.getElementById('navbar').innerHTML = data;

    const currentPage = window.location.pathname.split('/').pop();
    document.querySelectorAll('.nav-links a').forEach(link => {
      if (link.getAttribute('href').split('/').pop() === currentPage) {
        link.classList.add('active');
      }
    });

    // ✅ Hier: langBtn definieren
    const langBtn = document.getElementById("lang-toggle");
    if (langBtn) {
      const currentLang = localStorage.getItem("lang") || "de";
      langBtn.textContent = currentLang === "de" ? "EN" : "DE";

      langBtn.addEventListener("click", () => {
        const newLang = localStorage.getItem("lang") === "de" ? "en" : "de";
        localStorage.setItem("lang", newLang);
        langBtn.textContent = newLang === "de" ? "EN" : "DE";

        if (typeof applyTranslations === "function") {
          applyTranslations(newLang); // sofort übersetzen ✅
        }
      });
    }

    //  Direkt nach dem Einfügen übersetzen
    const initialLang = localStorage.getItem("lang") || "de";
    if (typeof applyTranslations === "function") {
      applyTranslations(initialLang);
    }
  });
