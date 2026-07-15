from app import app, db, User
from werkzeug.security import generate_password_hash

def init_admin():
    with app.app_context():
        # Vérifie si l'admin existe déjà
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            # Crée l'admin
            admin = User(
                username="admin",
                password=generate_password_hash("admin123"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Utilisateur admin créé avec succès !")
        else:
            print("ℹ️ L'utilisateur admin existe déjà.")

if __name__ == "__main__":
    init_admin()