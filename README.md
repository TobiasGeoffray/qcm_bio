# QCM Bio

Une application Flask pour créer et gérer des QCM (Questionnaires à Choix Multiples) avec scoring, timer, suivi des résultats, gestion de cours PDF et éditeur de Pixel Art.

## Fonctionnalités

- 🔐 **Authentification** : Connexion utilisateur sécurisée avec hachage de mot de passe
- 👤 **Création de compte** : Interface pour créer un nouveau compte utilisateur
- 📝 **Création de QCM** : Les administrateurs peuvent créer des QCM avec explications
- ⏱️ **Timer** : Chronomètre intégré pour mesurer le temps passé par quiz
- 📊 **Scoring** : Calcul automatique du score et du pourcentage de réussite
- 🏆 **Classement** : Leaderboard global avec scores totaux et moyennes
- 📋 **Historique** : Détail complet de tous les résultats avec timestamps
- 📖 **Correction détaillée** : Affichage des questions, réponses données, bonnes réponses et explications
- 📄 **Gestion des cours** : Upload, visualisation et téléchargement de fichiers PDF
- 🎨 **Éditeur Pixel Art** : Création et sauvegarde d'images pixel art avec gestion des couleurs
- 🖼️ **Images dans les QCM** : Ajout d'images aux questions pour un contenu riche

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
├── app.py                      # Application Flask principale
├── init_db.py                 # Script d'initialisation admin
├── add_user.py                # Script pour ajouter des utilisateurs
├── migrate_add_time_taken.py   # Migration pour ajouter timer
├── migrate_add_answers.py      # Migration pour stocker réponses
├── migrate_add_cour.py         # Migration pour ajouter table Cour
├── requirements.txt           # Dépendances Python
├── instance/
│   └── database.db            # Base de données SQLite
├── static/
│   ├── style.css              # Feuille de styles
│   ├── script.js              # JavaScript côté client
│   ├── pixelart.js            # Éditeur Pixel Art
│   ├── cours/                 # Fichiers PDF des cours
│   ├── img/                   # Images utilisateur (Pixel Art)
│   ├── img_background/        # Images de fond pour Pixel Art
│   └── img_questions/         # Images pour les questions de QCM
└── templates/
    ├── index.html             # Page de connexion
    ├── create_username.html   # Création de compte utilisateur
    ├── dashboard.html         # Tableau de bord principal
    ├── create_quiz.html       # Formulaire de création de QCM
    ├── take_quiz.html         # Page de passage du QCM
    ├── results.html           # Page de résultats détaillés
    ├── create_cour.html       # Formulaire d'upload de cours
    ├── view_cour.html         # Visualisation des cours PDF
    └── create_pixelart.html    # Éditeur Pixel Art
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

### Créer un compte utilisateur

1. Cliquez sur "Créer un compte" depuis la page de connexion
2. Remplissez le nom d'utilisateur, le mot de passe et sa confirmation
3. Connectez-vous avec vos nouveaux identifiants

### Créer un QCM

1. Connectez-vous en tant qu'admin
2. Cliquez sur "Nouveau QCM"
3. Remplissez le titre, les questions, les réponses et les explications
4. Optionnellement, ajoutez des images à vos questions
5. Cliquez sur "Enregistrer le QCM"

### Passer un QCM

1. Connectez-vous
2. Sélectionnez un QCM dans la liste
3. Répondez aux questions (le timer tourne automatiquement)
4. Cliquez sur "Valider les réponses"
5. Consultez les résultats avec les corrections

### Gérer les cours PDF

1. Connectez-vous en tant qu'admin
2. Cliquez sur "Nouveau Cours"
3. Donnez un titre et sélectionnez un fichier PDF
4. Cliquez sur "Enregistrer"
5. Les utilisateurs peuvent consulter les cours depuis le dashboard

### Créer un Pixel Art

1. Connectez-vous
2. Cliquez sur "Pixel Art" dans le menu
3. Utilisez l'éditeur pour créer votre image
4. Sauvegardez votre création
5. Les images sont stockées et accessibles pour les futurs usages

## Base de données

Trois migrations peuvent être appliquées :
- `migrate_add_time_taken.py` : Ajoute la colonne `time_taken` si elle n'existe pas
- `migrate_add_answers.py` : Ajoute la colonne `answers` si elle n'existe pas
- `migrate_add_cour.py` : Crée la table `Cour` pour la gestion des fichiers PDF

## Auteur

Tobias Geoffray

## Licence

MIT

