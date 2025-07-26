import time
import requests
import pytest
from tests.config import REGISTER_URL, USER_URL, INGREDIENTS_URL


@pytest.fixture
def new_user():
    """Фикстура для регистрации нового пользователя и очистки после теста."""
    # Генерируем уникальные данные пользователя
    timestamp = str(time.time()).replace('.', '')
    email = f"test{timestamp}@example.com"
    password = "testPassword"
    name = "TestUser"
    # Регистрируем пользователя через API
    response = requests.post(REGISTER_URL, json={
        "email": email,
        "password": password,
        "name": name
    })
    # Убедимся, что пользователь успешно создан
    assert response.status_code == 200 and response.json().get("success") is True
    data = response.json()
    # Получаем токен авторизации для последующих запросов
    access_token: str = data.get("accessToken")
    # Убираем префикс 'Bearer ', если он есть, для удобства использования
    if access_token.startswith("Bearer "):
        access_token = access_token.split("Bearer ")[1]
    # Отдаем тесту данные пользователя
    yield {"email": email, "password": password, "token": access_token}
    # После выполнения теста – удаляем созданного пользователя через API
    headers = {"Authorization": f"Bearer {access_token}"}
    requests.delete(USER_URL, headers=headers)

@pytest.fixture(scope="session")
def ingredients():
    """Возвращает список всех доступных ingredient_id из API."""
    resp = requests.get(INGREDIENTS_URL)
    assert resp.status_code == 200, f"Не удалось получить ингредиенты: {resp.status_code}"
    data = resp.json()
    # В стертчной API-спецификации возвращается ключ 'data'
    items = data.get("data", [])
    assert items, "Список ингредиентов пуст"
    # Собираем первые два ID как валидные
    ids = [item["_id"] for item in items]
    return ids