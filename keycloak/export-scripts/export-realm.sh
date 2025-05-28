#!/bin/bash

echo "== Realm wird exportiert =="
docker exec mep-keycloak /opt/keycloak/bin/kc.sh export --dir=/opt/keycloak/data/import --realm imblue-realm --users realm_file

EXPORT_DIR="../keycloak-export"
IMPORT_PATH="/opt/keycloak/data/import/imblue-realm-realm.json"

echo "-- Zielordner pruefen..."
mkdir -p "$EXPORT_DIR"

echo "-- JSON-Datei wird exportiert..."
docker cp mep-keycloak:$IMPORT_PATH "$EXPORT_DIR/"

echo "== Export abgeschlossen! Datei liegt unter: $EXPORT_DIR/imblue-realm-realm.json"
