"""Tests for DELETE /api/2/item/{id} - Delete item endpoint."""

import allure
import pytest

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.data_generator import DataGenerator


@allure.feature("Delete Item")
@allure.story("Positive scenarios")
@pytest.mark.api
@pytest.mark.positive
class TestDeleteItemPositive:
    """Positive test cases for delete item endpoint."""

    @allure.title("Delete existing item")
    @allure.description("Test deleting an existing advertisement")
    def test_delete_existing_item(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test deleting existing item."""
        with allure.step("Create item to delete"):
            response = api_client.create_item(
                name=DataGenerator.item_name(),
                price=5000,
                seller_id=unique_seller_id
            )
            APIAssertions.assert_status_code(response, 200)
            created = response.json()
            item_id = created["id"]

        with allure.step(f"Delete item: {item_id}"):
            response = api_client.delete_item(item_id)

        with allure.step("Verify deletion response"):
            APIAssertions.assert_status_code(response, 200)

        with allure.step("Verify item is deleted"):
            response = api_client.get_item(item_id)
            APIAssertions.assert_status_code(response, 404)

    @allure.title("Delete item and verify it's removed from seller items")
    @allure.description("Test that deleted item no longer appears in seller's items")
    def test_delete_removes_from_seller_items(
        self,
        api_client: APIClient,
        unique_seller_id: int
    ) -> None:
        """Test that deleted item is removed from seller items."""
        with allure.step("Create item"):
            response = api_client.create_item(
                name=DataGenerator.item_name(),
                price=5000,
                seller_id=unique_seller_id
            )
            APIAssertions.assert_status_code(response, 200)
            created = response.json()
            item_id = created["id"]

        with allure.step("Verify item exists in seller items"):
            response = api_client.get_seller_items(unique_seller_id)
            APIAssertions.assert_status_code(response, 200)
            items = response.json()
            item_ids = [item["id"] for item in items]
            assert item_id in item_ids

        with allure.step(f"Delete item: {item_id}"):
            response = api_client.delete_item(item_id)
            APIAssertions.assert_status_code(response, 200)

        with allure.step("Verify item is removed from seller items"):
            response = api_client.get_seller_items(unique_seller_id)
            APIAssertions.assert_status_code(response, 200)
            items = response.json()
            item_ids = [item["id"] for item in items]
            assert item_id not in item_ids, "Deleted item still appears in seller items"


@allure.feature("Delete Item")
@allure.story("Negative scenarios")
@pytest.mark.api
@pytest.mark.negative
class TestDeleteItemNegative:
    """Negative test cases for delete item endpoint."""

    @allure.title("Delete non-existent item")
    @allure.description("Test deleting item that doesn't exist")
    def test_delete_nonexistent_item(self, api_client: APIClient) -> None:
        """Test deleting non-existent item."""
        non_existent_id = "non-existent-delete-id"

        with allure.step(f"Try to delete item: {non_existent_id}"):
            response = api_client.delete_item(non_existent_id)

        with allure.step("Verify 404 response"):
            APIAssertions.assert_status_code(response, 404)

    @allure.title("Delete already deleted item")
    @allure.description("Test deleting item that was already deleted")
    def test_delete_already_deleted(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test deleting already deleted item."""
        with allure.step("Create item"):
            response = api_client.create_item(
                name=DataGenerator.item_name(),
                price=5000,
                seller_id=unique_seller_id
            )
            APIAssertions.assert_status_code(response, 200)
            created = response.json()
            item_id = created["id"]

        with allure.step(f"Delete item first time: {item_id}"):
            response = api_client.delete_item(item_id)
            APIAssertions.assert_status_code(response, 200)

        with allure.step("Delete same item again"):
            response = api_client.delete_item(item_id)

        with allure.step("Verify response"):
            # Should return 404 since item doesn't exist
            APIAssertions.assert_status_code(response, 404)

    @allure.title("Delete item with invalid ID")
    @allure.description("Test deleting item with invalid ID format")
    @pytest.mark.parametrize("invalid_id", [
        "",
        "<script>alert(1)</script>",
        "../../../etc/passwd",
        "item' OR '1'='1",
    ])
    def test_delete_invalid_id(self, api_client: APIClient, invalid_id: str) -> None:
        """Test deleting item with invalid ID."""
        with allure.step(f"Try to delete item: {invalid_id}"):
            response = api_client.delete_item(invalid_id)

        with allure.step("Verify error response"):
            assert response.status_code in [400, 404, 500], (
                f"Expected error status, got {response.status_code}"
            )
