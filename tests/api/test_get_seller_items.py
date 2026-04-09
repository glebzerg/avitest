"""Tests for GET /api/1/{sellerID}/item - Get all items by seller endpoint."""

import allure
import pytest

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.data_generator import DataGenerator


@allure.feature("Get Seller Items")
@allure.story("Positive scenarios")
@pytest.mark.api
@pytest.mark.positive
class TestGetSellerItemsPositive:
    """Positive test cases for get seller items endpoint."""

    @allure.title("Get items for seller with multiple items")
    @allure.description("Test retrieving all items for a seller with multiple ads")
    def test_get_seller_multiple_items(self, api_client: APIClient, multiple_items: dict) -> None:
        """Test getting items for seller with multiple ads."""
        seller_id = multiple_items["seller_id"]
        created_items = multiple_items["items"]

        with allure.step(f"Get items for seller: {seller_id}"):
            response = api_client.get_seller_items(seller_id)

        with allure.step("Verify response"):
            APIAssertions.assert_status_code(response, 200)
            items = APIAssertions.assert_response_list(
                response,
                min_count=len(created_items)
            )

            # Verify all created items are present
            created_ids = {item["id"] for item in created_items}
            response_ids = {item["id"] for item in items}

            assert created_ids.issubset(response_ids), (
                f"Not all created items found. Expected: {created_ids}, Got: {response_ids}"
            )

    @allure.title("Get items for seller with single item")
    @allure.description("Test retrieving items for seller with one ad")
    def test_get_seller_single_item(self, api_client: APIClient, created_item: dict) -> None:
        """Test getting items for seller with single item."""
        seller_id = created_item["sellerId"]
        item_id = created_item["id"]

        with allure.step(f"Get items for seller: {seller_id}"):
            response = api_client.get_seller_items(seller_id)

        with allure.step("Verify response"):
            APIAssertions.assert_status_code(response, 200)
            items = APIAssertions.assert_response_list(response, min_count=1)

            # Verify our item is in the list
            item_ids = [item["id"] for item in items]
            assert item_id in item_ids, f"Created item {item_id} not found in response"

    @allure.title("Get items returns valid item structure")
    @allure.description("Verify that all returned items have valid structure")
    def test_get_seller_items_structure(self, api_client: APIClient, multiple_items: dict) -> None:
        """Test that all returned items have valid structure."""
        seller_id = multiple_items["seller_id"]

        with allure.step(f"Get items for seller: {seller_id}"):
            response = api_client.get_seller_items(seller_id)

        with allure.step("Verify all items have valid structure"):
            APIAssertions.assert_status_code(response, 200)
            items = response.json()

            for item in items:
                APIAssertions.assert_valid_item(item)

    @allure.title("Get items for seller - verify sellerId consistency")
    @allure.description("Verify all returned items have the same sellerId")
    def test_get_seller_items_consistency(
        self,
        api_client: APIClient,
        multiple_items: dict
    ) -> None:
        """Test that all items have consistent sellerId."""
        seller_id = multiple_items["seller_id"]

        with allure.step(f"Get items for seller: {seller_id}"):
            response = api_client.get_seller_items(seller_id)

        with allure.step("Verify sellerId consistency"):
            APIAssertions.assert_status_code(response, 200)
            items = response.json()

            for item in items:
                assert item["sellerId"] == seller_id, (
                    f"Item {item['id']} has sellerId {item['sellerId']}, "
                    f"expected {seller_id}"
                )


@allure.feature("Get Seller Items")
@allure.story("Negative scenarios")
@pytest.mark.api
@pytest.mark.negative
class TestGetSellerItemsNegative:
    """Negative test cases for get seller items endpoint."""

    @allure.title("Get items for non-existent seller")
    @allure.description("Test retrieving items for seller that doesn't exist")
    def test_get_seller_nonexistent(self, api_client: APIClient) -> None:
        """Test getting items for non-existent seller."""
        non_existent_seller = 999999999

        with allure.step(f"Try to get items for seller: {non_existent_seller}"):
            response = api_client.get_seller_items(non_existent_seller)

        with allure.step("Verify response"):
            # API returns 200 with empty list for non-existent sellers
            APIAssertions.assert_status_code(response, 200)
            items = response.json()
            assert isinstance(items, list), "Response should be a list"
            # Empty list is acceptable for non-existent sellers

    @allure.title("Get items with invalid sellerID format")
    @allure.description("Test retrieving items with invalid sellerID")
    @pytest.mark.parametrize("invalid_seller_id", [
        "invalid",
        "abc123",
        "",
        "-1",
        "1.5",
    ])
    def test_get_seller_invalid_id(self, api_client: APIClient, invalid_seller_id) -> None:
        """Test getting items with invalid seller ID."""
        with allure.step(f"Try to get items for seller: {invalid_seller_id}"):
            response = api_client.session.get(
                f"{api_client.base_url}/api/1/{invalid_seller_id}/item"
            )

        with allure.step("Verify error response"):
            # Should return error for invalid seller ID
            assert response.status_code in [400, 404, 500], (
                f"Expected error status, got {response.status_code}"
            )

    @allure.title("Get items with negative sellerID")
    @allure.description("Test retrieving items with negative sellerID")
    def test_get_seller_negative_id(self, api_client: APIClient) -> None:
        """Test getting items with negative seller ID."""
        with allure.step("Try to get items for seller: -123"):
            response = api_client.get_seller_items(-123)

        with allure.step("Verify response"):
            # API behavior for negative IDs
            if response.status_code == 200:
                items = response.json()
                # Empty list or error is acceptable
                assert isinstance(items, list)
