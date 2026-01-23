import random
from .base import DataSource, ProductSnapshot


class MockDataSource(DataSource):

    @property
    def vendor_name(self) -> str:
        return "mock"

    def validate_url(self, url: str) -> bool:
        return url.startswith("https://mock.com/")

    def fetch_product(self, identifier: str) -> ProductSnapshot:
        base_price = 99.99
        variation = random.uniform(-10, 10)

        return ProductSnapshot(
            vendor=self.vendor_name,
            external_id=identifier,
            name=f"Mock Product {identifier}",
            price=round(base_price + variation, 2),
            currency="USD",
            in_stock=random.choice([True, True, True, False]),
            url=f"https://mock.com/products/{identifier}",
            image_url=f"https://via.placeholder.com/300?text=Product+{identifier}",
        )
