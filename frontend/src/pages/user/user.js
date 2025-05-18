// =========================
// src/pages/user/user.js
// =========================

const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

keycloak.init({
  onLoad: 'check-sso', // nur überprüfen, ob eingeloggt
  pkceMethod: 'S256',
  redirectUri: window.location.origin + '/src/pages/user/user.html'
}).then(authenticated => {
  if (!authenticated) {
    keycloak.login();
  } else {
    // Benutzer mit Name begrüßen
    const name = keycloak.tokenParsed?.name || "Benutzer";
    document.getElementById('greeting').textContent = `Hallo ${name}. Herzlich willkommen auf Ihrer Seite!`;
  }

  window.history.replaceState({}, document.title, window.location.pathname);
});

function logout() {
  window.location.href = keycloak.createLogoutUrl({
    redirectUri: 'http://localhost:8080/index.html'
  });
}

// Entfernt Session beim Fensterwechsel (optional, kann Login-Seite beeinflussen!)
window.addEventListener('beforeunload', function () {
  navigator.sendBeacon(
    keycloak.createLogoutUrl({ redirectUri: 'http://localhost:8080/index.html' })
  );
});