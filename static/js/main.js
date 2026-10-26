// Переключатель расширенной информации о матче внутри карточки.
document.addEventListener('DOMContentLoaded', function () {
    var buttons = document.querySelectorAll('.js-toggle-details');

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            var card = button.closest('.match-card');
            var details = card.querySelector('.match-details');
            var isHidden = details.hasAttribute('hidden');

            if (isHidden) {
                details.removeAttribute('hidden');
                button.textContent = 'Скрыть подробности';
                button.setAttribute('aria-expanded', 'true');
            } else {
                details.setAttribute('hidden', '');
                button.textContent = 'Подробнее';
                button.setAttribute('aria-expanded', 'false');
            }
        });
    });
});