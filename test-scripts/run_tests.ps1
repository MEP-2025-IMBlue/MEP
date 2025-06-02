# ===========================================
# run_tests.ps1
# ===========================================
# Führt Tests in einem Docker-Container aus.
# Container: mep-backend
# Kein pytest auf dem Host nötig.
# ===========================================

$containerName = "mep-backend"
$baseCommand = "export PYTHONPATH=/app && cd /app/src"

function Run-CRUDKIImageTests {
    Write-Host "`n-- CRUD KIImage-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/crud_tests/test_kiImage_crud.py"
    docker exec -it $containerName bash -c $cmd
}

function Run-CRUDDICOMTests {
    Write-Host "`n-- CRUD DICOM-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/crud_tests/test_dicom_crud.py"
    docker exec -it $containerName bash -c $cmd
}

function Run-CRUDTests {
    Write-Host "`n-- Alle CRUD-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/crud_tests/"
    docker exec -it $containerName bash -c $cmd
}

function Run-APIKIImageTests {
    Write-Host "`n-- API KIIMage-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/api_tests/test_KIImage_routes.py"
    docker exec -it $containerName bash -c $cmd
}

function Run-APITests {
    Write-Host "`n-- Alle API-Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/api_tests/"
    docker exec -it $containerName bash -c $cmd
}
function Run-AllTests {
    Write-Host "`n-- Alle Tests laufen..."
    $cmd = "$baseCommand && pytest -v --color=yes tests/"
    docker exec -it $containerName bash -c $cmd
}

Write-Host "`n== Testskript (Docker-basiert) =="
Write-Host "1 = Nur CRUD KIImage-Tests"
Write-Host "2 = Nur CRUD DICOM-Tests"
Write-Host "3 = Alle CRUD-Tests"
Write-Host "4 = Nur API KIImage-Tests"
Write-Host "5 = Alle API-Tests"
Write-Host "6 = Alle Tests"
Write-Host "Q = Beenden"

$choice = Read-Host "`nAuswahl"

switch ($choice) {
    "1" { Run-CRUDKIImageTests }
    "2" { Run-CRUDDICOMTests }
    "3" { Run-CRUDTests }
    "4" { Run-APIKIImageTests }
    "5" { Run-APITests }
    "6" { Run-AllTests }
    "Q" { Write-Host "`n== Abbruch durch Benutzer =="; exit }
    default { Write-Host "`n!! Ungueltige Eingabe"; exit 1 }
}
