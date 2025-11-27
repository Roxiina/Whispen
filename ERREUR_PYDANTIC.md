# ⚠️ ERREUR: Failed building wheel for pydantic-core

## 🔍 Diagnostic

Cette erreur apparaît quand **UV essaie de compiler pydantic-core** depuis les sources au lieu d'utiliser les wheels pré-compilés.

```
ERROR: Failed building wheel for pydantic-core
error: failed-wheel-build-for-install
```

---

## ✅ SOLUTION RAPIDE (2 minutes)

### N'UTILISEZ PAS `start-uv.ps1` !

Utilisez **`start.ps1`** qui utilise pip standard :

```powershell
# 1. Supprimez l'ancien environnement virtuel (si existant)
cd Whispen\backend
Remove-Item -Recurse -Force .venv, venv -ErrorAction SilentlyContinue

# 2. Retournez à la racine
cd ..

# 3. Lancez avec le script STANDARD
.\start.ps1
```

**✅ Le script `start.ps1` utilise pip qui télécharge automatiquement les wheels pré-compilés.**

---

## 🔧 Installation Manuelle (si start.ps1 ne fonctionne pas)

### Windows

```powershell
# 1. Supprimer ancien environnement
cd backend
Remove-Item -Recurse -Force venv -ErrorAction SilentlyContinue

# 2. Créer nouvel environnement avec Python standard
python -m venv venv

# 3. Activer
.\venv\Scripts\Activate.ps1

# 4. Mettre à jour pip (IMPORTANT)
python -m pip install --upgrade pip setuptools wheel

# 5. Installer les dépendances
pip install -r requirements.txt

# 6. Vérifier l'installation
python -c "from faster_whisper import WhisperModel; print('OK')"

# 7. Lancer le backend
python -m app.main
```

### Dans un NOUVEAU terminal (Frontend)

```powershell
cd frontend
npm install
npm run dev
```

---

## ❌ Pourquoi UV ne fonctionne pas ?

UV est **ultra-rapide** mais il a des limitations :

1. **Pas de wheels pré-compilés** - UV compile depuis les sources
2. **Nécessite Rust** - pydantic-core, cryptography, etc.
3. **Nécessite Visual C++ Build Tools** - Pour av, numpy, etc.

**Pour un projet Python avec beaucoup de dépendances compilées, pip standard est PLUS FIABLE.**

---

## 🎯 Vérification que ça fonctionne

Après installation, vous devriez voir :

### Backend (http://localhost:8000)
```
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
🔄 Loading Whisper model 'medium'...
✅ Local Whisper model loaded successfully
```

### Frontend (http://localhost:3000)
```
VITE v5.0.11  ready in 234 ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

---

## 📚 Documentation

- **README.md** - Guide utilisateur complet
- **INSTALLATION.md** - Guide d'installation détaillé
- **start.ps1** - Script de démarrage standard (RECOMMANDÉ)
- **start-uv.ps1** - Script UV (pour utilisateurs avancés avec Rust installé)

---

## 🆘 Toujours des problèmes ?

### Erreur : "Module 'faster_whisper' not found"
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install faster-whisper==1.1.0 requests==2.32.3
```

### Erreur : "Port 8000 already in use"
```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus (remplacer <PID>)
taskkill /PID <PID> /F
```

### Erreur : "Python not found"
Installez Python 3.11+ : https://www.python.org/downloads/

---

**Auteur** : Équipe Whispen  
**Version** : 1.1 (27 novembre 2024)
