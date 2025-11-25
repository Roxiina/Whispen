# Script PowerShell avec UV - Demarrage Whispen

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WHISPEN - Demarrage avec UV" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier UV
try {
    $uvVersion = uv --version 2>&1
    Write-Host "UV detecte : $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "UV n'est pas installe" -ForegroundColor Red
    Write-Host "Installation de UV..." -ForegroundColor Yellow
    try {
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        Write-Host "UV installe avec succes" -ForegroundColor Green
    } catch {
        Write-Host "Echec installation UV" -ForegroundColor Red
        exit 1
    }
}

# Verifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python detecte : $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python n'est pas installe" -ForegroundColor Red
    exit 1
}

# Verifier Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js detecte : $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js n'est pas installe" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Demarrer le backend avec UV
Write-Host "Demarrage Backend FastAPI avec UV..." -ForegroundColor Yellow
Set-Location backend

# Creer l'environnement virtuel avec UV si necessaire
if (-not (Test-Path ".venv")) {
    Write-Host "Creation environnement virtuel avec UV..." -ForegroundColor Yellow
    uv venv
}

# Activer l'environnement
Write-Host "Activation environnement virtuel..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Synchroniser les dependances avec UV
Write-Host "Installation dependances avec UV..." -ForegroundColor Yellow
uv pip install -r requirements.txt

Write-Host "Lancement du serveur FastAPI sur http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; python -m app.main"

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
Write-Host "Backend cree avec UV (10-100x plus rapide que pip !)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Appuyez sur CTRL+C dans les fenetres de terminal pour arreter." -ForegroundColor Gray
Write-Host ""
