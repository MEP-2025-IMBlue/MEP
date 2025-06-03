const i18n = {
  translations: {},
  currentLang: localStorage.getItem("lang") || "de",

  async loadTranslations(lang) {
    try {
      const res = await fetch(`../scripts/${lang}.json`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      this.translations = await res.json();
      this.currentLang = lang;
      localStorage.setItem("lang", lang);
      this.applyTranslations();

      // Update Toggle-Button-Text immer korrekt
      const btn = document.getElementById("lang-toggle");
      if (btn) btn.textContent = lang === "de" ? "EN" : "DE";
    } catch (e) {
      console.error("Fehler beim Laden der Übersetzungen:", e);
    }
  },

  applyTranslations() {
    document.querySelectorAll("[data-i18n-key]").forEach(el => {
      const key = el.getAttribute("data-i18n-key");
      const value = this.translations[key];
      if (!value) return;

      if (el.tagName === "INPUT" || el.hasAttribute("data-i18n-key-placeholder")) {
        el.placeholder = value;
      } else {
        el.textContent = value;
      }
    });
  },


  toggleLang() {
    const newLang = this.currentLang === "de" ? "en" : "de";
    this.loadTranslations(newLang).then(() => {
      document.dispatchEvent(new Event("languageChanged"));
    });
  }
};
