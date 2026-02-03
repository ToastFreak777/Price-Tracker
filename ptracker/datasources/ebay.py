import requests
import time
import re
from .base import DataSource, ProductSnapshot, DataSourceError, ProductNotFoundError, RateLimitError


class EbayDataSource(DataSource):
    """eBay API data source"""

    _TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
    _ITEM_URL = "https://api.ebay.com/buy/browse/v1/item/{}"

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

        self._access_token = None
        self._token_expires_at = 0

    @property
    def vendor_name(self) -> str:
        return "ebay"

    def _get_token(self) -> str:
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token

        response = requests.post(
            self._TOKEN_URL,
            auth=(self.api_key, self.api_secret),
            data={
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            raise DataSourceError(f"ebay auth failed!: {response.text}")

        data = response.json()
        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"] - 60
        return self._access_token

    def _to_rest_id(self, legacy_id: str) -> str:
        return f"v1|{legacy_id}|0"

    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid eBay product page"""
        ebay_patterns = [
            r"ebay\.com/itm/",
            r"ebay\.com/.*/\d+",
        ]
        return any(re.search(pattern, url) for pattern in ebay_patterns)

    def extract_product_id(self, url: str) -> str:
        """Extract eBay item ID from URL"""
        # eBay URLs: https://www.ebay.com/itm/123456789
        match = re.search(r"/itm/(\d+)", url)
        if match:
            return match.group(1)
        # Try end of URL
        match = re.search(r"/(\d+)(?:\?|$)", url)
        if match:
            return match.group(1)
        return url

    def fetch_product(self, identifier: str) -> ProductSnapshot:
        """Fetch product from eBay API"""

        rest_id = self._to_rest_id(identifier)

        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
        }

        url = self._ITEM_URL.format(rest_id)
        response = requests.get(url, headers=headers)

        if response.status_code == 404:
            raise ProductNotFoundError("Item not found on ebay")
        if response.status_code == 429:
            raise RateLimitError("eBay API rate limit exceeded")
        if response.status_code != 200:
            raise DataSourceError(f"eBay API error: {response.text}")

        data = response.json()
        avail = data.get("availability", [{}])[0]
        in_stock = avail.get("estimatedAvailabilityStatus") == "IN_STOCK"

        return ProductSnapshot(
            vendor=self.vendor_name,
            external_id=data.get("legacyItemId"),
            name=data.get("title"),
            price=float(data["price"]["value"]),
            currency=data["price"]["currency"],
            in_stock=in_stock,
            url=data.get("itemWebUrl"),
            image_url=data.get("image", {}).get("imageUrl"),
        )
