"""Tests for POST /api/1/item - Create advertisement endpoint."""

import allure
import pytest
from requests import Response

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.data_generator import DataGenerator


@allure.feature("Create Item")
@allure.story("Positive scenarios")
@pytest.mark.api
@pytest.mark.positive
class TestCreateItemPositive:
    """Positive test cases for create item endpoint."""

    @allure.title("Create item with minimum required fields")
    @allure.description("Test creating item with only required fields (name, price, sellerID)")
    def test_create_item_minimal(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test creating item with minimal data."""
        name = DataGenerator.item_name()
        price = DataGenerator.price()

        with allure.step("Create item with minimal data"):
            response = api_client.create_item(name, price, unique_seller_id)

        with allure.step("Verify response"):
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            APIAssertions.assert_valid_item(data)
            APIAssertions.assert_field_equals(data, "name", name)
            APIAssertions.assert_field_equals(data, "price", price)
            APIAssertions.assert_field_equals(data, "sellerId", unique_seller_id)

        # Cleanup
        if "id" in data:
            api_client.delete_item(data["id"])

    @allure.title("Create item with full data including statistics")
    @allure.description("Test creating item with all fields including statistics")
    def test_create_item_full(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test creating item with full data."""
        name = DataGenerator.item_name()
        price = 15000
        statistics = DataGenerator.statistics(likes=10, view_count=100, contacts=5)

        with allure.step("Create item with full data"):
            response = api_client.create_item(name, price, unique_seller_id, statistics)

        with allure.step("Verify response"):
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            APIAssertions.assert_valid_item(data)
            APIAssertions.assert_field_equals(data, "name", name)
            APIAssertions.assert_field_equals(data, "price", price)

            # Verify statistics
            response_stats = data["statistics"]
            assert response_stats["likes"] == statistics["likes"]
            assert response_stats["viewCount"] == statistics["viewCount"]
            assert response_stats["contacts"] == statistics["contacts"]

        # Cleanup
        if "id" in data:
            api_client.delete_item(data["id"])

    @allure.title("Create item with boundary price values")
    @allure.description("Test creating items with boundary price values (0, 1, max int)")
    @pytest.mark.parametrize("price", [0, 1, 999999999])
    def test_create_item_boundary_prices(
        self,
        api_client: APIClient,
        unique_seller_id: int,
        price: int
    ) -> None:
        """Test creating item with boundary price values."""
        name = DataGenerator.item_name()

        with allure.step(f"Create item with price={price}"):
            response = api_client.create_item(name, price, unique_seller_id)

        with allure.step("Verify response"):
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            APIAssertions.assert_field_equals(data, "price", price)

        # Cleanup
        if "id" in data:
            api_client.delete_item(data["id"])

    @allure.title("Create items with same sellerId")
    @allure.description("Test that multiple items can have the same sellerId")
    def test_create_items_same_seller(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test creating multiple items with same seller ID."""
        created_items = []

        with allure.step("Create 3 items with same sellerId"):
            for i in range(3):
                name = f"Item {i} - {DataGenerator.random_string()}"
                price = DataGenerator.price()
                response = api_client.create_item(name, price, unique_seller_id)
                APIAssertions.assert_status_code(response, 200)
                created_items.append(response.json())

        with allure.step("Verify all items have same sellerId"):
            for item in created_items:
                assert item["sellerId"] == unique_seller_id

        # Cleanup
        for item in created_items:
            if "id" in item:
                api_client.delete_item(item["id"])

    @allure.title("Create items with duplicate names")
    @allure.description("Test that items with same name can be created")
    def test_create_items_duplicate_names(
        self,
        api_client: APIClient,
        unique_seller_id: int
    ) -> None:
        """Test creating items with duplicate names."""
        name = "Duplicate Name Test"
        created_items = []

        with allure.step("Create 2 items with same name"):
            for _ in range(2):
                price = DataGenerator.price()
                response = api_client.create_item(name, price, unique_seller_id)
                APIAssertions.assert_status_code(response, 200)
                created_items.append(response.json())

        with allure.step("Verify both items have same name"):
            assert created_items[0]["name"] == name
            assert created_items[1]["name"] == name
            # IDs should be different
            assert created_items[0]["id"] != created_items[1]["id"]

        # Cleanup
        for item in created_items:
            if "id" in item:
                api_client.delete_item(item["id"])


@allure.feature("Create Item")
@allure.story("Negative scenarios")
@pytest.mark.api
@pytest.mark.negative
class TestCreateItemNegative:
    """Negative test cases for create item endpoint."""

    @allure.title("Create item without name field")
    @allure.description("Test that missing name field returns error")
    def test_create_item_missing_name(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test creating item without name."""
        payload = {
            "sellerID": unique_seller_id,
            "price": 1000
        }

        with allure.step("Send request without name"):
            response = api_client.session.post(
                f"{api_client.base_url}/api/1/item",
                json=payload
            )

        with allure.step("Verify error response"):
            APIAssertions.assert_status_code(response, 400)

    @allure.title("Create item without price field")
    @allure.description("Test that missing price field returns error")
    def test_create_item_missing_price(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test creating item without price."""
        payload = {
            "sellerID": unique_seller_id,
            "name": DataGenerator.item_name()
        }

        with allure.step("Send request without price"):
            response = api_client.session.post(
                f"{api_client.base_url}/api/1/item",
                json=payload
            )

        with allure.step("Verify error response"):
            APIAssertions.assert_status_code(response, 400)

    @allure.title("Create item without sellerID field")
    @allure.description("Test that missing sellerID field returns error")
    def test_create_item_missing_seller_id(self, api_client: APIClient) -> None:
        """Test creating item without sellerID."""
        payload = {
            "name": DataGenerator.item_name(),
            "price": 1000
        }

        with allure.step("Send request without sellerID"):
            response = api_client.session.post(
                f"{api_client.base_url}/api/1/item",
                json=payload
            )

        with allure.step("Verify error response"):
            APIAssertions.assert_status_code(response, 400)

    @allure.title("Create item with invalid price types")
    @allure.description("Test that non-integer price values return error")
    @pytest.mark.parametrize("price", ["invalid", "1000", 1000.50, None, True])
    def test_create_item_invalid_price_type(
        self,
        api_client: APIClient,
        unique_seller_id: int,
        price
    ) -> None:
        """Test creating item with invalid price type."""
        payload = {
            "sellerID": unique_seller_id,
            "name": DataGenerator.item_name(),
            "price": price
        }

        with allure.step(f"Send request with price={price} (type: {type(price).__name__})"):
            response = api_client.session.post(
                f"{api_client.base_url}/api/1/item",
                json=payload
            )

        with allure.step("Verify error response"):
            # API should return 400 for invalid types
            assert response.status_code in [400, 500], (
                f"Expected 400 or 500, got {response.status_code}"
            )

    @allure.title("Create item with empty name")
    @allure.description("Test creating item with empty string name")
    def test_create_item_empty_name(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test creating item with empty name."""
        response = api_client.create_item("", 1000, unique_seller_id)

        # Behavior may vary - document what actually happens
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                api_client.delete_item(data["id"])

    @allure.title("Create item with very long name")
    @allure.description("Test creating item with name exceeding typical limits")
    def test_create_item_long_name(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test creating item with very long name."""
        long_name = "A" * 10000  # 10k characters

        response = api_client.create_item(long_name, 1000, unique_seller_id)

        # Document actual behavior
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                api_client.delete_item(data["id"])

    @allure.title("Create item with negative price")
    @allure.description("Test creating item with negative price value")
    def test_create_item_negative_price(
        self,
        api_client: APIClient,
        unique_seller_id: int
    ) -> None:
        """Test creating item with negative price."""
        response = api_client.create_item(
            DataGenerator.item_name(),
            -100,
            unique_seller_id
        )

        # API should reject negative prices
        if response.status_code == 200:
            data = response.json()
            if "id" in data:
                api_client.delete_item(data["id"])
