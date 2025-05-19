// =========================
// src/pages/user/user.js
// =========================

// Keycloak initialisieren für die User-Seite
const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

keycloak.init({
  onLoad: 'check-sso', // Nur prüfen, ob bereits eingeloggt (keine automatische Weiterleitung)
  pkceMethod: 'S256', // Sicherheit bei der Tokenübertragung (Proof Key for Code Exchange)
  redirectUri: window.location.origin + '/src/pages/user/user.html' // Nach Login -> Userseite
}).then(authenticated => {
  if (!authenticated) {
    keycloak.login(); // Wenn nicht eingeloggt → zur Loginseite umleiten
  } else {
    // Begrüßung anzeigen mit vollständigem Namen oder Fallback
    const name = keycloak.tokenParsed?.name || "Benutzer";
    document.getElementById('greeting').textContent = `Herzlich Willkommen ${name}!`;
  }

  // Entfernt URL-Token nach erfolgreicher Anmeldung
  window.history.replaceState({}, document.title, window.location.pathname);
});

// Logout-Funktion: Weiterleitung zur Keycloak-Logout-Seite mit Rückleitung zur Startseite
function logout() {
  window.location.href = keycloak.createLogoutUrl({
    redirectUri: 'http://localhost:8080/index.html'
  });
}

// Automatisches Logout bei Schließen der Seite (optional, kann Login blockieren!)
// Hinweis: Diese Funktion sendet beim Schließen der Seite ein Logout-Signal an Keycloak
// Das kann zu Problemen führen, wenn der Benutzer z. B. beim Login ist → daher lieber deaktivieren
// window.addEventListener('beforeunload', function () {
//   navigator.sendBeacon(
//     keycloak.createLogoutUrl({ redirectUri: 'http://localhost:8080/index.html' })
//   );
// });