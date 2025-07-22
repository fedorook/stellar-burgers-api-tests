import requests
from tests.config import USER_URL


class TestUserUpdate:


    def test_update_user_with_auth(self, new_user):
        """Авторизованный пользователь может изменить свои данные (имя, email или пароль)."""
        token = new_user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Новые данные для пользователя
        new_name = "UpdatedName"
        new_email = new_user["email"]  # оставим тот же email для простоты
        payload = {"email": new_email, "name": new_name}
        resp = requests.patch(USER_URL, headers=headers, json=payload)
        assert resp.status_code == 200, "Статус код должен быть 200 при обновлении с авторизацией"
        body = resp.json()
        assert body.get("success") is True
        # Проверяем, что имя действительно обновилось в ответе
        assert body["user"]["name"] == new_name, "Имя пользователя должно обновиться"
        assert body["user"]["email"] == new_email, "Email пользователя не должен измениться (мы не меняли его)"

    def test_update_user_without_auth(self):
        """Запрос на изменение профиля без токена должен возвращать 401 Unauthorized."""
        payload = {"name": "Hacker"}  # пытаемся сменить имя без авторизации
        resp = requests.patch(USER_URL, json=payload)  # без заголовка Authorization
        assert resp.status_code == 401, "Ожидается 401 Unauthorized без токена"
        body = resp.json()
        assert body.get("success") is False
        assert body.get("message") == "You should be authorised", \
            "Сообщение должно быть 'You should be authorised' при отсутствии авторизации"
