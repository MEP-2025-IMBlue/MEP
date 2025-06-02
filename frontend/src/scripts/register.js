// Event-Listener auf das Registrierungsformular setzen
document.getElementById("register-form").addEventListener("submit", function (e) {
    e.preventDefault(); // Standardverhalten (Absenden des Formulars) verhindern

    // Werte der Passwortfelder auslesen
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm-password").value;
    const message = document.getElementById("register-message"); // Feedback-Element

    // Überprüfen, ob beide Passwörter übereinstimmen
    if (password !== confirm) {
      message.textContent = "\u274C Die Passwörter stimmen nicht überein.";
      message.style.color = "#ff4d4d"; // Fehlerfarbe (rot)
      return; // Beende Funktion bei Fehler
    }

    // Wenn Passwörter stimmen: Erfolgsmeldung anzeigen
    message.textContent = "\u2705 Registrierung erfolgreich! Weiterleitung...";
    message.style.color = "#00cc66"; // Erfolgsfarbe (grün)

    // Nach 2 Sekunden Weiterleitung zur DICOM-Upload-Seite
    setTimeout(() => {
      window.location.href = "dicom_upload.html";
    }, 2000);
});
