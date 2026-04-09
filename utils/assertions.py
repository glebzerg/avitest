"""Custom assertions for API testing."""

from typing import Any, Dict, List, Optional

import allure
from requests import Response


class APIAssertions:
    """Custom assertions for API responses."""

    @staticmethod
    @allure.step("Assert status code is {expected_code}")
    def assert_status_code(response: Response, expected_code: int) -> None:
        """Assert response status code.

        Args:
            response: HTTP response
            expected_code: Expected status code

        Raises:
            AssertionError: If status code doesn't match
        """
        actual_code = response.status_code
        assert actual_code == expected_code, (
            f"Expected status code {expected_code}, got {actual_code}. "
            f"Response: {response.text}"
        )

    @staticmethod
    @allure.step("Assert response contains field '{field}'")
    def assert_field_exists(data: Dict[str, Any], field: str) -> None:
        """Assert field exists in response data.

        Args:
            data: Response data dict
            field: Field name to check

        Raises:
            AssertionError: If field doesn't exist
        """
        assert field in data, f"Field '{field}' not found in response. Fields: {list(data.keys())}"

    @staticmethod
    @allure.step("Assert field '{field}' equals {expected_value}")
    def assert_field_equals(
        data: Dict[str, Any],
        field: str,
        expected_value: Any
    ) -> None:
        """Assert field equals expected value.

        Args:
            data: Response data dict
            field: Field name
            expected_value: Expected value

        Raises:
            AssertionError: If values don't match
        """
        APIAssertions.assert_field_exists(data, field)
        actual_value = data[field]
        assert actual_value == expected_value, (
            f"Field '{field}' expected {expected_value}, got {actual_value}"
        )

    @staticmethod
    @allure.step("Assert response is valid item")
    def assert_valid_item(item: Dict[str, Any]) -> None:
        """Assert item has all required fields.

        Args:
            item: Item dictionary

        Raises:
            AssertionError: If item is invalid
        """
        required_fields = ["id", "sellerId", "name", "price", "statistics", "createdAt"]
        for field in required_fields:
            APIAssertions.assert_field_exists(item, field)

        # Validate statistics fields
        stats = item["statistics"]
        assert isinstance(stats, dict), "statistics should be a dict"
        for stat_field in ["likes", "viewCount", "contacts"]:
            assert stat_field in stats, f"statistics.{stat_field} not found"

    @staticmethod
    @allure.step("Assert response is list with {min_count} items")
    def assert_response_list(
        response: Response,
        min_count: int = 0,
        max_count: Optional[int] = None
    ) -> List[Dict]:
        """Assert response is a valid list.

        Args:
            response: HTTP response
            min_count: Minimum expected items
            max_count: Maximum expected items

        Returns:
            List of items

        Raises:
            AssertionError: If response is not valid list
        """
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"

        if min_count > 0:
            assert len(data) >= min_count, (
                f"Expected at least {min_count} items, got {len(data)}"
            )

        if max_count is not None:
            assert len(data) <= max_count, (
                f"Expected at most {max_count} items, got {len(data)}"
            )

        return data

    @staticmethod
    @allure.step("Assert error response")
    def assert_error_response(
        response: Response,
        expected_status: int,
        error_message_contains: Optional[str] = None
    ) -> None:
        """Assert error response format.

        Args:
            response: HTTP response
            expected_status: Expected error status code
            error_message_contains: Expected text in error message

        Raises:
            AssertionError: If error response is invalid
        """
        APIAssertions.assert_status_code(response, expected_status)

        data = response.json()
        assert "result" in data or "status" in data, (
            "Error response should contain 'result' or 'status' field"
        )

        if error_message_contains:
            response_text = response.text.lower()
            assert error_message_contains.lower() in response_text, (
                f"Error message should contain '{error_message_contains}'"
            )
