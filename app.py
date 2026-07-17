from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'cours')
app.config['IMG_UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'img')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB max
ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Création des dossiers d'upload s'ils n'existent pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['IMG_UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# Modèles de la base de données
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    questions = db.Column(db.String(5000), nullable=False)  # Stocké sous forme JSON

class Cour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, default=0, nullable=False)  # Temps en secondes
    answers = db.Column(db.String(5000), nullable=True)  # JSON string des réponses de l'utilisateur
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# Création de la base de données
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['username'] = user.username
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        flash('Identifiants incorrects.', 'error')
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    quizzes = Quiz.query.all()
    cours = Cour.query.all()

    # Classement général : score total par utilisateur, trié du plus haut au plus bas
    leaderboard_raw = db.session.query(
        User.username,
        db.func.sum(Result.score).label('total_score'),
        db.func.count(Result.id).label('nb_quiz')
    ).join(Result, Result.user_id == User.id) \
     .group_by(User.id) \
     .order_by(db.func.sum(Result.score).desc()) \
     .all()

    # Construire un leaderboard détaillé avec le total possible (nombre de questions jouées)
    import json as _json
    leaderboard = []
    # Construire les lignes du leaderboard en calculant le total possible (nombre de questions jouées)
    for username, total_score, nb_quiz in leaderboard_raw:
        user = User.query.filter_by(username=username).first()
        total_possible = 0
        if user:
            user_results = Result.query.filter_by(user_id=user.id).all()
            for r in user_results:
                quiz_obj = Quiz.query.get(r.quiz_id)
                if quiz_obj:
                    try:
                        qs = _json.loads(quiz_obj.questions)
                        total_possible += len(qs)
                    except Exception:
                        pass
        # Calcul de la moyenne en pourcentage (0 si total_possible == 0)
        average_pct = (total_score / total_possible) if total_possible > 0 else 0
        leaderboard.append({
            'username': username,
            'total_score': total_score,
            'nb_quiz': nb_quiz,
            'total_possible': total_possible,
            'average_pct': average_pct
        })

    # Trier le leaderboard par moyenne décroissante (puis, par score total en cas d'égalité)
    leaderboard = sorted(
        leaderboard,
        key=lambda u: (u['average_pct'], u['total_score']),
        reverse=True
    )

    # Détail de tous les résultats individuels (utilisateur / QCM / score / date)
    # On récupère aussi l'ID du quiz pour déterminer le nombre total de questions
    raw_results = db.session.query(
        User.username,
        Quiz.id,
        Quiz.title,
        Result.score,
        Result.timestamp,
        Result.time_taken
    ).join(User, Result.user_id == User.id) \
     .join(Quiz, Result.quiz_id == Quiz.id) \
     .order_by(Result.id.desc()) \
     .all()

    import json as _json
    all_results = []
    for username, quiz_id, quiz_title, score, timestamp, time_taken in raw_results:
        total_questions = 0
        try:
            quiz_obj = Quiz.query.get(quiz_id)
            if quiz_obj:
                qs = _json.loads(quiz_obj.questions)
                total_questions = len(qs)
        except Exception:
            total_questions = 0
        all_results.append((username, quiz_title, score, timestamp, time_taken, total_questions))

    return render_template(
        'dashboard.html',
        quizzes=quizzes,
        cours=cours,
        is_admin=session.get('is_admin'),
        leaderboard=leaderboard,
        all_results=all_results
    )

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        print("Données reçues :", request.form)  # Affiche dans le terminal
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        title = request.form['title']
        # Récupère toutes les questions et réponses
        question_texts = request.form.getlist('question_text[]')
        correct_answers = request.form.getlist('correct_answer[]')
        wrong_answer_1s = request.form.getlist('wrong_answer_1[]')
        wrong_answer_2s = request.form.getlist('wrong_answer_2[]')
        explanations = request.form.getlist('explanation[]')
        # Récupère les images
        question_images = request.files.getlist('question_image[]')

        # Crée une liste de questions au format JSON
        questions = []
        for i in range(len(question_texts)):
            # Gestion de l'image si elle a été uploadée
            image_filename = None
            if i < len(question_images) and question_images[i].filename != '':
                file = question_images[i]
                if allowed_image_file(file.filename):
                    import time
                    filename = secure_filename(file.filename)
                    # Ajouter un timestamp pour éviter les doublons
                    filename = f"{int(time.time())}_{i}_{filename}"
                    filepath = os.path.join(app.config['IMG_UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    image_filename = filename

            question = {
                "text": question_texts[i],
                "correct_answer": correct_answers[i],
                "wrong_answers": [wrong_answer_1s[i], wrong_answer_2s[i]],
                "explanation": (explanations[i] if i < len(explanations) else ""),
                "image": image_filename
            }
            questions.append(question)

        # Convertis en JSON pour stockage
        import json
        questions_json = json.dumps(questions)

        # Crée le QCM
        new_quiz = Quiz(title=title, questions=questions_json)
        db.session.add(new_quiz)
        db.session.commit()
        flash('QCM créé avec succès !', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_quiz.html')

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    quiz = Quiz.query.get_or_404(quiz_id)
    # Supprime d'abord les résultats liés à ce QCM
    Result.query.filter_by(quiz_id=quiz_id).delete()
    db.session.delete(quiz)
    db.session.commit()
    flash('QCM supprimé avec succès !', 'success')
    return redirect(url_for('dashboard'))

@app.route('/take_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        # Récupère les questions depuis le JSON
        import json
        questions = json.loads(quiz.questions)

        # Récupère les réponses de l'utilisateur
        answers = {}
        for i in range(len(questions)):
            answer_key = f"answer_{i}"
            if answer_key in request.form:
                answers[i] = request.form[answer_key]

        # Calcule le score
        score = 0
        for i, question in enumerate(questions):
            if i in answers and answers[i] == question['correct_answer']:
                score += 1

        # Enregistre le résultat (y compris les réponses de l'utilisateur)
        import json as _json
        time_taken = int(request.form.get('time_taken', 0))
        answers_json = _json.dumps(answers)
        new_result = Result(user_id=session['user_id'], quiz_id=quiz_id, score=score, time_taken=time_taken, answers=answers_json)
        db.session.add(new_result)
        db.session.commit()
        return redirect(url_for('results', result_id=new_result.id))

    # Affiche le QCM
    import json
    questions = json.loads(quiz.questions)
    # Mélange l'ordre des réponses pour chaque question
    for question in questions:
        all_answers = [question['correct_answer']] + question['wrong_answers']
        random.shuffle(all_answers)
        question['all_answers'] = all_answers
    return render_template('take_quiz.html', quiz=quiz, questions=questions)

@app.route('/results/<int:result_id>')
def results(result_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    result = Result.query.get_or_404(result_id)
    quiz = Quiz.query.get_or_404(result.quiz_id)
    import json
    questions = json.loads(quiz.questions)  # Décode le JSON
    # Récupère les réponses de l'utilisateur si présentes
    user_answers = {}
    if result.answers:
        try:
            user_answers = json.loads(result.answers)
        except Exception:
            user_answers = {}

    return render_template('results.html', result=result, quiz=quiz, questions=questions, user_answers=user_answers)

@app.route('/create_cour', methods=['GET', 'POST'])
def create_cour():
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        # Vérifier qu'un titre et un fichier sont fournis
        if 'title' not in request.form or not request.form['title']:
            flash('Le titre du cours est requis.', 'error')
            return redirect(url_for('create_cour'))
        
        if 'pdf_file' not in request.files:
            flash('Aucun fichier PDF fourni.', 'error')
            return redirect(url_for('create_cour'))
        
        file = request.files['pdf_file']
        
        if file.filename == '':
            flash('Aucun fichier sélectionné.', 'error')
            return redirect(url_for('create_cour'))
        
        if not allowed_file(file.filename):
            flash('Seuls les fichiers PDF sont autorisés.', 'error')
            return redirect(url_for('create_cour'))
        
        # Sauvegarder le fichier avec un nom sécurisé
        filename = secure_filename(file.filename)
        # Ajouter un timestamp pour éviter les doublons
        import time
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Créer l'enregistrement dans la BD
        title = request.form['title']
        new_cour = Cour(title=title, filename=filename)
        db.session.add(new_cour)
        db.session.commit()
        
        flash('Cours créé avec succès !', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_cour.html')

@app.route('/view_cour/<int:cour_id>')
def view_cour(cour_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cour = Cour.query.get_or_404(cour_id)
    pdf_url = url_for('static', filename=f'cours/{cour.filename}')

    return render_template('view_cour.html', cour=cour, pdf_url=pdf_url)

@app.route('/download_cour/<int:cour_id>')
def download_cour(cour_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    cour = Cour.query.get_or_404(cour_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], cour.filename)
    
    if not os.path.exists(filepath):
        flash('Le fichier du cours n\'existe plus.', 'error')
        return redirect(url_for('dashboard'))
    
    return send_file(filepath, as_attachment=True, download_name=f"{cour.title}.pdf")

@app.route('/delete_cour/<int:cour_id>', methods=['POST'])
def delete_cour(cour_id):
    if not session.get('is_admin'):
        return redirect(url_for('dashboard'))
    
    cour = Cour.query.get_or_404(cour_id)
    
    # Supprimer le fichier du serveur
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], cour.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Supprimer l'enregistrement de la BD
    db.session.delete(cour)
    db.session.commit()
    
    flash('Cours supprimé avec succès !', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)