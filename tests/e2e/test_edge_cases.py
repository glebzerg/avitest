"""E2E tests for edge cases and boundary conditions."""

import allure
import pytest

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.data_generator import DataGenerator


@allure.feature("E2E Scenarios")
@allure.story("Edge Cases")
@pytest.mark.e2e
class TestEdgeCases:
    """Edge case tests."""

    @allure.title("Create item with maximum integer values")
    @allure.description("Test creating item with very large integer values")
    def test_maximum_integer_values(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test with maximum integer values."""
        max_int = 2147483647  # Max 32-bit signed integer

        with allure.step(f"Create item with price={max_int}"):
            response = api_client.create_item(
                name="Max Price Test",
                price=max_int,
                seller_id=unique_seller_id
            )

        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                api_client.delete_item(data["id"])

    @allure.title("Create item with unicode name")
    @allure.description("Test creating item with unicode characters in name")
    def test_unicode_name(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test with unicode characters."""
        unicode_names = [
            "🐱 Персидский котёнок",
            "日本語テスト",
            "العربية",
            "Special chars: <>&\"'",
        ]

        for name in unicode_names:
            with allure.step(f"Test name: {name}"):
                response = api_client.create_item(
                    name=name,
                    price=1000,
                    seller_id=unique_seller_id
                )

                if response.status_code == 200:
                    data = response.json()
                    if "id" in data:
                        api_client.delete_item(data["id"])

    @allure.title("Rapid create and delete operations")
    @allure.description("Test rapid sequential create and delete operations")
    def test_rapid_operations(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test rapid operations."""
        item_ids = []

        with allure.step("Rapidly create 10 items"):
            for i in range(10):
                response = api_client.create_item(
                    name=f"Rapid Item {i}",
                    price=1000 + i,
                    seller_id=unique_seller_id
                )
                if response.status_code == 200:
                    item_ids.append(response.json()["id"])

        with allure.step("Rapidly delete all items"):
            for item_id in item_ids:
                api_client.delete_item(item_id)

        with allure.step("Verify all deleted"):
            for item_id in item_ids:
                response = api_client.get_item(item_id)
                assert response.status_code == 404

    @allure.title("Concurrent seller operations")
    @allure.description("Test operations with multiple different sellers")
    def test_multiple_sellers(self, api_client: APIClient) -> None:
        """Test with multiple sellers."""
        sellers_data = {}

        with allure.step("Create items for 5 different sellers"):
            for _ in range(5):
                seller_id = DataGenerator.seller_id()
                items = []
                for i in range(3):
                    response = api_client.create_item(
                        name=f"Seller {seller_id} Item {i}",
                        price=1000 * (i + 1),
                        seller_id=seller_id
                    )
                    if response.status_code == 200:
                        items.append(response.json())
                sellers_data[seller_id] = items

        with allure.step("Verify each seller only sees their items"):
            for seller_id, items in sellers_data.items():
                response = api_client.get_seller_items(seller_id)
                APIAssertions.assert_status_code(response, 200)
                seller_items = response.json()
                seller_item_ids = {item["id"] for item in seller_items}

                for item in items:
                    assert item["id"] in seller_item_ids, (
                        f"Item {item['id']} not found for seller {seller_id}"
                    )

        with allure.step("Cleanup all items"):
            for items in sellers_data.values():
                for item in items:
                    if "id" in item:
                        api_client.delete_item(item["id"])
