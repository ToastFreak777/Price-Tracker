import requests

from dotenv import dotenv_values

config = dotenv_values(".env")

url = "https://real-time-amazon-data.p.rapidapi.com/search"

headers = {
    "x-rapidapi-key": config.get("RAPID_API_KEY"),
    "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
}


def price_to_cents(price_str: str) -> int | None:
    """Convert price string like '$128.98' to integer cents (12898)."""
    if not price_str:
        return None
    return int(float(price_str.replace("$", "").replace(",", "").strip()) * 100)


def search(query):
    query_string = {
        "query": query,
        "page": "1",
        "country": "US",
        "sort_by": "RELEVANCE",
        "product_condition": "ALL",
        "is_prime": "false",
        "deals_and_discounts": "NONE",
    }

    response = requests.get(url, headers=headers, params=query_string)
    data = response.json().get("data")

    products = []
    for item in data.get("products", []):
        product = {
            "source": data.get("domain"),
            "source_id": item.get("asin"),
            "title": item.get("product_title"),
            "price_cents": price_to_cents(item.get("product_price")),
            "currency": item.get("currency"),
            "original_price_cents": price_to_cents(item.get("product_original_price")),
            "url": item.get("product_url"),
            "image": item.get("product_photo"),
            "availability": item.get("product_availability"),
            "minimum_offer_price_cents": price_to_cents(
                item.get("product_minimum_offer_price")
            ),
        }
        products.append(product)

    return products
