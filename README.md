# QCM Bio

Une application Flask pour créer et gérer des QCM (Questionnaires à Choix Multiples) avec scoring, timer et suivi des résultats.

## Fonctionnalités

- 🔐 **Authentification** : Connexion utilisateur sécurisée avec hachage de mot de passe
- 📝 **Création de QCM** : Les administrateurs peuvent créer des QCM avec explications
- ⏱️ **Timer** : Chronomètre intégré pour mesurer le temps passé par quiz
- 📊 **Scoring** : Calcul automatique du score et du pourcentage de réussite
- 🏆 **Classement** : Leaderboard global avec scores totaux et moyennes
- 📋 **Historique** : Détail complet de tous les résultats avec timestamps
- 📖 **Correction détaillée** : Affichage des questions, réponses données, bonnes réponses et explications

## Installation

### Prérequis
- Python 3.8+
- pip

### Étapes d'installation

1. Clonez le repo :
```bash
git clone https://github.com/TobiasGeoffray/qcm_bio.git
cd qcm_bio
```

2. Créez un environnement virtuel :
```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialiser la base de données :
```bash
python3 init_db.py
```

5. Lancez l'application :
```bash
python3 app.py
```

L'application sera accessible à `http://localhost:5000`

## Structure du projet

```
qcm_bio/
├── app.py                 # Application Flask principale
├── init_db.py            # Script d'initialisation admin
├── add_user.py           # Script pour ajouter des utilisateurs
├── static/
│   ├── style.css         # Feuille de styles
│   └── script.js         # JavaScript côté client
├── templates/
│   ├── index.html        # Page de connexion
│   ├── dashboard.html    # Tableau de bord principal
│   ├── create_quiz.html  # Formulaire de création
│   ├── take_quiz.html    # Page de passage du QCM
│   └── results.html      # Page de résultats détaillés
├── instance/
│   └── database.db       # Base de données SQLite
├── migrate_add_time_taken.py    # Migration pour ajouter timer
├── migrate_add_answers.py       # Migration pour stocker réponses
└── requirements.txt      # Dépendances Python
```

## Utilisation

### Créer un utilisateur administrateur

```bash
python3 init_db.py
```

### Ajouter des utilisateurs

```bash
python3 add_user.py
```

### Créer un QCM

1. Connectez-vous en tant qu'admin
2. Cliquez sur "Nouveau QCM"
3. Remplissez le titre, les questions, les réponses et les explications
4. Cliquez sur "Enregistrer le QCM"

### Passer un QCM

1. Connectez-vous
2. Sélectionnez un QCM dans la liste
3. Répondez aux questions (le timer tourne automatiquement)
4. Cliquez sur "Valider les réponses"
5. Consultez les résultats avec les corrections

## Base de données

Trois migrations peuvent être appliquées :
- `migrate_add_time_taken.py` : Ajoute la colonne `time_taken` si elle n'existe pas
- `migrate_add_answers.py` : Ajoute la colonne `answers` si elle n'existe pas

## Auteur

Tobias Geoffray

## Licence

MIT

