from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ProductSnapshot:
    """Standardized product data format - all sources must return this format"""

    vendor: str
    external_id: str  # Vendor's product ID
    name: str
    price: float
    currency: str
    in_stock: bool
    url: str
    image_url: str | None = None
    timestamp: datetime | None = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class DataSource(ABC):
    """Interface for all product data sources"""

    @property
    @abstractmethod
    def vendor_name(self) -> str:
        pass

    @abstractmethod
    def fetch_product(self, identifier: str) -> ProductSnapshot:
        """
        Fetch product data from vendor API using product ID

        Args:
            identifier: Vendor's external product ID

        Returns:
             ProductSnapshot with current product data

        Raises:
            DataSourceError: For general data source errors
            ProductNotFoundError: If product doesn't exist
            RateLimitError: If API rate limit is exceeded
        """

        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        pass

    def extract_product_id(self, url: str) -> str:
        """
        Extract product identifer from URL

        Args:
            url (str): Product URL

        Returns:
            Product ID/external ID used by vendor's API

        Raises:
            ValueError: If URL format is invalid
        """

        return url

    def fetch_from_url(self, url: str) -> ProductSnapshot:

        if not self.validate_url(url):
            raise ValueError(f"Invalid URL for vendor {self.vendor_name}: {url}")

        product_id = self.extract_product_id(url)
        return self.fetch_product(product_id)


class DataSourceError(Exception):
    """Base exception for data source errors"""

    pass


class ProductNotFoundError(DataSourceError):
    """Product doesnt't exist or was removed"""

    pass


class RateLimitError(DataSourceError):
    """API rate limit exceeded"""

    pass
