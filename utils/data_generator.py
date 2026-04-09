"""Data generators for test data."""

import random
import string
from typing import Dict

from allure import step


class DataGenerator:
    """Generator for test data."""

    @staticmethod
    @step("Generate random string of length {length}")
    def random_string(length: int = 10) -> str:
        """Generate random string.

        Args:
            length: String length

        Returns:
            Random string
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    @step("Generate random item name")
    def item_name() -> str:
        """Generate random item name.

        Returns:
            Item name
        """
        prefixes = ["Персидский", "Британский", "Сиамский", "Мейн-кун", "Бенгальский"]
        suffixes = ["котёнок", "кот", "кошка", "котик"]
        return f"{random.choice(prefixes)} {random.choice(suffixes)} {DataGenerator.random_string(5)}"

    @staticmethod
    @step("Generate random price")
    def price(min_val: int = 100, max_val: int = 100000) -> int:
        """Generate random price.

        Args:
            min_val: Minimum price
            max_val: Maximum price

        Returns:
            Random price
        """
        return random.randint(min_val, max_val)

    @staticmethod
    @step("Generate seller ID")
    def seller_id(min_val: int = 111111, max_val: int = 999999) -> int:
        """Generate random seller ID.

        Args:
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Random seller ID
        """
        return random.randint(min_val, max_val)

    @staticmethod
    @step("Generate statistics")
    def statistics(
        likes: int = 0,
        view_count: int = 0,
        contacts: int = 0
    ) -> Dict[str, int]:
        """Generate statistics dict.

        Args:
            likes: Number of likes
            view_count: View count
            contacts: Contact count

        Returns:
            Statistics dictionary
        """
        return {
            "likes": likes,
            "viewCount": view_count,
            "contacts": contacts
        }

    @staticmethod
    @step("Generate complete item data")
    def item_data(seller_id: int = 0) -> Dict:
        """Generate complete item data.

        Args:
            seller_id: Seller ID (0 for auto-generate)

        Returns:
            Complete item data
        """
        if seller_id == 0:
            seller_id = DataGenerator.seller_id()

        return {
            "sellerID": seller_id,
            "name": DataGenerator.item_name(),
            "price": DataGenerator.price(),
            "statistics": DataGenerator.statistics(
                likes=random.randint(0, 100),
                view_count=random.randint(0, 1000),
                contacts=random.randint(0, 50)
            )
        }
