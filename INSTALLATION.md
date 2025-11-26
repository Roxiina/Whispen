# 🚀 Guide d'Installation Whispen

## ⚠️ Problème avec UV ?

Si vous avez l'erreur `Failed building wheel for pydantic-core`, utilisez le script standard **start.ps1** au lieu de **start-uv.ps1**.

---

## 📋 Prérequis

1. **Python 3.11+** : https://www.python.org/downloads/
2. **Node.js 18+** : https://nodejs.org/
3. **Git** : https://git-scm.com/

---

## 🎯 Installation Simple (RECOMMANDÉ)

### Windows

```powershell
# 1. Cloner le projet
git clone https://github.com/Roxiina/Whispen.git
cd Whispen

# 2. Configurer Azure OpenAI
cd backend
copy .env.example .env
# Éditer .env avec vos clés Azure

# 3. Lancer l'application
cd ..
.\start.ps1
```

### Linux/Mac

```bash
# 1. Cloner le projet
git clone https://github.com/Roxiina/Whispen.git
cd Whispen

# 2. Configurer Azure OpenAI
cd backend
cp .env.example .env
# Éditer .env avec vos clés Azure

# 3. Rendre le script exécutable
chmod +x start.sh

# 4. Lancer l'application
./start.sh
```

---

## ⚡ Installation Ultra-Rapide avec UV (Optionnel)

**⚠️ UV nécessite que les packages aient des wheels pré-compilés.**

Si vous voulez utiliser UV (10-100x plus rapide que pip) :

```powershell
# Windows
.\start-uv.ps1

# Linux/Mac
./start-uv.sh
```

Si vous avez des erreurs de compilation (pydantic-core, faster-whisper, etc.), utilisez le script standard.

---

## 🐛 Résolution Problèmes Courants

### Erreur : `Failed building wheel for pydantic-core`

**Cause** : UV essaie de compiler depuis les sources au lieu d'utiliser des wheels pré-compilés.

**Solution** : Utilisez `start.ps1` au lieu de `start-uv.ps1`

```powershell
.\start.ps1
```

### Erreur : `Rust compiler not found`

**Cause** : Certains packages nécessitent Rust pour compiler.

**Solutions** :
1. Utilisez `start.ps1` (recommandé)
2. OU installez Rust : https://rustup.rs/

### Erreur : `Module 'faster_whisper' not found`

**Cause** : faster-whisper nécessite Visual C++ Build Tools sur Windows.

**Solutions** :
1. Installez Visual Studio Build Tools : https://visualstudio.microsoft.com/downloads/
2. OU utilisez Python 3.11 avec wheels pré-compilés

### Erreur : `Port 8000 already in use`

**Solution** :
```powershell
# Trouver le processus utilisant le port 8000
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID par le numéro trouvé)
taskkill /PID <PID> /F
```

---

## 📖 Documentation Complète

- **README.md** - Guide utilisateur complet
- **docs/ARCHITECTURE.md** - Architecture technique
- **docs/COMPARATIF_LOCAL_VS_CLOUD.md** - Analyse comparative
- **docs/PRESENTATION_GUIDE.md** - Guide de présentation orale
- **docs/RGPD_COMPLIANCE.md** - Conformité RGPD

---

## 🆘 Support

Si vous rencontrez toujours des problèmes :

1. Vérifiez que Python 3.11+ est installé : `python --version`
2. Vérifiez que pip est à jour : `python -m pip install --upgrade pip`
3. Essayez d'installer manuellement les dépendances :
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---
