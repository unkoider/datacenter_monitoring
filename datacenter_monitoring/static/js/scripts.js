document.addEventListener('DOMContentLoaded', function () {
    // Обработчик клика на кнопку "Редактировать"
    const editUserButtons = document.querySelectorAll('.edit-user-button');
    editUserButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.dataset.userId;
            // Перенаправление на страницу редактирования пользователя
            window.location.href = /edit_user/${userId};
        });
    });

    // Обработчик клика на кнопку "Удалить"
    const deleteUserButtons = document.querySelectorAll('.delete-user-button');
    deleteUserButtons.forEach(button => {
        button.addEventListener('click', function () {
            const userId = this.dataset.userId;
            // Подтверждение удаления пользователя
            if (confirm('Вы уверены, что хотите удалить пользователя?')) {
                // Отправка запроса на удаление пользователя
                fetch(/delete_user/${userId}, {
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