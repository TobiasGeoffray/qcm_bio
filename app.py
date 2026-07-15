from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
        leaderboard.append((username, total_score, nb_quiz, total_possible))

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

        # Crée une liste de questions au format JSON
        questions = []
        for i in range(len(question_texts)):
            question = {
                "text": question_texts[i],
                "correct_answer": correct_answers[i],
                "wrong_answers": [wrong_answer_1s[i], wrong_answer_2s[i]],
                "explanation": (explanations[i] if i < len(explanations) else "")
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)