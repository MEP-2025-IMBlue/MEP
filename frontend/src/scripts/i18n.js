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

      const btn = document.getElementById("lang-toggle");
      if (btn) btn.textContent = lang === "de" ? "EN" : "DE";

      // Sprache geändert → Event auslösen
      document.dispatchEvent(new Event("languageChanged"));
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
        // Emoji (z. B. 📄) am Anfang beibehalten
        const emojiMatch = el.textContent.trim().match(/^\p{Emoji_Presentation}+/u);
        const emoji = emojiMatch ? emojiMatch[0] + " " : "";
        el.textContent = emoji + value;
      }
    });
  },

  toggleLang() {
    const newLang = this.currentLang === "de" ? "en" : "de";
    this.loadTranslations(newLang);
  }
};
