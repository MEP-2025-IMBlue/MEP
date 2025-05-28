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

    if (typeof i18n !== "undefined") {
      i18n.applyTranslations();
    }

    const langBtn = document.getElementById("lang-toggle");
    if (langBtn) {
      langBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";

      langBtn.replaceWith(langBtn.cloneNode(true));
      const newLangBtn = document.getElementById("lang-toggle");

      newLangBtn.addEventListener("click", () => {
        i18n.toggleLang();
        i18n.applyTranslations();
        newLangBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";
      });
    }
  })
  .catch(error => console.error('Fehler beim Laden der Navbar:', error));

document.addEventListener("DOMContentLoaded", () => {
  i18n.loadTranslations(i18n.currentLang);
});
