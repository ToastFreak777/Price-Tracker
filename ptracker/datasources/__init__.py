from .base import (
    DataSource,
    ProductSnapshot,
    DataSourceError,
    ProductNotFoundError,
    RateLimitError,
)
from .mock import MockDataSource

# from .ebay import EbayDataSource


class DataSourceFactory:
    _sources = {}

    @classmethod
    def register(cls, vendor: str, source: DataSource):
        """Register or add a data source"""
        cls._sources[vendor] = source

    @classmethod
    def get(cls, vendor: str) -> DataSource:
        """Get data source by vendor name"""
        if vendor not in cls._sources:
            raise ValueError(f"Unknown vendor: {vendor}")
        return cls._sources[vendor]

    @classmethod
    def detect_vendor(cls, url: str) -> str:
        """Detect vendor from URL"""
        for vendor, source in cls._sources.items():
            if source.validate_url(url):
                return vendor
        raise ValueError(f"Could not detect vendor from URL: {url}")


# Initialize available sources
def init_datasources(app):
    """Initialize data sources with config"""
    # Always available for testing
    DataSourceFactory.register("mock", MockDataSource())

    # eBay (when credentials available)
    # ebay_key = app.config.get("EBAY_API_KEY")
    # if ebay_key:
    #     DataSourceFactory.register("ebay", EbayDataSource(api_key=ebay_key))


__all__ = [
    "DataSource",
    "ProductSnapshot",
    "DataSourceError",
    "ProductNotFoundError",
    "RateLimitError",
    "DataSourceFactory",
    "MockDataSource",
    # "EbayDataSource",
    "init_datasources",
]
