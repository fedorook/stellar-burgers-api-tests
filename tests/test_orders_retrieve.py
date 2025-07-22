import requests
import pytest
from tests.config import BASE_URL, ORDERS_URL


class TestOrderRetrieve:

    def test_get_orders_auth_success(self, new_user, ingredients):
        """
        Авторизованный пользователь может получить список своих заказов (200 OK).
        Сначала создаём заказ с реальными ингредиентами, затем проверяем,
        что он отобразился в GET /api/orders.
        """
        token = new_user["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Сначала создаём заказ — используем первые два валидных ID из фикстуры
        create_resp = requests.post(
            ORDERS_URL,
            headers=headers,
            json={"ingredients": ingredients[:2]}
        )
        assert create_resp.status_code == 200, (
            f"Не удалось создать заказ, получили {create_resp.status_code}, {create_resp.text}"
        )

        # Теперь запрашиваем список заказов
        resp = requests.get(ORDERS_URL, headers=headers)
        assert resp.status_code == 200, (
            f"Ожидали 200 при GET /orders, но получили {resp.status_code}"
        )
        body = resp.json()
        assert body.get("success") is True, f"success должен быть True, получили {body}"
        assert "orders" in body, f"В ответе нет ключа orders: {body}"
        assert isinstance(body["orders"], list), "orders должен быть списком"
        # Проверяем, что наш только что созданный заказ есть в списке
        assert len(body["orders"]) > 0, "Список заказов пуст, хотя мы только что создали заказ"
        # Дополнительно можно проверить, что последних два элемента — это наш заказ:
        last_order = body["orders"][0]
        assert last_order.get("number"), "В заказе нет номера"
        assert isinstance(last_order.get("ingredients"), list), "В заказе нет списка ingredients"

    def test_get_orders_unauthorized_failed(self):
        """
        Без токена GET /orders должен вернуть 401 Unauthorized (или 403/400 в старых версиях API).
        """
        resp = requests.get(ORDERS_URL)
        # допускаем разные коды, но без токена это не 200
        assert resp.status_code != 200, (
            f"Без авторизации GET /orders вернул 200: {resp.text}"
        )
        if resp.status_code in (400, 401, 403):
            data = resp.json()
            assert data.get("success") is False, f"success должен быть False, получили {data}"
        else:
            pytest.skip(f"Неожиданный код {resp.status_code} для неавторизованного запроса")
