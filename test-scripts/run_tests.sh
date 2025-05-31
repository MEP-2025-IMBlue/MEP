#!/bin/bash

# ===========================================
# run_tests.sh
# ===========================================
# Führt Tests im Docker-Container aus.
# Container: mep-backend
# Kein pytest auf dem Host nötig.
# ===========================================

container="mep-backend"
base_cmd="export PYTHONPATH=/app && cd /app/src"

run_kiimage_tests() {
  echo -e "\n-- KIImage-Tests laufen..."
  docker exec -it $container bash -c "$base_cmd && pytest -v --color=yes tests/crud_tests/test_kiImage_crud.py"
}

run_dicom_tests() {
  echo -e "\n-- DICOM-Tests laufen..."
  docker exec -it $container bash -c "$base_cmd && pytest -v --color=yes tests/crud_tests/test_dicom_crud.py"
}

run_crud_tests() {
  echo -e "\n-- Alle CRUD-Tests laufen..."
  docker exec -it $container bash -c "$base_cmd && pytest -v --color=yes tests/crud_tests/"
}

run_all_tests() {
  echo -e "\n-- Alle Tests (CRUD + API) laufen..."
  docker exec -it $container bash -c "$base_cmd && pytest -v --color=yes tests/"
}

echo -e "\n== Testskript (Docker-basiert) =="
echo "1 = Nur KIImage-Tests"
echo "2 = Nur DICOM-Tests"
echo "3 = Alle CRUD-Tests"
echo "4 = Alle Tests"
echo "Q = Beenden"
read -p $'\nAuswahl: ' option

case "$option" in
  1) run_kiimage_tests ;;
  2) run_dicom_tests ;;
  3) run_crud_tests ;;
  4) run_all_tests ;;
  Q|q) echo "== Abbruch durch Benutzer ==" ;;
  *) echo "!! Ungültige Eingabe" ;;
esac
