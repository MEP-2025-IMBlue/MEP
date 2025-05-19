# 📦 MEP-Frontend mit Keycloak

Dies ist das **Frontend-Modul** des MEP-Projekts zur Verwaltung von Benutzern (Admin, Provider, User) mit **Keycloak**. Die Anwendung ist statisch aufgebaut (HTML, JS) und nutzt ein CDN für `keycloak-js`, ohne Build-System oder Node.js-Abhängigkeiten.

---

## 🚀 Features

* 🔐 Login und Logout über Keycloak
* 🔁 Rollenbasierte Weiterleitung (`admin`, `provider`, `user`)
* 🙋 Benutzerbegrüßung auf Basis des Tokens
* 📁 Strukturierte Trennung der Seiten und JavaScript-Logik

---

## 🗂️ Projektstruktur

```
frontend/
├── index.html            # Einstiegspunkt → prüft Rolle und leitet weiter
├── index.js              # Rolle auslesen + Weiterleitung
└── src/
    └── pages/
        ├── admin/
        │   ├── admin.html
        │   └── admin.js
        ├── provider/
        │   ├── provider.html
        │   └── provider.js
        └── user/
            ├── user.html
            └── user.js
```

---

## ⚙️ Voraussetzungen

* Läuft als statische Seite z. B. mit `http-server`, NGINX oder im Docker-Container
* Benötigt funktionierenden **Keycloak-Server** unter `http://localhost:8090`
* Ein Realm namens `imblue-realm` mit dem Client `mep-frontend`
* Rollen: `admin`, `provider`, `user` müssen definiert und Benutzern zugewiesen sein

---

## 📌 Hinweise

* Das Projekt verwendet bewusst ein CDN (`https://cdn.jsdelivr.net/...`) – keine lokale NPM-Installation notwendig
* Die JS-Dateien sind modular und klar kommentiert
* Die automatische Logout-Funktion über `beforeunload` ist **auskommentiert**, um Login-Störungen zu vermeiden

---

## 🧪 Testzugänge (Beispiel)

| Benutzername | Rolle    | Passwort    |
| ------------ | -------- | ----------- |
| admin1       | admin    | admin123    |
| provider1    | provider | provider123 |
| user1        | user     | user123     |
| test1        | -        | test123     |

---

## 🧼 Deployment-Tipp

Da es sich um eine statische App handelt, kannst du sie einfach z. B. so hosten:

```bash
npx http-server ./frontend -p 8080
```

Oder per Docker:

```Dockerfile
FROM node:20-slim
WORKDIR /app
RUN npm install -g http-server
COPY ./frontend /app
CMD ["http-server", ".", "-p", "8080"]
```

---

## 🧠 Autor / Wartung

Dieses Frontend wurde im Rahmen des IMBlue-Projekts entwickelt. Bitte beachte die Kommentare in den JavaScript-Dateien für Anpassungen oder Erweiterungen.
