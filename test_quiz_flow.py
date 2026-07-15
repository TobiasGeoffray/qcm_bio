from app import app, db, User, Quiz, Result
import json

with app.app_context():
    # Nettoyer/test setup: créer un user test
    test_user = User.query.filter_by(username='test_user').first()
    if not test_user:
        test_user = User(username='test_user', password='fakehash', is_admin=False)
        db.session.add(test_user)
        db.session.commit()

    # Créer un quiz de test
    questions = [
        {"text": "2+2?", "correct_answer": "4", "wrong_answers": ["3", "5"], "explanation": "2+2 égale 4."},
        {"text": "Capital de France?", "correct_answer": "Paris", "wrong_answers": ["Lyon", "Marseille"], "explanation": "Paris est la capitale."}
    ]
    quiz = Quiz(title='Quiz Test', questions=json.dumps(questions))
    db.session.add(quiz)
    db.session.commit()

    quiz_id = quiz.id

    # Utiliser le test client pour simuler la soumission
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
        sess['username'] = test_user.username

    # Préparer données de formulaire
    data = {
        'answer_0': '4',
        'answer_1': 'Lyon',
        'time_taken': '7'
    }
    resp = client.post(f'/take_quiz/{quiz_id}', data=data, follow_redirects=False)
    print('POST status:', resp.status_code, 'Location:', resp.headers.get('Location'))

    # Vérifier résultat
    last_result = Result.query.order_by(Result.id.desc()).first()
    print('Last result:', last_result.id, last_result.user_id, last_result.quiz_id, last_result.score, last_result.time_taken, last_result.answers)
    if last_result and last_result.answers:
        print('Answers JSON:', json.loads(last_result.answers))
    else:
        print('No answers stored')

