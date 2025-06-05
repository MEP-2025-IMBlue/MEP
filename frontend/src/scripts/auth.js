// =========================
// frontend/src/scripts/auth.js
// =========================

const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

// Nicht auf index.html ausführen
if (!window.location.pathname.endsWith('/index.html')) {
  keycloak.init({
    onLoad: 'check-sso',
    pkceMethod: 'S256',
    redirectUri: window.location.origin + window.location.pathname
  }).then(authenticated => {
    if (!authenticated) {
      keycloak.login();
      return;
    }

    window.history.replaceState({}, document.title, window.location.pathname);

    const roles = keycloak.tokenParsed?.realm_access?.roles || [];

    setupNavbar(roles);
    enforceAccessControl(roles);
  }).catch(console.error);
}

// =========================
// Navbar je nach Rolle anzeigen
// =========================
function setupNavbar(roles) {
  const navbarContainer = document.getElementById("navbar");
  if (!navbarContainer) return;

  fetch("/layouts/navbar.html")
    .then(res => res.text())
    .then(html => {
      navbarContainer.innerHTML = html;

      // === Rollenbasierte Links ===
      const linksDiv = document.getElementById("nav-links");
      if (!linksDiv) return;

      let links = [];

      if (roles.includes("admin") || roles.includes("provider")) {
        links.push(`<a href="/pages/dashboard.html" data-i18n-key="dashboard">Dashboard</a>`);
        links.push(`<a href="/pages/container_upload.html" data-i18n-key="upload_container">Container hochladen</a>`);
      }

      if (roles.includes("admin") || roles.includes("user")) {
        links.push(`<a href="/pages/dicom_upload.html" data-i18n-key="upload_dicom">DICOM hochladen</a>`);
      }

      links.push(`<a href="http://localhost:8090/realms/imblue-realm/account" target="_blank" data-i18n-key="edit_profile">Profil bearbeiten</a>`);

      linksDiv.innerHTML = links.join(" ");

      // === Aktive Seite markieren ===
      const currentPage = window.location.pathname.split('/').pop();
      document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href').split('/').pop() === currentPage) {
          link.classList.add('active');
        }
      });

      // === Sprachumschalter aktivieren ===
      if (typeof i18n !== "undefined") {
        i18n.applyTranslations();

        const langBtn = document.getElementById("lang-toggle");
        if (langBtn) {
          langBtn.textContent = i18n.currentLang === "de" ? "EN" : "DE";
          langBtn.addEventListener("click", () => {
            i18n.toggleLang();
          });
        }
      }

      // === Logout-Button setzen ===
      const logoutLink = document.getElementById("logout-link");
      if (logoutLink) {
        logoutLink.addEventListener("click", () => {
          logout(); // führt den Logout korrekt aus
        });
      }
    })
    .catch(error => console.error("Navbar konnte nicht geladen werden:", error));
}

// =========================
// Zugriffskontrolle auf Seitenebene
// =========================
function enforceAccessControl(roles) {
  const path = window.location.pathname;

  const accessMatrix = {
    "/pages/dashboard.html": ["admin", "provider"],
    "/pages/container_upload.html": ["admin", "provider"],
    "/pages/dicom_upload.html": ["admin", "user"]
  };

  const allowed = accessMatrix[path];

  if (allowed && !roles.some(r => allowed.includes(r))) {
    alert("Zugriff verweigert. Sie werden ausgeloggt.");
    logout();
  }
}

// =========================
// Logout-Fallback (optional)
// =========================
function logout() {
  window.location.href = keycloak.createLogoutUrl({
    redirectUri: 'http://localhost:8080/index.html'
  });
}

// =========================
// Initiale Übersetzung laden
// =========================
document.addEventListener("DOMContentLoaded", () => {
  if (typeof i18n !== "undefined") {
    i18n.loadTranslations(i18n.currentLang);
  }
});
