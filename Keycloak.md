# ❓ Docker & Keycloak – FAQ & Verhalten

## 1. ✨ Können andere über Git auf meine Volumes (z. B. Postgres) zugreifen?

**❌ Nein.**

* Docker-Volumes liegen **lokal** auf deinem Rechner.
* Sie werden **nicht mit Git geteilt**, außer du exportierst oder kopierst gezielt Daten.

✅ **Dein Team bekommt nur das Repository – keine deiner gespeicherten DICOM-Daten oder Benutzerdaten in der DB.**

---

## 2. ⚡ Wird der Keycloak-Stand automatisch gespeichert wie bei Postgres?

**✅ Ja – intern. Aber:**

* Keycloak speichert seine Daten **persistiert im Docker-Volume** (wie Postgres).
* Du musst `docker exec ... export` **nur dann machen**, wenn du den Stand z. B. über `keycloak-export/` im Git weitergeben willst.

### 📌 Fazit:

| Fall                                      | Export nötig? |
| ----------------------------------------- | ------------- |
| Du arbeitest lokal weiter                 | ❌ Nein        |
| Du willst den aktuellen Realm weitergeben | ✅ Ja          |

---

## 3. 🚀 Kann ich meine JSON-Datei einfach weitergeben (z. B. per Git oder USB)?

**✅ Ja, absolut.**

### Voraussetzungen:

* Der Mitstudent nutzt den **exakt gleichen Realm-Namen**, z. B. `imblue-realm`
* Und dieselbe Projektstruktur: `docker-compose.yml` + `--import-realm` + `volume`

Dann gilt:

🔁 **Deine `imblue-realm-realm.json` ist vollständig portierbar**

* Sie enthält: Benutzer, Rollen, Mappings, Clients usw.

> Es gibt **keine Kompatibilitätsprobleme**, solange das Setup gleich ist.

---

## 4. 🌐 Was passiert bei `docker compose down` vs `docker compose down -v`?

| Befehl                   | Keycloak-Daten (Realms, Benutzer)         | Wann sinnvoll?                      |
| ------------------------ | ----------------------------------------- | ----------------------------------- |
| `docker compose down`    | ✅ Daten bleiben erhalten (Volume bleibt)  | Normaler Shutdown                   |
| `docker compose down -v` | ❌ Daten werden gelöscht (Volume entfernt) | Wenn du komplett neu starten willst |

### 🟢 Nach `docker compose down -v`:

* Beim nächsten `docker compose up --build` erkennt Keycloak:
  → **"Kein Realm vorhanden"**
  → Importiert automatisch `keycloak-export/imblue-realm-realm.json`
  (solange `--import-realm` gesetzt ist)

---

## ✅ Zusammenfassung deiner 4 Fragen:

| Frage                               | Antwort               |
| ----------------------------------- | --------------------- |
| 1. Volumes im Git sichtbar?         | ❌ Nein, sind lokal    |
| 2. Keycloak speichert wie Postgres? | ✅ Ja, über Volume     |
| 3. JSON weitergeben möglich?        | ✅ Ja, problemlos      |
| 4. `down` vs `down -v`?             | Nur `-v` löscht Realm |
