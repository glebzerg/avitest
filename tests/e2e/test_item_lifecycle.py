"""E2E tests for complete item lifecycle scenarios."""

import allure
import pytest

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.data_generator import DataGenerator


@allure.feature("E2E Scenarios")
@allure.story("Item Lifecycle")
@pytest.mark.e2e
class TestItemLifecycle:
    """End-to-end tests for complete item lifecycle."""

    @allure.title("Complete item lifecycle: Create → Get → Get Stats → Delete → Verify")
    @allure.description("Test complete lifecycle of an advertisement")
    def test_complete_item_lifecycle(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test complete item lifecycle flow."""
        item_name = DataGenerator.item_name()
        item_price = 25000
        statistics = DataGenerator.statistics(likes=20, view_count=200, contacts=10)

        # Step 1: Create item
        with allure.step("1. Create new advertisement"):
            response = api_client.create_item(
                name=item_name,
                price=item_price,
                seller_id=unique_seller_id,
                statistics=statistics
            )
            APIAssertions.assert_status_code(response, 200)
            created = response.json()
            APIAssertions.assert_valid_item(created)
            item_id = created["id"]
            allure.attach(item_id, "Created Item ID", allure.attachment_type.TEXT)

        # Step 2: Get item by ID
        with allure.step("2. Get item by ID"):
            response = api_client.get_item(item_id)
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            item = data[0]
            APIAssertions.assert_field_equals(item, "id", item_id)
            APIAssertions.assert_field_equals(item, "name", item_name)
            APIAssertions.assert_field_equals(item, "price", item_price)
            APIAssertions.assert_field_equals(item, "sellerId", unique_seller_id)

        # Step 3: Get seller items
        with allure.step("3. Get all items for seller"):
            response = api_client.get_seller_items(unique_seller_id)
            APIAssertions.assert_status_code(response, 200)
            items = response.json()
            item_ids = [i["id"] for i in items]
            assert item_id in item_ids, "Created item not found in seller items"

        # Step 4: Get statistics
        with allure.step("4. Get item statistics"):
            response = api_client.get_statistics(item_id)
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            stats = data[0]
            assert stats["likes"] == statistics["likes"]
            assert stats["viewCount"] == statistics["viewCount"]
            assert stats["contacts"] == statistics["contacts"]

        # Step 5: Delete item
        with allure.step("5. Delete item"):
            response = api_client.delete_item(item_id)
            APIAssertions.assert_status_code(response, 200)

        # Step 6: Verify deletion
        with allure.step("6. Verify item is deleted"):
            response = api_client.get_item(item_id)
            APIAssertions.assert_status_code(response, 404)

    @allure.title("Multiple items lifecycle for same seller")
    @allure.description("Test creating, retrieving and deleting multiple items for one seller")
    def test_multiple_items_lifecycle(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test lifecycle with multiple items."""
        created_items = []

        # Step 1: Create multiple items
        with allure.step("1. Create 5 items for same seller"):
            for i in range(5):
                response = api_client.create_item(
                    name=f"Item {i} - {DataGenerator.random_string()}",
                    price=DataGenerator.price(),
                    seller_id=unique_seller_id
                )
                APIAssertions.assert_status_code(response, 200)
                created_items.append(response.json())

            allure.attach(
                str([item["id"] for item in created_items]),
                "Created Item IDs",
                allure.attachment_type.TEXT
            )

        # Step 2: Verify all items exist
        with allure.step("2. Verify all items exist"):
            response = api_client.get_seller_items(unique_seller_id)
            APIAssertions.assert_status_code(response, 200)
            items = response.json()
            created_ids = {item["id"] for item in created_items}
            response_ids = {item["id"] for item in items}
            assert created_ids.issubset(response_ids), "Not all items found"

        # Step 3: Delete all items
        with allure.step("3. Delete all created items"):
            for item in created_items:
                response = api_client.delete_item(item["id"])
                APIAssertions.assert_status_code(response, 200)

        # Step 4: Verify all deleted
        with allure.step("4. Verify all items are deleted"):
            for item in created_items:
                response = api_client.get_item(item["id"])
                APIAssertions.assert_status_code(response, 404)

    @allure.title("Item update simulation via delete and recreate")
    @allure.description("Simulate update by deleting and creating new item")
    def test_item_update_simulation(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test update simulation via delete and recreate."""
        original_name = "Original Item"
        original_price = 10000
        updated_name = "Updated Item"
        updated_price = 15000

        # Step 1: Create original item
        with allure.step("1. Create original item"):
            response = api_client.create_item(
                name=original_name,
                price=original_price,
                seller_id=unique_seller_id
            )
            APIAssertions.assert_status_code(response, 200)
            original = response.json()
            original_id = original["id"]

        # Step 2: Delete original
        with allure.step("2. Delete original item"):
            response = api_client.delete_item(original_id)
            APIAssertions.assert_status_code(response, 200)

        # Step 3: Create updated item
        with allure.step("3. Create updated item"):
            response = api_client.create_item(
                name=updated_name,
                price=updated_price,
                seller_id=unique_seller_id
            )
            APIAssertions.assert_status_code(response, 200)
            updated = response.json()
            updated_id = updated["id"]

        # Step 4: Verify new item exists with updated data
        with allure.step("4. Verify updated item"):
            response = api_client.get_item(updated_id)
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            item = data[0]
            APIAssertions.assert_field_equals(item, "name", updated_name)
            APIAssertions.assert_field_equals(item, "price", updated_price)

        # Step 5: Verify old item is deleted
        with allure.step("5. Verify original item is deleted"):
            response = api_client.get_item(original_id)
            APIAssertions.assert_status_code(response, 404)

        # Cleanup
        api_client.delete_item(updated_id)


@allure.feature("E2E Scenarios")
@allure.story("Idempotency Tests")
@pytest.mark.e2e
class TestIdempotency:
    """Tests for idempotency scenarios."""

    @allure.title("Create item with same data multiple times creates different items")
    @allure.description("Verify that creating items with same data creates separate items")
    def test_create_idempotency(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test that creating same item multiple times creates different items."""
        name = "Idempotency Test Item"
        price = 5000
        created_items = []

        with allure.step("Create same item 3 times"):
            for _ in range(3):
                response = api_client.create_item(name, price, unique_seller_id)
                APIAssertions.assert_status_code(response, 200)
                created_items.append(response.json())

        with allure.step("Verify different IDs"):
            ids = [item["id"] for item in created_items]
            assert len(set(ids)) == 3, "Items should have different IDs"

        with allure.step("Verify same data"):
            for item in created_items:
                assert item["name"] == name
                assert item["price"] == price
                assert item["sellerId"] == unique_seller_id

        # Cleanup
        for item in created_items:
            api_client.delete_item(item["id"])

    @allure.title("Delete item is idempotent - second delete returns 404")
    @allure.description("Verify that deleting already deleted item returns 404")
    def test_delete_idempotency(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test delete idempotency."""
        with allure.step("Create item"):
            response = api_client.create_item(
                name="Delete Idempotency Test",
                price=5000,
                seller_id=unique_seller_id
            )
            APIAssertions.assert_status_code(response, 200)
            item_id = response.json()["id"]

        with allure.step("Delete item first time"):
            response = api_client.delete_item(item_id)
            APIAssertions.assert_status_code(response, 200)

        with allure.step("Delete item second time - should return 404"):
            response = api_client.delete_item(item_id)
            APIAssertions.assert_status_code(response, 404)

        with allure.step("Delete item third time - should still return 404"):
            response = api_client.delete_item(item_id)
            APIAssertions.assert_status_code(response, 404)
