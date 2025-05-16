// frontend/index.js
  const keycloak = new Keycloak({
  url: 'http://localhost:8090',
  realm: 'imblue-realm',
  clientId: 'mep-frontend'
});

keycloak.init({
  onLoad: 'login-required',
  pkceMethod: 'S256',
  redirectUri: window.location.origin + '/index.html'
}).then(authenticated => {
  if (authenticated) {
    const roles = keycloak.tokenParsed.realm_access.roles;
    if (roles.includes('admin')) {
      window.location.href = '/src/pages/admin/admin.html';
    } else if (roles.includes('provider')) {
      window.location.href = '/src/pages/provider/provider.html';
    } else if (roles.includes('user')) {
      window.location.href = '/src/pages/user/user.html';
    } else {
      keycloak.logout({ redirectUri: 'http://localhost:8080' });
    }

    window.history.replaceState({}, document.title, window.location.pathname);
  }
});