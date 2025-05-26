# 🔐 Keycloak Realm Export – Windows & Linux/macOS

Dieses Verzeichnis enthält zwei Skripte zum Exportieren des Keycloak-Realm `imblue-realm`:

- `export-realm.sh` → für **Linux/macOS**
- `export-realm.ps1` → für **Windows (PowerShell)**

## 📦 Was machen die Skripte?

1. Exportieren den Realm `imblue-realm` aus dem laufenden Container `mep-keycloak`.
2. Speichern ihn im Container unter `/opt/keycloak/data/import/`.
3. Kopieren die JSON-Datei `imblue-realm-realm.json` aus dem Container auf den Host in:  
   **`./keycloak/keycloak-export/`**

Diese Datei kann beim nächsten Start von Keycloak (docker_compose.yml) importiert werden (wenn der Realm dort noch nicht existiert).

## ⚙️ Nutzung

### 🐧 Linux/macOS 

# Wechsle in das Skriptverzeichnis
cd keycloak/export-scripts
# Mache das Shell-Skript ausführbar (nur beim ersten Mal notwendig)
chmod +x export-realm.sh
# Führe das Skript aus
./export-realm.sh

### Windows

# Wechsle in das Skriptverzeichnis
cd keycloak\export-scripts
# Führe das PowerShell-Skript aus
.\export-realm.ps1