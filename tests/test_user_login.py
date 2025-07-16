import requests

class TestUserLogin:

    LOGIN_URL = "https://stellarburgers.nomoreparties.site/api/auth/login"

    def test_login_success(self, new_user):
        """Авторизация с корректными учетными данными должна проходить успешно (200)."""
        # new_user fixture создала пользователя, берем его email и пароль
        email = new_user["email"]
        password = new_user["password"]
        resp = requests.post(self.LOGIN_URL, json={"email": email, "password": password})
        assert resp.status_code == 200, "Статус код должен быть 200 при верном логине"
        body = resp.json()
        assert body.get("success") is True
        # Должны вернуться accessToken, refreshToken и информация о пользователе
        assert "accessToken" in body and "refreshToken" in body, "В ответе должны быть токены"
        assert body["user"]["email"] == email, "Email в ответе должен совпадать с залогиненным"
        assert body["user"]["name"], "Имя пользователя должно присутствовать в ответе"

    def test_login_wrong_credentials(self):
        """Попытка авторизации с неверным логином/паролем должна возвращать 401."""
        # Несуществующие учетные данные
        fake_email = "nonexistent@example.com"
        fake_pass = "wrongPassword"
        resp = requests.post(self.LOGIN_URL, json={"email": fake_email, "password": fake_pass})
        # Ожидаем 401 Unauthorized
        assert resp.status_code == 401, "Статус код должен быть 401 при неверных данных"
        body = resp.json()
        assert body.get("success") is False
        assert body.get("message") == "email or password are incorrect", \
            "Сообщение об ошибке должно быть о неправильных логине или пароле"
