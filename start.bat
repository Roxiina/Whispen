@echo off
REM Script de démarrage Whispen (Windows)

echo ========================================
echo   🎙️ WHISPEN - Demarrage Application
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

echo ✅ Python et Node.js detectes
echo.

REM Démarrer le backend
echo 📦 Demarrage Backend FastAPI...
cd backend
if not exist venv (
    echo 🔧 Creation environnement virtuel...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Installer les dépendances si nécessaire
if not exist venv\Lib\site-packages\fastapi (
    echo 📥 Installation dependances backend...
    pip install -r requirements.txt
)

echo 🚀 Lancement du serveur FastAPI sur http://localhost:8000
start cmd /k "venv\Scripts\activate.bat && python -m app.main"

cd ..

REM Attendre 3 secondes
timeout /t 3 /nobreak >nul

REM Démarrer le frontend
echo 📦 Demarrage Frontend React...
cd frontend

if not exist node_modules (
    echo 📥 Installation dependances frontend...
    npm install
)

echo 🚀 Lancement du serveur Vite sur http://localhost:3000
start cmd /k "npm run dev"

cd ..

echo.
echo ========================================
echo   ✅ Application lancee avec succes !
echo ========================================
echo.
echo 🌐 Backend API : http://localhost:8000
echo 🌐 Frontend    : http://localhost:3000
echo 📖 API Docs    : http://localhost:8000/docs
echo.
echo Appuyez sur CTRL+C dans les fenetres de terminal pour arreter.
echo.

pause
