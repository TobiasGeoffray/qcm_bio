function addQuestion() {
    const container = document.getElementById('questions-container');
    const questionIndex = container.children.length;
    const newQuestion = document.createElement('div');
    newQuestion.className = 'question';
    newQuestion.innerHTML = `
        <input type="text" name="question_text[]" placeholder="Texte de la question" required>
        <input type="text" name="correct_answer[]" placeholder="Bonne réponse" required>
        <input type="text" name="wrong_answer_1[]" placeholder="Mauvaise réponse 1" required>
        <input type="text" name="wrong_answer_2[]" placeholder="Mauvaise réponse 2" required>
        <textarea name="explanation[]" placeholder="Explication" rows="2" style="width:70%;margin-top: 5px;"></textarea>
        <div style="margin-top: 10px;">
            <label for="question_image_${questionIndex}" style="display: block; margin-bottom: 5px;">Image (optionnelle) :</label>
            <input type="file" id="question_image_${questionIndex}" name="question_image[]" accept="image/*">
        </div>
    `;
    container.appendChild(newQuestion);
}