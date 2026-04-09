"""Tests for GET /api/1/item/{id} - Get item by ID endpoint."""

import allure
import pytest

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.data_generator import DataGenerator


@allure.feature("Get Item")
@allure.story("Positive scenarios")
@pytest.mark.api
@pytest.mark.positive
class TestGetItemPositive:
    """Positive test cases for get item endpoint."""

    @allure.title("Get existing item by ID")
    @allure.description("Test retrieving an item by its valid ID")
    def test_get_item_by_id(self, api_client: APIClient, created_item: dict) -> None:
        """Test getting item by valid ID."""
        item_id = created_item["id"]
        expected_name = created_item["name"]
        expected_price = created_item["price"]
        expected_seller_id = created_item["sellerId"]

        with allure.step(f"Get item by ID: {item_id}"):
            response = api_client.get_item(item_id)

        with allure.step("Verify response"):
            APIAssertions.assert_status_code(response, 200)
            data = response.json()

            # Response is a list with one item
            APIAssertions.assert_response_list(response, min_count=1, max_count=1)
            item = data[0]
            APIAssertions.assert_valid_item(item)

            # Verify data matches created item
            APIAssertions.assert_field_equals(item, "id", item_id)
            APIAssertions.assert_field_equals(item, "name", expected_name)
            APIAssertions.assert_field_equals(item, "price", expected_price)
            APIAssertions.assert_field_equals(item, "sellerId", expected_seller_id)

    @allure.title("Get item returns correct statistics")
    @allure.description("Verify that statistics are correctly returned")
    def test_get_item_statistics(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test that item statistics are correctly returned."""
        statistics = DataGenerator.statistics(likes=5, view_count=50, contacts=2)

        with allure.step("Create item with statistics"):
            response = api_client.create_item(
                name=DataGenerator.item_name(),
                price=5000,
                seller_id=unique_seller_id,
                statistics=statistics
            )
            APIAssertions.assert_status_code(response, 200)
            created = response.json()
            item_id = created["id"]

        with allure.step("Get item and verify statistics"):
            response = api_client.get_item(item_id)
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            item = data[0]

            response_stats = item["statistics"]
            assert response_stats["likes"] == statistics["likes"]
            assert response_stats["viewCount"] == statistics["viewCount"]
            assert response_stats["contacts"] == statistics["contacts"]

        # Cleanup
        api_client.delete_item(item_id)

    @allure.title("Get item returns createdAt timestamp")
    @allure.description("Verify that createdAt field is present and valid")
    def test_get_item_created_at(self, api_client: APIClient, created_item: dict) -> None:
        """Test that createdAt timestamp is returned."""
        item_id = created_item["id"]

        with allure.step(f"Get item: {item_id}"):
            response = api_client.get_item(item_id)

        with allure.step("Verify createdAt field"):
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            item = data[0]

            APIAssertions.assert_field_exists(item, "createdAt")
            created_at = item["createdAt"]
            assert isinstance(created_at, str), "createdAt should be a string"
            assert len(created_at) > 0, "createdAt should not be empty"


@allure.feature("Get Item")
@allure.story("Negative scenarios")
@pytest.mark.api
@pytest.mark.negative
class TestGetItemNegative:
    """Negative test cases for get item endpoint."""

    @allure.title("Get item with non-existent ID")
    @allure.description("Test retrieving item with ID that doesn't exist")
    def test_get_item_nonexistent_id(self, api_client: APIClient) -> None:
        """Test getting item with non-existent ID."""
        non_existent_id = "non-existent-id-12345"

        with allure.step(f"Try to get item with ID: {non_existent_id}"):
            response = api_client.get_item(non_existent_id)

        with allure.step("Verify 404 response"):
            APIAssertions.assert_status_code(response, 404)

    @allure.title("Get item with empty ID")
    @allure.description("Test retrieving item with empty ID")
    def test_get_item_empty_id(self, api_client: APIClient) -> None:
        """Test getting item with empty ID."""
        with allure.step("Try to get item with empty ID"):
            response = api_client.get_item("")

        with allure.step("Verify response"):
            # Empty ID might return 404 or be handled differently
            assert response.status_code in [404, 400, 500]

    @allure.title("Get item with special characters in ID")
    @allure.description("Test retrieving item with special characters in ID")
    @pytest.mark.parametrize("special_id", [
        "<script>alert(1)</script>",
        "../../../etc/passwd",
        "item' OR '1'='1",
        "test\n\r",
        "test\x00",
    ])
    def test_get_item_special_chars(self, api_client: APIClient, special_id: str) -> None:
        """Test getting item with special characters in ID."""
        with allure.step(f"Try to get item with ID: {special_id}"):
            response = api_client.get_item(special_id)

        with allure.step("Verify error response"):
            # Should not return 200 for invalid IDs
            assert response.status_code in [400, 404, 500], (
                f"Expected error status, got {response.status_code}"
            )

    @allure.title("Get item with very long ID")
    @allure.description("Test retrieving item with extremely long ID")
    def test_get_item_long_id(self, api_client: APIClient) -> None:
        """Test getting item with very long ID."""
        long_id = "a" * 10000

        with allure.step("Try to get item with long ID"):
            response = api_client.get_item(long_id)

        with allure.step("Verify response"):
            assert response.status_code in [400, 404, 500]
