# Script PowerShell - Demarrage Whispen (Standard)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WHISPEN - Demarrage Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK Python detecte : $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERREUR Python n'est pas installe ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Verifier Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "OK Node.js detecte : $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERREUR Node.js n'est pas installe ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Demarrer le backend
Write-Host "Demarrage Backend FastAPI..." -ForegroundColor Yellow
Set-Location backend

# Creer l'environnement virtuel si necessaire
if (-not (Test-Path "venv")) {
    Write-Host "Creation environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
}

# Activer l'environnement
Write-Host "Activation environnement virtuel..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Mettre a jour pip
Write-Host "Mise a jour pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Installer les dependances
Write-Host "Installation dependances backend..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "Lancement du serveur FastAPI sur http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m app.main"

Set-Location ..

# Attendre 3 secondes
Start-Sleep -Seconds 3

# Demarrer le frontend
Write-Host "Demarrage Frontend React..." -ForegroundColor Yellow
Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "Installation dependances frontend..." -ForegroundColor Yellow
    npm install
}

Write-Host "Lancement du serveur Vite sur http://localhost:3000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Application lancee avec succes !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API : http://localhost:8000" -ForegroundColor White
Write-Host "Frontend    : http://localhost:3000" -ForegroundColor White
Write-Host "API Docs    : http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur CTRL+C dans les fenetres de terminal pour arreter." -ForegroundColor Gray
Write-Host ""
