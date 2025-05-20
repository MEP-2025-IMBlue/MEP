✅ Keycloak Realm exportieren – Schritt für Schritt

-----------------1.Export im Container starten:--------------------------------------------

Kopiere das: docker exec mep-keycloak /opt/keycloak/bin/kc.sh export --dir=/opt/keycloak/data/import --realm imblue-realm --users realm_file

🔄 Dadurch wird dein aktueller imblue-realm als JSON-Datei im Container abgelegt.

-----------------2.Datei aus dem Container kopieren:----------------------------------------

Kopiere das: docker cp mep-keycloak:/opt/keycloak/data/import/imblue-realm-realm.json ./keycloak-export/


📁 Jetzt hast du im Projektverzeichnis den Ordner ./keycloak-export/ mit der Datei
imblue-realm-realm.json.

--------------------------------------------------------------------------------------------
💡 Hinweis:
Du musst diese Schritte nur ausführen, wenn du Änderungen am Realm sichern oder teilen willst.

Beim nächsten Start wird diese Datei nur dann genutzt, wenn der Realm nicht existiert (z. B. nach docker compose down -v).
