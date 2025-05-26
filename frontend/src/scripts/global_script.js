// frontend/src/scripts/navbar.js
fetch('/layouts/navbar.html')
  .then(response => response.text())
  .then(data => {
    document.getElementById('navbar').innerHTML = data;
    // Optional: Active-Klasse setzen
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
      if (link.getAttribute('href').split('/').pop() === currentPage) {
        link.classList.add('active');
      }
    });
  })
  .catch(error => console.error('Fehler:', error));