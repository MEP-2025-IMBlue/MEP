# ===========================================
# run_tests.ps1
# ===========================================
# Führt Tests in einem Docker-Container aus.
# Container: mep-backend
# Kein pytest auf dem Host nötig.
# ===========================================

$containerName = "mep-backend"
$baseCommand = "export PYTHONPATH=/app && cd /app/src"

function Run-KIImageTests {
    Write-Host "`n-- KIImage-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/crud_tests/test_kiImage_crud.py"
    docker exec -it $containerName bash -c $cmd
}

function Run-DICOMTests {
    Write-Host "`n-- DICOM-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/crud_tests/test_dicom_crud.py"
    docker exec -it $containerName bash -c $cmd
}

function Run-CRUDTests {
    Write-Host "`n-- Alle CRUD-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/crud_tests/"
    docker exec -it $containerName bash -c $cmd
}

function Run-AllTests {
    Write-Host "`n-- Alle Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/"
    docker exec -it $containerName bash -c $cmd
}

Write-Host "`n== Testskript (Docker-basiert) =="
Write-Host "1 = Nur KIImage-Tests"
Write-Host "2 = Nur DICOM-Tests"
Write-Host "3 = Alle CRUD-Tests"
Write-Host "4 = Alle Tests"
Write-Host "Q = Beenden"

$choice = Read-Host "`nAuswahl"

switch ($choice) {
    "1" { Run-KIImageTests }
    "2" { Run-DICOMTests }
    "3" { Run-CRUDTests }
    "4" { Run-AllTests }
    "Q" { Write-Host "`n== Abbruch durch Benutzer =="; exit }
    default { Write-Host "`n!! Ungültige Eingabe"; exit 1 }
}
