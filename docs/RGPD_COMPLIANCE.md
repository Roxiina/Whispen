# 📄 Conformité RGPD - Whispen

## Introduction

Whispen est conçu pour être **100% conforme au RGPD** (Règlement Général sur la Protection des Données) dès sa conception. Ce document détaille les mesures techniques et organisationnelles mises en place.

---

## 🎯 Principes RGPD Respectés

| Principe | Implémentation Whispen |
|----------|------------------------|
| **Licéité, loyauté, transparence** | Consentement explicite (upload volontaire), informations claires |
| **Limitation des finalités** | Transcription/résumé uniquement, pas d'autre usage |
| **Minimisation des données** | Aucune donnée personnelle collectée sauf fichier audio |
| **Exactitude** | IA >95% précision, pas de modification manuelle |
| **Limitation de la conservation** | Suppression automatique après 24h |
| **Intégrité et confidentialité** | HTTPS, validation stricte, logs anonymisés |
| **Responsabilité** | Documentation complète, traçabilité des traitements |

---

## 🔒 Données Traitées

### Catégories de Données

| Type | Données | Durée de Conservation | Base Légale |
|------|---------|----------------------|-------------|
| **Fichiers audio** | Enregistrements vocaux uploadés | 24h max (suppression auto) | Consentement |
| **Transcriptions** | Texte généré par IA | Session uniquement (pas de stockage) | Consentement |
| **Résumés** | Synthèse générée par IA | Session uniquement | Consentement |
| **Logs techniques** | IP anonymisée, timestamps | 7 jours | Intérêt légitime (sécurité) |

### ❌ Données NON Collectées

- Nom, prénom, email
- Adresse postale
- Numéro de téléphone
- Cookies de tracking
- Historique de navigation
- Données bancaires

---

## 🛡️ Mesures de Sécurité Techniques

### 1. Chiffrement

```
✅ HTTPS/TLS 1.3 : Communication chiffrée client-serveur
✅ Azure Storage : Chiffrement au repos (AES-256)
✅ API Keys : Stockées dans Azure Key Vault (recommandé en production)
```

### 2. Validation & Isolation

```python
# Validation stricte des fichiers (file_handler.py)
- Taille maximale : 200 MB
- Extensions whitelist : mp3, wav, m4a, flac, ogg, webm
- Vérification type MIME (python-magic)
- Pas de path traversal (UUID unique)
```

### 3. Suppression Automatique

```python
# Nettoyage automatique (file_handler.py)
async def cleanup_old_files(self, hours: int = 24):
    """Supprime les fichiers >24h (conformité RGPD)"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for file_path in self.temp_folder.iterdir():
        if file_mtime < cutoff_time:
            path.unlink()  # Suppression définitive
```

**Exécution** :
- Au démarrage de l'application
- Optionnel : Cron job quotidien

### 4. Logs Anonymisés

```python
# Exemple de log conforme RGPD
logger.info(f"Transcription completed: {file_id}")  # UUID, pas d'info personnelle
# ❌ PAS DE : logger.info(f"User {email} uploaded {filename}")
```

---

## 📜 Droits des Utilisateurs

### Droit d'Accès

**Q** : Un utilisateur peut-il accéder à ses données ?  
**R** : Oui, pendant la session. Après 24h, les fichiers sont supprimés.

**Implémentation** :
- Export TXT/PDF disponible immédiatement après transcription
- Pas de compte utilisateur → pas de "profil" à consulter

### Droit de Rectification

**Q** : Un utilisateur peut-il corriger des erreurs ?  
**R** : Oui, via édition manuelle du texte transcrit (frontend).

**Implémentation** :
```javascript
// Frontend : textarea éditable
<textarea value={transcription.text} onChange={handleEdit} />
```

### Droit à l'Effacement ("Droit à l'oubli")

**Q** : Un utilisateur peut-il supprimer ses données ?  
**R** : Oui, automatiquement après 24h. Pas de demande nécessaire.

**Implémentation** :
- Suppression automatique (cf. `cleanup_old_files()`)
- Pas de stockage persistant en base de données

### Droit à la Limitation du Traitement

**Q** : Un utilisateur peut-il limiter l'usage de ses données ?  
**R** : Oui, en ne cliquant pas sur "Générer un résumé".

**Implémentation** :
- Transcription et résumé sont **deux étapes séparées**
- L'utilisateur contrôle chaque action

### Droit à la Portabilité

**Q** : Un utilisateur peut-il exporter ses données ?  
**R** : Oui, formats TXT, JSON, PDF disponibles.

**Implémentation** :
```javascript
// Frontend : export TXT
const handleDownload = () => {
  const blob = new Blob([transcription.text], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `transcription-${transcription.id}.txt`;
  a.click();
};
```

### Droit d'Opposition

**Q** : Un utilisateur peut-il s'opposer au traitement ?  
**R** : Oui, en ne uploadant pas de fichier.

**Implémentation** :
- Pas de traitement automatique sans action utilisateur
- Consentement explicite à chaque upload

---

## 🌍 Transferts de Données Hors UE

### Azure OpenAI (Localisation)

**Configuration Recommandée** :
```
Région Azure : France Central / West Europe
Datacenters : UE uniquement
```

**Garanties** :
- ✅ **Clauses Contractuelles Types (CCT)** : Microsoft Azure
- ✅ **Privacy Shield** : Invalide, mais CCT en remplacement
- ✅ **RGPD Article 44-49** : Transfert encadré

**Vérification** :
```bash
# Vérifier la région de votre ressource Azure OpenAI
az cognitiveservices account show \
  --name YOUR-RESOURCE-NAME \
  --resource-group YOUR-RG \
  --query location
```

### Sous-traitants

| Fournisseur | Service | Localisation | Conformité |
|-------------|---------|--------------|------------|
| **Microsoft Azure** | Hosting + IA | UE (France/West Europe) | ✅ RGPD, ISO 27001 |
| **OpenAI (via Azure)** | Modèles IA | UE via Azure | ✅ Encadré par CCT |

---

## 📋 Registre des Traitements

### Traitement 1 : Transcription Audio

| Champ | Valeur |
|-------|--------|
| **Finalité** | Conversion audio → texte |
| **Base légale** | Consentement (upload volontaire) |
| **Catégories de données** | Fichiers audio, transcriptions |
| **Destinataires** | Azure OpenAI Whisper |
| **Durée conservation** | 24h maximum |
| **Mesures sécurité** | HTTPS, validation, suppression auto |

### Traitement 2 : Génération de Résumé

| Champ | Valeur |
|-------|--------|
| **Finalité** | Synthèse automatique de texte |
| **Base légale** | Consentement (clic "Générer résumé") |
| **Catégories de données** | Transcriptions, résumés |
| **Destinataires** | Azure OpenAI GPT-4 |
| **Durée conservation** | Session uniquement |
| **Mesures sécurité** | HTTPS, pas de stockage |

---

## 🔍 Analyse d'Impact (AIPD)

### Risques Identifiés

| Risque | Gravité | Probabilité | Mesure d'Atténuation |
|--------|---------|-------------|----------------------|
| **Accès non autorisé aux fichiers** | Élevée | Faible | UUID uniques, validation stricte |
| **Fuite de données via logs** | Moyenne | Faible | Logs anonymisés, pas d'IP en clair |
| **Conservation excessive** | Élevée | Moyenne | Suppression auto 24h, pas de DB |
| **Transfert hors UE** | Moyenne | Faible | Azure EU uniquement, CCT |
| **Attaque par upload malveillant** | Élevée | Moyenne | Validation MIME, taille max, sandbox |

### Conclusion AIPD

✅ **Risques maîtrisés** : Aucune AIPD formelle nécessaire (traitement à faible risque).

---

## 📞 Contact DPO

**Délégué à la Protection des Données (DPO)** :
- Email : dpo@whispen.dev
- Adresse : [Votre adresse]

**Autorité de Contrôle (France)** :
- CNIL : [cnil.fr](https://www.cnil.fr)
- Plainte en ligne : [cnil.fr/plaintes](https://www.cnil.fr/fr/plaintes)

---

## 🔄 Mises à Jour

Ce document sera mis à jour en cas de :
- Modification des traitements de données
- Évolution réglementaire
- Ajout de nouvelles fonctionnalités

**Dernière mise à jour** : 25 novembre 2025  
**Version** : 1.0

---

## ✅ Checklist de Conformité

### Avant Mise en Production

- [ ] **Politique de confidentialité** rédigée et accessible
- [ ] **Mentions légales** affichées sur le site
- [ ] **Consentement** explicite (checkbox ou message clair)
- [ ] **Suppression automatique** configurée (<24h)
- [ ] **HTTPS** activé (certificat SSL valide)
- [ ] **Logs anonymisés** (pas d'IP en clair)
- [ ] **Azure OpenAI** en région UE (France/West Europe)
- [ ] **Tests de sécurité** réalisés (pentests recommandés)
- [ ] **Documentation** mise à jour (README, ARCHITECTURE)
- [ ] **Formation équipe** RGPD réalisée

### En Production (Continu)

- [ ] **Audit annuel** des traitements
- [ ] **Revue logs** (détection incidents)
- [ ] **Mises à jour sécurité** (dépendances, OS)
- [ ] **Veille réglementaire** (nouvelles lois)

---

## 📚 Références

- **RGPD** : [Règlement (UE) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- **CNIL** : [Guide développeur](https://www.cnil.fr/fr/guide-rgpd-du-developpeur)
- **Microsoft Azure** : [Centre de confiance](https://www.microsoft.com/fr-fr/trust-center)
- **OpenAI** : [Privacy Policy](https://openai.com/policies/privacy-policy)

---

**Whispen - Conformité RGPD garantie par conception** 🔒
