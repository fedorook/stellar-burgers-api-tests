import requests
import uuid
import allure
from tests.config import REGISTER_URL, USER_URL


class TestUserRegister:

    @allure.description("Регистрация нового пользователя должна проходить успешно (200 OK).")
    def test_register_new_user_success(self):
        # Генерируем действительно уникальный e-mail
        email = f"user_{uuid.uuid4().hex}@example.com"
        payload = {
            "email": email,
            "password": "secret123",
            "name": "UniqueUser"
        }

        # Шаг 1: регистрация
        response = requests.post(REGISTER_URL, json=payload)
        assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}"
        body = response.json()
        assert body.get("success") is True
        assert "accessToken" in body and "refreshToken" in body

        # Шаг 2: чистка — удаляем пользователя, чтобы не засорять базу
        token = body["accessToken"]
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        headers = {"Authorization": f"Bearer {token}"}
        del_resp = requests.delete(USER_URL, headers=headers)
        # Опционально: проверяем, что удаление прошло успешно
        assert del_resp.status_code == 200 or del_resp.status_code == 202

    @allure.description("Повторная регистрация того же пользователя должна возвращать ошибку 403.")
    def test_register_existing_user_failed(self):
        # Генерируем уникальный e-mail и регистрируем его
        email = f"user_{uuid.uuid4().hex}@example.com"
        password = "password123"
        name = "DupUser"
        user_data = {"email": email, "password": password, "name": name}

        first_resp = requests.post(REGISTER_URL, json=user_data)
        assert first_resp.status_code == 200, \
            f"Предусловие: первый POST должен вернуть 200, а вернул {first_resp.status_code}"
        first_body = first_resp.json()
        token = first_body["accessToken"]
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]

        # Повторяем регистрацию тем же e-mail
        second_resp = requests.post(REGISTER_URL, json=user_data)
        assert second_resp.status_code == 403, \
            f"Ожидали 403 при дублировании, получили {second_resp.status_code}"
        error_body = second_resp.json()
        assert error_body.get("success") is False
        assert error_body.get("message") == "User already exists"

        # Чистка: удаляем созданного пользователя
        headers = {"Authorization": f"Bearer {token}"}
        del_resp = requests.delete(USER_URL, headers=headers)
        assert del_resp.status_code == 200 or del_resp.status_code == 202
