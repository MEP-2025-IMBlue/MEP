# export-realm.ps1

Write-Host "Exportiere Realm..."
docker exec mep-keycloak /opt/keycloak/bin/kc.sh export --dir=/opt/keycloak/data/import --realm imblue-realm --users realm_file

Write-Host "Zielordner prüfen..."
if (!(Test-Path -Path "./keycloak-export")) {
    New-Item -ItemType Directory -Path "./keycloak-export" | Out-Null
}

Write-Host "Kopiere nur die JSON-Datei direkt in keycloak-export/..."
docker cp mep-keycloak:/opt/keycloak/data/import/imblue-realm-realm.json ./keycloak-export/

Write-Host "Export abgeschlossen! Datei liegt unter ./keycloak-export/imblue-realm-realm.json"