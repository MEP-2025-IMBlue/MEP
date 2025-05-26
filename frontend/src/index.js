// =========================
// frontend/index.js
// =========================

// Initialisiere Keycloak-Instanz
const keycloak = new Keycloak({
  url: 'http://localhost:8090/',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

// Startet Keycloak und erzwingt Login bei Seitenaufruf
keycloak.init({
  onLoad: 'login-required', // Bei nicht angemeldetem Benutzer → Login-Seite
  pkceMethod: 'S256',        // Sichere Tokenübertragung via PKCE
  redirectUri: window.location.origin + '/index.html' // Nach Login zurück zur Startseite
}).then(authenticated => {
  if (!authenticated) return;

  // Extrahiere Rollen aus Token
  const roles = keycloak.tokenParsed?.realm_access?.roles || [];

  // Weiterleitung je nach Rolle
  redirectToRolePage(roles);

  // Entferne Token-Parameter aus der URL
  window.history.replaceState({}, document.title, window.location.pathname);
}).catch(err => {
  console.error("Fehler bei Keycloak-Initialisierung:", err);
});

// Weiterleitung je nach Rolle auf die richtige HTML-Seite
function redirectToRolePage(roles) {
  if (roles.includes('admin') || roles.includes('provider')) {
    window.location.href = '/pages/dashboard.html';
  } else if (roles.includes('user')) {
    window.location.href = '/pages/dicom_upload.html';
  } else {
    alert("Keine gültige Rolle gefunden. Sie werden jetzt ausgeloggt.");
    keycloak.logout({ redirectUri: window.location.origin + '/index.html' });
  }
}
