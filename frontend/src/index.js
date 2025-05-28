// =========================
// frontend/src/index.js
// =========================

// Initialisiere Keycloak-Instanz mit den Basisinformationen:
// - URL des Keycloak-Servers
// - Name des Realms
// - ID des Clients, wie in Keycloak definiert (Typ: Public Client)
const keycloak = new Keycloak({
  url: 'http://localhost:8090',           // Keycloak-Serveradresse
  realm: 'imblue-realm',                  // Dein Realm-Name (z. B. mRay)
  clientId: 'mep-frontend'                // Dein Frontend-Client (in Keycloak konfiguriert)
});

// Initialisiere die Authentifizierung über Keycloak:
// - 'login-required': Weiterleitung zur Loginseite, wenn nicht eingeloggt
// - PKCE = Sicherheitsmechanismus für Public Clients (Code Flow)
// - redirectUri = nach Login zurück auf index.html
keycloak.init({
  onLoad: 'login-required',
  pkceMethod: 'S256',
  redirectUri: window.location.origin + '/index.html'
}).then(authenticated => {
  // Falls Benutzer sich nicht eingeloggt hat, breche hier ab
  if (!authenticated) return;

  // Entferne alle Keycloak-URL-Parameter nach erfolgreichem Login (code, state, session_state)
  window.history.replaceState({}, document.title, window.location.pathname);

  // Extrahiere die Rollen des Benutzers aus dem JWT-Token
  const roles = keycloak.tokenParsed?.realm_access?.roles || [];

  // Leite Benutzer je nach Rolle auf die passende Seite weiter:
  // - admin oder provider → Dashboard
  // - user → DICOM Upload
  // - keine gültige Rolle → Logout + zurück zur Loginseite
  if (roles.includes('admin') || roles.includes('provider')) {
    window.location.href = '/pages/dashboard.html';
  } else if (roles.includes('user')) {
    window.location.href = '/pages/dicom_upload.html';
  } else {
    alert("Keine gültige Rolle gefunden. Sie werden ausgeloggt.");
    window.location.href = keycloak.createLogoutUrl({
      redirectUri: 'http://localhost:8080/index.html'
    });
  }
}).catch(console.error); // Bei Authentifizierungsfehlern Konsolenmeldung
