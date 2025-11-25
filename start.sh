#!/bin/bash
# Script de démarrage Whispen (Linux/Mac)

echo "========================================"
echo "  🎙️  WHISPEN - Démarrage Application"
echo "========================================"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé"
    exit 1
fi

echo "✅ Python et Node.js détectés"
echo ""

# Démarrer le backend
echo "📦 Démarrage Backend FastAPI..."
cd backend

if [ ! -d "venv" ]; then
    echo "🔧 Création environnement virtuel..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -d "venv/lib/python*/site-packages/fastapi" ]; then
    echo "📥 Installation dépendances backend..."
    pip install -r requirements.txt
fi

echo "🚀 Lancement du serveur FastAPI sur http://localhost:8000"
python -m app.main &
BACKEND_PID=$!

cd ..

# Attendre 3 secondes
sleep 3

# Démarrer le frontend
echo "📦 Démarrage Frontend React..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📥 Installation dépendances frontend..."
    npm install
fi

echo "🚀 Lancement du serveur Vite sur http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "========================================"
echo "  ✅ Application lancée avec succès !"
echo "========================================"
echo ""
echo "🌐 Backend API : http://localhost:8000"
echo "🌐 Frontend    : http://localhost:3000"
echo "📖 API Docs    : http://localhost:8000/docs"
echo ""
echo "Appuyez sur CTRL+C pour arrêter."
echo ""

# Attendre l'arrêt
wait $BACKEND_PID $FRONTEND_PID
