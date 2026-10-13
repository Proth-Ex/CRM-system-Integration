import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models.customer import Customer
from backend.app.models.order import Order
from backend.app.models.communication import CommunicationLog
from backend.app.models.workflow import WorkflowRule
from backend.app.services.crm_service import CRMService

# Use in-memory SQLite database for fast unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    # Pre-seed test workflow
    workflow = WorkflowRule(
        name="Test Followup",
        trigger_event="order.completed",
        action_config={"subject": "Thanks!", "body": "Hello {first_name}, order #{order_id} total {total}"},
        is_active=True
    )
    db.add(workflow)
    db.commit()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_calculate_customer_tier():
    """Verify RFM segmentation logic."""
    assert CRMService.calculate_customer_tier(35000.0, 5) == "VIP"
    assert CRMService.calculate_customer_tier(12000.0, 2) == "Loyal"
    assert CRMService.calculate_customer_tier(2500.0, 1) == "New"
    assert CRMService.calculate_customer_tier(0.0, 0) == "Lead"


def test_sync_customer_from_wc_data(db_session):
    """Verify Customer creation and property mapping from WooCommerce payload."""
    payload = {
        "id": 99,
        "email": "test.user@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
        "billing": {"phone": "+1234567890", "city": "Seattle"},
        "shipping": {"city": "Seattle"},
        "total_spent": "550.00",
        "orders_count": 3
    }
    customer = CRMService.sync_customer_from_wc_data(db_session, payload)

    assert customer is not None
    assert customer.email == "test.user@example.com"
    assert customer.first_name == "Alice"
    assert customer.total_spent == 550.0
    assert customer.orders_count == 3
    assert customer.avg_order_value == round(550.0 / 3, 2)
    assert customer.tier == "Loyal"


def test_sync_order_triggers_metrics_and_workflow(db_session):
    """Verify order ingestion, LTV calculation, and automated workflow trigger."""
    order_payload = {
        "id": 8801,
        "status": "completed",
        "currency": "USD",
        "total": "400.00",
        "total_tax": "30.00",
        "shipping_total": "0.00",
        "billing": {
            "first_name": "Bob",
            "last_name": "Taylor",
            "email": "bob.taylor@example.com",
            "phone": "+1987654321"
        },
        "line_items": [
            {"id": 1, "name": "Mechanical Keyboard", "quantity": 1, "total": "400.00"}
        ]
    }

    order = CRMService.sync_order_from_wc_data(db_session, order_payload)

    assert order is not None
    assert order.wc_order_id == 8801
    assert order.total == 400.0
    assert order.status == "completed"

    # Customer should be created and linked automatically
    customer = db_session.query(Customer).filter(Customer.email == "bob.taylor@example.com").first()
    assert customer is not None
    assert customer.total_spent == 400.0
    assert customer.orders_count == 1
    assert customer.tier == "New"

    # Verify workflow generated communication log
    comms = db_session.query(CommunicationLog).filter(CommunicationLog.customer_id == customer.id).all()
    assert len(comms) == 1
    assert "workflow:Test Followup" in comms[0].trigger_source
    assert "Bob" in comms[0].content
    assert "#8801" in comms[0].content


def test_crm_analytics(db_session):
    """Verify aggregate analytics generation."""
    analytics = CRMService.get_crm_analytics(db_session)
    assert "total_customers" in analytics
    assert "total_orders" in analytics
    assert "total_revenue" in analytics
    assert "tier_distribution" in analytics
