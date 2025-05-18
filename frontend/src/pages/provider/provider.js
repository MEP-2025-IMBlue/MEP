// =========================
// src/pages/provider/provider.js
// =========================

const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

keycloak.init({
  onLoad: 'check-sso',
  pkceMethod: 'S256',
  redirectUri: window.location.origin + '/src/pages/provider/provider.html'
}).then(authenticated => {
  if (!authenticated) {
    keycloak.login();
  } else {
    // Provider mit Name begrüßen
    const name = keycloak.tokenParsed?.name || "Provider";
    document.getElementById('greeting').textContent = `Hallo ${name}. Herzlich willkommen auf Ihrer Seite!`;
  }
  window.history.replaceState({}, document.title, window.location.pathname);
});

function logout() {
  window.location.href = keycloak.createLogoutUrl({
    redirectUri: 'http://localhost:8080/index.html'
  });
}

window.addEventListener('beforeunload', function () {
  navigator.sendBeacon(
    keycloak.createLogoutUrl({ redirectUri: 'http://localhost:8080/index.html' })
  );
});