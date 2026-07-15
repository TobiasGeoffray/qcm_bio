function addQuestion() {
    const container = document.getElementById('questions-container');
    const newQuestion = document.createElement('div');
    newQuestion.className = 'question';
    newQuestion.innerHTML = `
        <input type="text" name="question_text[]" placeholder="Texte de la question" required>
        <input type="text" name="correct_answer[]" placeholder="Bonne réponse" required>
        <input type="text" name="wrong_answer_1[]" placeholder="Mauvaise réponse 1" required>
        <input type="text" name="wrong_answer_2[]" placeholder="Mauvaise réponse 2" required>
        <textarea name="explanation[]" placeholder="Explication / correction (visible dans les résultats)" rows="2"></textarea>
    `;
    container.appendChild(newQuestion);
}