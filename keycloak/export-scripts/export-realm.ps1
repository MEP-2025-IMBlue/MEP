Write-Host "== Realm wird exportiert =="
docker exec mep-keycloak /opt/keycloak/bin/kc.sh export --dir=/opt/keycloak/data/import --realm imblue-realm --users realm_file

# Ziel: keycloak/keycloak-export/, relativ zum Skriptverzeichnis
$exportDir = "../keycloak-export"
$importPath = "/opt/keycloak/data/import/imblue-realm-realm.json"

Write-Host "-- Zielordner pruefen..."
if (!(Test-Path -Path $exportDir)) {
    New-Item -ItemType Directory -Path $exportDir | Out-Null
}

Write-Host "-- JSON-Datei wird exportiert..."
docker cp mep-keycloak:$importPath "$exportDir/"

Write-Host "== Export abgeschlossen! Datei liegt unter: $exportDir\imblue-realm-realm.json"
