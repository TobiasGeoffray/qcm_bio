"""
Script de migration pour ajouter la table Cour à la base de données existante.
Exécutez-le une seule fois après avoir mis à jour app.py
"""

from app import app, db, Cour

with app.app_context():
    print("Création de la table Cour...")
    db.create_all()
    print("✓ Table Cour créée avec succès!")
    print("Vous pouvez maintenant utiliser la fonctionnalité de gestion des cours.")

