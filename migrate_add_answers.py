#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne answers à la table result
"""
import sqlite3
import os

DB_PATH = '/home/tobias/Bureau/1A/qcm_bio/instance/database.db'


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(result)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'answers' in columns:
            print("✅ La colonne 'answers' existe déjà.")
            return
        # Ajouter la colonne
        print("Migration: Ajout de la colonne 'answers' à la table 'result'...")
        cursor.execute("ALTER TABLE result ADD COLUMN answers TEXT")
        conn.commit()
        print("✅ Migration réussie! La colonne 'answers' a été ajoutée.")
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de données introuvable à {DB_PATH}")
    else:
        migrate()

