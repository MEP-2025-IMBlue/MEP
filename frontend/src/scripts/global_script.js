fetch('/layouts/navbar.html')
  .then(response => response.text())
  .then(data => {
    document.getElementById('navbar').innerHTML = data;

    // Active-Klasse setzen
    const currentPage = window.location.pathname.split('/').pop();
    document.querySelectorAll('.nav-links a').forEach(link => {
      if (link.getAttribute('href').split('/').pop() === currentPage) {
        link.classList.add('active');
      }
    });

    // Übersetzungen anwenden (falls bereits geladen)
    if (typeof i18n !== "undefined") {
      i18n.applyTranslations();
    }

    // Sprach-Button initialisieren und Klick-Handler setzen
    const langBtn = document.getElementById("lang-toggle");
    if (langBtn) {
      langBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";

      // Eventlistener sauber neu setzen (kein doppeltes Registrieren)
      langBtn.replaceWith(langBtn.cloneNode(true));
      const newLangBtn = document.getElementById("lang-toggle");

      newLangBtn.addEventListener("click", () => {
        i18n.toggleLang();
        // Nach Umschalten Übersetzungen erneut anwenden
        i18n.applyTranslations();
        newLangBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";
      });
    }
  })
  .catch(error => console.error('Fehler beim Laden der Navbar:', error));

// Nach DOM fertig laden, lade initial die Übersetzungen (ohne zu applizieren, da Navbar noch nicht da)
document.addEventListener("DOMContentLoaded", () => {
  i18n.loadTranslations(i18n.currentLang);
});