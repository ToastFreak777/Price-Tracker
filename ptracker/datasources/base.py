from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ProductSnapshot:
    """Standardized product data format - all sources must return this format"""

    vendor: str
    external_id: str
    name: str
    price: float
    currency: str
    in_stock: bool
    url: str
    image_url: Optional[str] = None
    timestamp: datetime = None

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
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        pass

    def extract_product_id(self, url: str) -> str:
        return url


class DataSourceError(Exception):
    """Base exception for data source errors"""

    pass


class ProductNotFoundError(DataSourceError):
    """Product doesnt't exist or was removed"""

    pass


class RateLimitError(DataSourceError):
    """API rate limit exceeded"""

    pass
