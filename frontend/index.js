// =========================
// frontend/index.js
// =========================

// Initialisiert Keycloak-Instanz mit Realm und Client-ID
const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

keycloak.init({
  onLoad: 'login-required', // Benutzer muss eingeloggt sein, sonst wird weitergeleitet
  pkceMethod: 'S256',
  redirectUri: window.location.origin + '/index.html'
}).then(authenticated => {
  if (!authenticated) {
    console.warn("Benutzer ist nicht authentifiziert.");
    return;
  }

  // Debug: Gibt das ganze Token aus
  //console.log("Token:", keycloak.tokenParsed);
  //const realmAccess = keycloak.tokenParsed?.realm_access;
  //const roles = Array.isArray(realmAccess?.roles) ? realmAccess.roles : [];
  //console.log("🧾 Zugewiesene Rollen:", roles);

  // Weiterleitung basierend auf Rolle
  if (roles.includes('admin')) {
    window.location.href = '/src/pages/admin/admin.html';
  } else if (roles.includes('provider')) {
    window.location.href = '/src/pages/provider/provider.html';
  } else if (roles.includes('user')) {
    window.location.href = '/src/pages/user/user.html';
  } else {
    alert("Keine gültige Rolle gefunden. Sie werden jetzt ausgeloggt.");
    keycloak.logout({ redirectUri: window.location.origin + '/index.html' });
  }

  // Entfernt Token-Infos aus der URL
  window.history.replaceState({}, document.title, window.location.pathname);
}).catch(err => {
  console.error("Fehler bei Keycloak-Initialisierung:", err);
});