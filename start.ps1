# Script PowerShell - Démarrage Whispen (Standard)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🎙️  WHISPEN - Démarrage Application" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python détecté : $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Vérifier Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js détecté : $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Démarrer le backend
Write-Host "📦 Démarrage Backend FastAPI..." -ForegroundColor Yellow
Set-Location backend

# Créer l'environnement virtuel si nécessaire
if (-not (Test-Path "venv")) {
    Write-Host "🔧 Création environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
}

# Activer l'environnement
Write-Host "⚡ Activation environnement virtuel..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Mettre à jour pip
Write-Host "📥 Mise à jour pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Installer les dépendances
Write-Host "📥 Installation dépendances backend..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "🚀 Lancement du serveur FastAPI sur http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\venv\Scripts\Activate.ps1; python -m app.main"

Set-Location ..

# Attendre 3 secondes
Start-Sleep -Seconds 3

# Démarrer le frontend
Write-Host "📦 Démarrage Frontend React..." -ForegroundColor Yellow
Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "📥 Installation dépendances frontend..." -ForegroundColor Yellow
    npm install
}

Write-Host "🚀 Lancement du serveur Vite sur http://localhost:3000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev"

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ Application lancée avec succès !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Backend API : http://localhost:8000" -ForegroundColor White
Write-Host "🌐 Frontend    : http://localhost:3000" -ForegroundColor White
Write-Host "📖 API Docs    : http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Appuyez sur CTRL+C dans les fenêtres de terminal pour arrêter." -ForegroundColor Gray
Write-Host ""
