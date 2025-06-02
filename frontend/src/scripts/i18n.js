const i18n = {
  translations: {},
  currentLang: localStorage.getItem("lang") || "de",

  async loadTranslations(lang) {
    try {
      console.log(`Lade Übersetzungen für: ${lang}`);
      const res = await fetch(`../scripts/${lang}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      this.translations = await res.json();
      this.currentLang = lang;
      localStorage.setItem("lang", lang);
      // Übersetzungen nur anwenden, wenn Navbar schon im DOM ist
      if (document.getElementById('navbar')) {
        this.applyTranslations();
      }
    } catch (e) {
      console.error("Fehler beim Laden der Übersetzungen:", e);
    }
  },

  applyTranslations() {
    console.log("Übersetzungen anwenden");
    document.querySelectorAll("[data-i18n-key]").forEach(el => {
      const key = el.getAttribute("data-i18n-key");
      if (this.translations[key]) {
        el.textContent = this.translations[key];
        console.log(`Übersetzt ${key} → ${this.translations[key]}`);
      }
    });
  },

  toggleLang() {
    const newLang = this.currentLang === "de" ? "en" : "de";
    this.loadTranslations(newLang);
  }
};