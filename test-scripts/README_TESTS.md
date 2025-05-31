# Test-Skripte für MEP-Projekt

Dieses Verzeichnis enthält zwei Skripte, um automatisierte Tests im Docker-Container `mep-backend` auszuführen.

## Dateien

- `run_tests.ps1`  
  PowerShell-Skript für Windows-Nutzer. Führt Unit-Tests im Docker-Container aus.

- `run_tests.sh`  
  Bash-Skript für Linux/macOS/WSL. Führt dieselben Tests im Container aus.

## Verwendung

### PowerShell (Windows)

```powershell
cd test-scripts
./run_tests.ps1
```

### Bash (Linux/macOS/WSL)

```bash
cd test-scripts
chmod +x run_tests.sh
./run_tests.sh
```

> **Hinweis:** Es wird direkt im Container getestet (Container muss existieren und laufen). Auf deinem Rechner muss kein `pytest` installiert sein.