import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database import engine, Base


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "woocommerce_api_v3" in data


@pytest.mark.asyncio
async def test_woocommerce_sandbox_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Customers
        c_res = await client.get("/wp-json/wc/v3/customers")
        assert c_res.status_code == 200
        assert len(c_res.json()) > 0

        # Orders
        o_res = await client.get("/wp-json/wc/v3/orders")
        assert o_res.status_code == 200
        assert len(o_res.json()) > 0


@pytest.mark.asyncio
async def test_crm_analytics_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/analytics")
        assert res.status_code == 200
        data = res.json()
        assert "total_customers" in data
        assert "total_orders" in data
        assert "tier_distribution" in data


@pytest.mark.asyncio
async def test_webhook_simulate_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"event_type": "order.created", "customer_email": "demo.webhook@hackathon.com", "order_amount": 199.0}
        res = await client.post("/api/webhooks/simulate", params=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "simulated"
        assert data["customer_email"] == "demo.webhook@hackathon.com"


@pytest.mark.asyncio
async def test_incentive_policies_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/ai/incentive-policies")
        assert res.status_code == 200
        policies = res.json()
        assert len(policies) == 5
        policy_ids = [p["id"] for p in policies]
        assert "free_delivery" in policy_ids
        assert "extended_warranty" in policy_ids
        assert "capped_coupon" in policy_ids
        assert "vip_concierge" in policy_ids


@pytest.mark.asyncio
async def test_retention_strategy_incentive_enforcement():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test autonomous context-driven incentive selection for Customer 1 (High spend VIP)
        res = await client.post("/api/ai/retention-strategy/1?incentive_type=auto")
        assert res.status_code == 200
        data = res.json()
        assert "incentive_type" in data
        assert "incentive_rationale" in data
        assert data["incentive_type"] in ["free_delivery", "extended_warranty", "complimentary_gift", "capped_coupon", "vip_concierge"]
        # Ensure safety guardrail: no arbitrary large discounts or 500 giveaways
        assert "500" not in data["retention_action"] or "₹500" not in data["retention_action"]
        assert "recovery_message" in data


