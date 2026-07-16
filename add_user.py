from app import app, db, User
from werkzeug.security import generate_password_hash

# --- Modifiez ici l'identifiant souhaité ---
USERNAME = "Clara"
PASSWORD = "13.05.2023"
# --------------------------------------------

def add_user():
    with app.app_context():
        existing = User.query.filter_by(username=USERNAME).first()
        if existing:
            print(f"ℹ️ L'utilisateur '{USERNAME}' existe déjà.")
            return
        new_user = User(
            username=USERNAME,
            password=generate_password_hash(PASSWORD),
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"✅ Utilisateur '{USERNAME}' créé avec succès !")

if __name__ == "__main__":
    add_user()