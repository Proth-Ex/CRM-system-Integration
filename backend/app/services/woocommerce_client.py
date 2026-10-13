import httpx
from typing import List, Dict, Any, Optional
import logging
from backend.app.config import settings

logger = logging.getLogger(__name__)


class WooCommerceClient:
    """
    Standard WooCommerce REST API v3 Client.
    Follows the Adapter Design Pattern to connect seamlessly with:
    - Real WooCommerce instances (using Consumer Key & Consumer Secret)
    - Local or test WooCommerce Sandbox instances.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.WOOCOMMERCE_BASE_URL).rstrip("/")
        self.consumer_key = consumer_key or settings.WOOCOMMERCE_CONSUMER_KEY
        self.consumer_secret = consumer_secret or settings.WOOCOMMERCE_CONSUMER_SECRET

    def _get_auth(self) -> Optional[httpx.BasicAuth]:
        if self.consumer_key and self.consumer_secret:
            return httpx.BasicAuth(self.consumer_key, self.consumer_secret)
        return None

    async def get_customers(self, per_page: int = 50, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch customers from WooCommerce."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.base_url}/customers"
            params = {"per_page": per_page, "page": page}
            response = await client.get(url, params=params, auth=self._get_auth())
            response.raise_for_status()
            return response.json()

    async def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """Fetch a specific customer by ID."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.base_url}/customers/{customer_id}"
            response = await client.get(url, auth=self._get_auth())
            response.raise_for_status()
            return response.json()

    async def get_orders(self, status: Optional[str] = None, per_page: int = 50, page: int = 1) -> List[Dict[str, Any]]:
        """Fetch orders from WooCommerce."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.base_url}/orders"
            params = {"per_page": per_page, "page": page}
            if status:
                params["status"] = status
            response = await client.get(url, params=params, auth=self._get_auth())
            response.raise_for_status()
            return response.json()

    async def get_order(self, order_id: int) -> Dict[str, Any]:
        """Fetch a specific order by ID."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.base_url}/orders/{order_id}"
            response = await client.get(url, auth=self._get_auth())
            response.raise_for_status()
            return response.json()

    async def update_order_status(self, order_id: int, new_status: str) -> Dict[str, Any]:
        """Update order status in WooCommerce."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.base_url}/orders/{order_id}"
            response = await client.put(url, json={"status": new_status}, auth=self._get_auth())
            response.raise_for_status()
            return response.json()

    async def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Create order in WooCommerce."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = f"{self.base_url}/orders"
            response = await client.post(url, json=payload, auth=self._get_auth())
            response.raise_for_status()
            return response.json()


# Singleton instance
woo_client = WooCommerceClient()
