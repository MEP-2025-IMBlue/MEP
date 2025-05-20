document.getElementById("register-form").addEventListener("submit", function (e) {
    e.preventDefault();
  
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm-password").value;
    const message = document.getElementById("register-message");
  
    if (password !== confirm) {
      message.textContent = "\u274C Die Passwörter stimmen nicht überein.";
      message.style.color = "#ff4d4d";
      return;
    }
  
    message.textContent = "\u2705 Registrierung erfolgreich! Weiterleitung...";
    message.style.color = "#00cc66";
  
    setTimeout(() => {
      window.location.href = "dicom_upload.html";
    }, 2000);
  });
  