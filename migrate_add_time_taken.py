#!/usr/bin/env python3
"""
Script de migration pour ajouter la colonne time_taken à la table result
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

        if 'time_taken' in columns:
            print("✅ La colonne 'time_taken' existe déjà.")
            return

        # Ajouter la colonne
        print("Migration: Ajout de la colonne 'time_taken' à la table 'result'...")
        cursor.execute("ALTER TABLE result ADD COLUMN time_taken INTEGER DEFAULT 0 NOT NULL")

        conn.commit()
        print("✅ Migration réussie! La colonne 'time_taken' a été ajoutée.")

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

