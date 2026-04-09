"""Tests for GET /api/1/statistic/{id} - Get statistics endpoint."""

import allure
import pytest

from utils.api_client import APIClient
from utils.assertions import APIAssertions
from utils.data_generator import DataGenerator


@allure.feature("Get Statistics")
@allure.story("Positive scenarios")
@pytest.mark.api
@pytest.mark.positive
class TestGetStatisticsPositive:
    """Positive test cases for get statistics endpoint."""

    @allure.title("Get statistics for existing item")
    @allure.description("Test retrieving statistics for a valid item")
    def test_get_statistics_existing(self, api_client: APIClient, created_item: dict) -> None:
        """Test getting statistics for existing item."""
        item_id = created_item["id"]

        with allure.step(f"Get statistics for item: {item_id}"):
            response = api_client.get_statistics(item_id)

        with allure.step("Verify response"):
            APIAssertions.assert_status_code(response, 200)
            data = response.json()

            # Response is a list with statistics
            assert isinstance(data, list), f"Expected list, got {type(data)}"
            assert len(data) > 0, "Statistics list should not be empty"

            # Verify statistics structure
            stats = data[0]
            assert "likes" in stats, "likes field not found"
            assert "viewCount" in stats, "viewCount field not found"
            assert "contacts" in stats, "contacts field not found"

            # All fields should be integers
            for field in ["likes", "viewCount", "contacts"]:
                assert isinstance(stats[field], int), (
                    f"{field} should be integer, got {type(stats[field])}"
                )

    @allure.title("Get statistics matches item statistics")
    @allure.description("Verify statistics endpoint returns same data as item endpoint")
    def test_get_statistics_matches_item(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test that statistics endpoint matches item data."""
        statistics = DataGenerator.statistics(likes=15, view_count=150, contacts=8)

        with allure.step("Create item with known statistics"):
            response = api_client.create_item(
                name=DataGenerator.item_name(),
                price=10000,
                seller_id=unique_seller_id,
                statistics=statistics
            )
            APIAssertions.assert_status_code(response, 200)
            created = response.json()
            item_id = created["id"]

        with allure.step("Get statistics via statistics endpoint"):
            response = api_client.get_statistics(item_id)
            APIAssertions.assert_status_code(response, 200)
            stats_data = response.json()
            stats = stats_data[0]

        with allure.step("Get statistics via item endpoint"):
            response = api_client.get_item(item_id)
            APIAssertions.assert_status_code(response, 200)
            item_data = response.json()
            item_stats = item_data[0]["statistics"]

        with allure.step("Verify statistics match"):
            assert stats["likes"] == item_stats["likes"]
            assert stats["viewCount"] == item_stats["viewCount"]
            assert stats["contacts"] == item_stats["contacts"]

        # Cleanup
        api_client.delete_item(item_id)

    @allure.title("Get statistics with zero values")
    @allure.description("Test statistics with all zero values")
    def test_get_statistics_zero_values(self, api_client: APIClient, unique_seller_id: int) -> None:
        """Test getting statistics with zero values."""
        statistics = DataGenerator.statistics(likes=0, view_count=0, contacts=0)

        with allure.step("Create item with zero statistics"):
            response = api_client.create_item(
                name=DataGenerator.item_name(),
                price=5000,
                seller_id=unique_seller_id,
                statistics=statistics
            )
            APIAssertions.assert_status_code(response, 200)
            created = response.json()
            item_id = created["id"]

        with allure.step("Get statistics"):
            response = api_client.get_statistics(item_id)
            APIAssertions.assert_status_code(response, 200)
            data = response.json()
            stats = data[0]

        with allure.step("Verify zero values"):
            assert stats["likes"] == 0
            assert stats["viewCount"] == 0
            assert stats["contacts"] == 0

        # Cleanup
        api_client.delete_item(item_id)


@allure.feature("Get Statistics")
@allure.story("Negative scenarios")
@pytest.mark.api
@pytest.mark.negative
class TestGetStatisticsNegative:
    """Negative test cases for get statistics endpoint."""

    @allure.title("Get statistics for non-existent item")
    @allure.description("Test retrieving statistics for item that doesn't exist")
    def test_get_statistics_nonexistent(self, api_client: APIClient) -> None:
        """Test getting statistics for non-existent item."""
        non_existent_id = "non-existent-stats-id"

        with allure.step(f"Try to get statistics for: {non_existent_id}"):
            response = api_client.get_statistics(non_existent_id)

        with allure.step("Verify 404 response"):
            APIAssertions.assert_status_code(response, 404)

    @allure.title("Get statistics with invalid ID")
    @allure.description("Test retrieving statistics with invalid item ID")
    @pytest.mark.parametrize("invalid_id", [
        "",
        "<script>alert(1)</script>",
        "../../../etc/passwd",
        "item' OR '1'='1",
        "test\n\r",
    ])
    def test_get_statistics_invalid_id(self, api_client: APIClient, invalid_id: str) -> None:
        """Test getting statistics with invalid ID."""
        with allure.step(f"Try to get statistics for: {invalid_id}"):
            response = api_client.get_statistics(invalid_id)

        with allure.step("Verify error response"):
            assert response.status_code in [400, 404, 500], (
                f"Expected error status, got {response.status_code}"
            )
