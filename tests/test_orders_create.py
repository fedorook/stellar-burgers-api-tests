import requests
from tests.config import ORDERS_URL



class TestOrderCreate:

    def test_create_order_auth_success(self, new_user, ingredients):
        """Авторизованный пользователь может создать заказ с реальными ингредиентами."""
        token = new_user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"ingredients": ingredients[:2]}
        resp = requests.post(ORDERS_URL, headers=headers, json=payload)
        assert resp.status_code == 200, f"Ожидали 200, получили {resp.status_code}, тело: {resp.text}"
        data = resp.json()
        assert data.get("success") is True, f"success должен быть True, тело: {resp.text}"
        assert "order" in data and data["order"].get("number"), f"В ответе нет номера заказа, тело: {resp.text}"

    def test_create_order_unauthorized_behavior(self, ingredients):
        """
        Попытка создать заказ без токена:
        API может разрешить анонимный заказ (200) или вернуть ошибку (400/401).
        Проверяем оба варианта.
        """
        payload = {"ingredients": ingredients[:2]}
        resp = requests.post(ORDERS_URL, json=payload)

        if resp.status_code == 200:
            data = resp.json()
            assert data.get("success") is True, f"Ожидали success=True, получили {data}"
            assert "order" in data and data["order"].get("number"), f"Нет номера заказа в {data}"
        else:
            assert resp.status_code in (400, 401), f"Ожидали 200, 400 или 401, но получили {resp.status_code}"
            data = resp.json()
            assert data.get("success") is False, f"При ошибке success должен быть False, получили {data}"

    def test_create_order_no_ingredients_failed(self, new_user):
        """Пустой список ингредиентов — Bad Request (400)."""
        token = new_user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(ORDERS_URL, headers=headers, json={"ingredients": []})
        assert resp.status_code == 400, f"Ожидали 400 при отсутствии ингредиентов, получили {resp.status_code}, тело: {resp.text}"
        data = resp.json()
        assert data.get("success") is False
        assert data.get("message") == "Ingredient ids must be provided", f"Неверное сообщение: {data}"

    def test_create_order_invalid_ingredient_failed(self, new_user):
        """Неверный ID ингредиента — сервер возвращает ошибку 400 или 500."""
        token = new_user["token"]
        headers = {"Authorization": f"Bearer {token}"}
        fake_id = "611111111111111111111111"
        resp = requests.post(ORDERS_URL, headers=headers, json={"ingredients": [fake_id]})
        assert resp.status_code in (400, 500), f"Ожидали 400 или 500, получили {resp.status_code}, тело: {resp.text}"
        try:
            data = resp.json()
            assert data.get("success") is False, f"success должен быть False, получили {data}"
        except ValueError:
            # иногда тело ответа не JSON
            pass
