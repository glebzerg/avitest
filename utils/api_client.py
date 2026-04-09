"""API client for Avito QA internship service."""

import random
from typing import Any, Dict, List, Optional

import requests
from allure import step


class APIClient:
    """Client for interacting with the Avito QA internship API."""

    def __init__(self, base_url: str = "https://qa-internship.avito.com") -> None:
        """Initialize API client with base URL.

        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    @step("Generate unique seller ID")
    def generate_seller_id(self, min_val: int = 111111, max_val: int = 999999) -> int:
        """Generate unique seller ID in specified range.

        Args:
            min_val: Minimum value for seller ID
            max_val: Maximum value for seller ID

        Returns:
            Random seller ID
        """
        return random.randint(min_val, max_val)

    @step("Create advertisement: name={name}, price={price}, sellerId={seller_id}")
    def create_item(
        self,
        name: str,
        price: int,
        seller_id: int,
        statistics: Optional[Dict[str, int]] = None
    ) -> requests.Response:
        """Create new advertisement.

        Args:
            name: Advertisement name
            price: Advertisement price
            seller_id: Seller identifier
            statistics: Optional statistics data

        Returns:
            API response
        """
        payload: Dict[str, Any] = {
            "sellerID": seller_id,
            "name": name,
            "price": price
        }

        if statistics:
            payload["statistics"] = statistics

        response = self.session.post(
            f"{self.base_url}/api/1/item",
            json=payload
        )
        return response

    @step("Get item by ID: {item_id}")
    def get_item(self, item_id: str) -> requests.Response:
        """Get advertisement by ID.

        Args:
            item_id: Advertisement identifier

        Returns:
            API response
        """
        response = self.session.get(
            f"{self.base_url}/api/1/item/{item_id}"
        )
        return response

    @step("Get all items for seller: {seller_id}")
    def get_seller_items(self, seller_id: int) -> requests.Response:
        """Get all advertisements for a seller.

        Args:
            seller_id: Seller identifier

        Returns:
            API response
        """
        response = self.session.get(
            f"{self.base_url}/api/1/{seller_id}/item"
        )
        return response

    @step("Get statistics for item: {item_id}")
    def get_statistics(self, item_id: str) -> requests.Response:
        """Get statistics for an advertisement.

        Args:
            item_id: Advertisement identifier

        Returns:
            API response
        """
        response = self.session.get(
            f"{self.base_url}/api/1/statistic/{item_id}"
        )
        return response

    @step("Delete item: {item_id}")
    def delete_item(self, item_id: str) -> requests.Response:
        """Delete advertisement by ID.

        Args:
            item_id: Advertisement identifier

        Returns:
            API response
        """
        response = self.session.delete(
            f"{self.base_url}/api/2/item/{item_id}"
        )
        return response

    @step("Create item with full data")
    def create_item_full(
        self,
        name: str = "Test Item",
        price: int = 1000,
        seller_id: Optional[int] = None,
        likes: int = 0,
        view_count: int = 0,
        contacts: int = 0
    ) -> requests.Response:
        """Create item with full statistics.

        Args:
            name: Item name
            price: Item price
            seller_id: Seller ID (generated if None)
            likes: Number of likes
            view_count: View count
            contacts: Contact count

        Returns:
            API response
        """
        if seller_id is None:
            seller_id = self.generate_seller_id()

        statistics = {
            "likes": likes,
            "viewCount": view_count,
            "contacts": contacts
        }

        return self.create_item(name, price, seller_id, statistics)
