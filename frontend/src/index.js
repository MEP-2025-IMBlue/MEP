// =========================
// frontend/index.js
// =========================

// Initialisiert Keycloak-Instanz mit Realm und Client-ID
const keycloak = new Keycloak({
  url: 'http://localhost:8090/',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

// Starte Keycloak-Session mit Loginpflicht
keycloak.init({
  onLoad: 'login-required', // Benutzer muss eingeloggt sein, sonst Weiterleitung zur Loginseite
  pkceMethod: 'S256', // Sicherheit bei der Tokenübertragung (Proof Key for Code Exchange)
  redirectUri: window.location.origin + '/index.html' // Nach Login zurück zur Startseite
}).then(authenticated => {
  if (!authenticated) {
    console.warn("Benutzer ist nicht authentifiziert.");
    return;
  }

  // Extrahiere Rollen aus dem Token
  const roles = keycloak.tokenParsed?.realm_access?.roles || [];

  // Weiterleitung je nach Benutzerrolle
  redirectToRolePage(roles);

  // Entfernt Token-Parameter aus der URL (Aufräumen)
  window.history.replaceState({}, document.title, window.location.pathname);

}).catch(err => {
  console.error("Fehler bei Keycloak-Initialisierung:", err);
});

// Weiterleitungslogik basierend auf spezifischer Rollenprüfung
function redirectToRolePage(roles) {
  if (roles.includes('admin')) {
    window.location.href = '/src/pages/dashboard.html';
  } else if (roles.includes('provider')) {
    window.location.href = '/src/pages/dashboard.html';
  } else if (roles.includes('user')) {
    window.location.href = '/src/pages/dicom_upload.html';
  } else {
    alert("Keine gültige Rolle gefunden. Sie werden jetzt ausgeloggt.");
    keycloak.logout({ redirectUri: window.location.origin + '/index.html' });
  }
}