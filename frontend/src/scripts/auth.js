// =========================
// frontend/src/scripts/auth.js
// =========================

// Initialisiere Keycloak erneut – diesmal auf allen Seiten außer index.html.
// Ziel: Rollen auslesen, Navbar laden und Zugriffsschutz einrichten.
const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

// Verhindere doppelte Authentifizierung:
// auth.js wird nur auf Unterseiten ausgeführt – NICHT auf /index.html
if (!window.location.pathname.endsWith('/index.html')) {
  // Initialisiere nur Single-Sign-On Prüfung (kein Redirect bei fehlender Session!)
  keycloak.init({
    onLoad: 'check-sso',  // Prüft nur, ob Benutzer eingeloggt ist
    pkceMethod: 'S256',
    redirectUri: window.location.origin + window.location.pathname // Bleibt auf aktueller Seite
  }).then(authenticated => {
    // Wenn Benutzer nicht eingeloggt ist → Login erzwingen
    if (!authenticated) {
      keycloak.login();
      return;
    }

    // Bereinige URL von überflüssigen Keycloak-Parametern
    window.history.replaceState({}, document.title, window.location.pathname);

    // Extrahiere die Rollen aus dem Access Token
    const roles = keycloak.tokenParsed?.realm_access?.roles || [];

    // Lade Navbar dynamisch und schütze die aktuelle Seite
    setupNavbar(roles);
    enforceAccessControl(roles);
  }).catch(console.error); // Fehlerbehandlung bei Token-Validierung
}

// =========================
// Navbar je nach Rolle anzeigen
// =========================
function setupNavbar(roles) {
  const navbarContainer = document.getElementById("navbar");
  if (!navbarContainer) return;

  // Lade HTML-Template für die Navbar
  fetch("/layouts/navbar.html")
    .then(res => res.text())
    .then(html => {
      navbarContainer.innerHTML = html;

      // Finde das Element, in das die Link-Liste geschrieben wird
      const linksDiv = document.getElementById("nav-links");
      if (!linksDiv) return;

      let links = [];

      // Dashboard & Container-Upload: nur für admin + provider
      if (roles.includes("admin") || roles.includes("provider")) {
        links.push(`<a href="/pages/dashboard.html">Dashboard</a>`);
        links.push(`<a href="/pages/container_upload.html">Container hochladen</a>`);
      }

      // DICOM-Upload: nur für admin + user
      if (roles.includes("admin") || roles.includes("user")) {
        links.push(`<a href="/pages/dicom_upload.html">DICOM hochladen</a>`);
      }

      // Profil-Link ist für alle Rollen sichtbar
      links.push(`<a href="http://localhost:8090/realms/imblue-realm/account" target="_blank">Profil bearbeiten</a>`);

      // Schreibe alle Links final in die Navbar
      linksDiv.innerHTML = links.join(" ");
    });
}

// =========================
// Zugriffskontrolle auf Seitenebene
// =========================
function enforceAccessControl(roles) {
  const path = window.location.pathname;

  // Zugriffsmatrix: definiert, welche Rollen welche Seiten sehen dürfen
  const accessMatrix = {
    "/pages/dashboard.html": ["admin", "provider"],
    "/pages/container_upload.html": ["admin", "provider"],
    "/pages/dicom_upload.html": ["admin", "user"]
  };

  // Liste der erlaubten Rollen für die aktuelle Seite
  const allowed = accessMatrix[path];

  // Falls Rolle nicht erlaubt → Logout und zurück zur Startseite
  if (allowed && !roles.some(r => allowed.includes(r))) {
    alert("Zugriff verweigert. Sie werden ausgeloggt.");
    logout();
  }
}

// =========================
// Logout-Logik (Keycloak + Weiterleitung)
// =========================
function logout() {
  // Erzeugt die vollständige Logout-URL mit Rückleitung zu index.html
  window.location.href = keycloak.createLogoutUrl({
    redirectUri: 'http://localhost:8080/index.html'
  });
}
