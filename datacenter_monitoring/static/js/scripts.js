document.addEventListener('DOMContentLoaded', function () {
    // Обработчик клика на кнопку "Удалить"
    const deleteUserButtons = document.querySelectorAll('.delete-user-button');
    deleteUserButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.dataset.userId;
            // Подтверждение удаления пользователя
            if (confirm('Вы уверены, что хотите удалить пользователя?')) {
                // Отправка запроса на удаление пользователя
                fetch( url_for('delete_user') /$userId, {
                    method: 'DELETE'
                })
                .then(response => {
                    if (response.ok) {
                        // Обновление страницы после удаления
                        location.reload();
                    } else {
                        alert('Ошибка удаления пользователя.');
                    }
                });
            }
        });
    });
});