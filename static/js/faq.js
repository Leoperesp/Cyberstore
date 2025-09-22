document.addEventListener('DOMContentLoaded', function() {
    // Selecciona todos los botones de pregunta y las respuestas
    const questionButtons = document.querySelectorAll('.question-btn');
    const answerContainers = document.querySelectorAll('.answer');

    // Oculta todas las respuestas al cargar la página
    answerContainers.forEach(answer => {
        answer.style.display = 'none';
    });

    // Añade un 'event listener' a cada botón
    questionButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Obtiene el identificador de la pregunta del atributo 'data-question'
            const questionId = button.getAttribute('data-question');

            // Oculta todas las respuestas de nuevo antes de mostrar la correcta
            answerContainers.forEach(answer => {
                answer.style.display = 'none';
            });

            // Muestra solo la respuesta que coincide con el 'id'
            const targetAnswer = document.querySelector(`.answer[data-answer="${questionId}"]`);
            if (targetAnswer) {
                targetAnswer.style.display = 'block';
            }
        });
    });
});