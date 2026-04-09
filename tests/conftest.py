"""Pytest fixtures and configuration."""

import pytest
from utils.api_client import APIClient
from utils.data_generator import DataGenerator


@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """Create API client session fixture.

    Returns:
        APIClient instance
    """
    return APIClient()


@pytest.fixture(scope="function")
def unique_seller_id() -> int:
    """Generate unique seller ID for each test.

    Returns:
        Random seller ID
    """
    return DataGenerator.seller_id()


@pytest.fixture(scope="function")
def created_item(api_client: APIClient, unique_seller_id: int):
    """Create item and yield it, then cleanup.

    Args:
        api_client: API client fixture
        unique_seller_id: Seller ID fixture

    Yields:
        Created item data
    """
    item_data = DataGenerator.item_data(unique_seller_id)
    response = api_client.create_item(
        name=item_data["name"],
        price=item_data["price"],
        seller_id=item_data["sellerID"],
        statistics=item_data["statistics"]
    )

    assert response.status_code == 200, f"Failed to create item: {response.text}"
    created = response.json()

    yield created

    # Cleanup: try to delete the item
    if "id" in created:
        api_client.delete_item(created["id"])


@pytest.fixture(scope="function")
def multiple_items(api_client: APIClient, unique_seller_id: int):
    """Create multiple items for same seller.

    Args:
        api_client: API client fixture
        unique_seller_id: Seller ID fixture

    Yields:
        List of created items and seller ID
    """
    items = []
    for _ in range(3):
        item_data = DataGenerator.item_data(unique_seller_id)
        response = api_client.create_item(
            name=item_data["name"],
            price=item_data["price"],
            seller_id=item_data["sellerID"],
            statistics=item_data["statistics"]
        )
        if response.status_code == 200:
            items.append(response.json())

    yield {"items": items, "seller_id": unique_seller_id}

    # Cleanup
    for item in items:
        if "id" in item:
            api_client.delete_item(item["id"])
