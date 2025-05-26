// ========================= 
// frontend/src/scripts/auth.js
// =========================

// Initialisiere Keycloak mit Realm-Infos
const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

// Starte Authentifizierung bei Seitenaufruf
keycloak.init({
  onLoad: 'login-required',
  pkceMethod: 'S256',
  redirectUri: window.location.href
}).then(authenticated => {
  if (!authenticated) return;

  const roles = keycloak.tokenParsed?.realm_access?.roles || [];

  // Navbar und Zugriffsprüfung aktivieren
  setupNavbar(roles);
  enforceAccessControl(roles);

}).catch(console.error);

// Lade Navbar und baue sie rollenspezifisch auf
function setupNavbar(roles) {
  const navbarContainer = document.getElementById("navbar");
  if (!navbarContainer) return;

  // Lade HTML von navbar.html
  fetch("/layouts/navbar.html")
    .then(response => response.text())
    .then(html => {
      navbarContainer.innerHTML = html;

      const linksDiv = document.getElementById("nav-links");
      if (!linksDiv) return;

      let links = [];

      if (roles.includes("admin") || roles.includes("provider")) {
        links.push(`<a href="/pages/dashboard.html">Dashboard</a>`);
        links.push(`<a href="/pages/container_upload.html">Container hochladen</a>`);
      }

      if (roles.includes("admin") || roles.includes("user")) {
        links.push(`<a href="/pages/dicom_upload.html">DICOM hochladen</a>`);
      }

      // Profil-Link immer sichtbar
      links.push(`<a href="http://localhost:8090/realms/imblue-realm/account" target="_blank">Profil bearbeiten</a>`);

      linksDiv.innerHTML = links.join(" ");
    });
}

// Schutz-Logik: Seite nur mit erlaubten Rollen betreten
function enforceAccessControl(roles) {
  const path = window.location.pathname;

  const accessMatrix = {
    "/pages/dashboard.html": ["admin", "provider"],
    "/pages/container_upload.html": ["admin", "provider"],
    "/pages/dicom_upload.html": ["admin", "user"]
  };

  const allowedRoles = accessMatrix[path];

  if (allowedRoles && !roles.some(r => allowedRoles.includes(r))) {
    alert("Zugriff verweigert. Sie werden jetzt ausgeloggt.");
    logout();
  }
}

// Logout mit Rückleitung zu Login
function logout() {
  window.location.href = keycloak.createLogoutUrl({
    redirectUri: 'http://localhost:8080/index.html'
  });
}
