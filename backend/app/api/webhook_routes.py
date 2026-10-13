from fastapi import APIRouter, Depends, Request, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import logging

from backend.app.database import get_db
from backend.app.services.crm_service import CRMService

webhook_router = APIRouter(prefix="/api/webhooks", tags=["WooCommerce Webhook Ingestion"])
logger = logging.getLogger(__name__)


@webhook_router.post("/woocommerce")
async def handle_woocommerce_webhook(
    request: Request,
    x_wc_webhook_topic: Optional[str] = Header(None),
    x_wc_webhook_resource: Optional[str] = Header(None),
    x_wc_webhook_event: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Ingests standard WooCommerce Webhooks (e.g. order.created, order.updated, customer.created).
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    topic = x_wc_webhook_topic or f"{x_wc_webhook_resource}.{x_wc_webhook_event}"
    logger.info(f"Received WooCommerce Webhook: {topic}")

    result = {}
    if "order" in str(topic).lower():
        order = CRMService.sync_order_from_wc_data(db, body)
        result = {"event": topic, "processed_order_id": order.id if order else None}
    elif "customer" in str(topic).lower():
        customer = CRMService.sync_customer_from_wc_data(db, body)
        result = {"event": topic, "processed_customer_id": customer.id if customer else None}
    else:
        # Fallback inspection
        if "line_items" in body or "total" in body:
            order = CRMService.sync_order_from_wc_data(db, body)
            result = {"event": "inferred_order", "processed_order_id": order.id if order else None}
        elif "email" in body:
            customer = CRMService.sync_customer_from_wc_data(db, body)
            result = {"event": "inferred_customer", "processed_customer_id": customer.id if customer else None}

    return {"status": "success", "data": result}


@webhook_router.post("/simulate")
async def simulate_wc_event(
    event_type: str = "order.created",
    customer_email: Optional[str] = None,
    order_amount: float = 349.00,
    db: Session = Depends(get_db)
):
    """
    Test endpoint for live demonstration:
    Simulates a WooCommerce event triggering our webhook pipeline.
    """
    import random
    fake_order_id = random.randint(6000, 9999)
    email = customer_email or f"user{fake_order_id}@hackathon.demo"

    fake_order_payload = {
        "id": fake_order_id,
        "number": str(fake_order_id),
        "status": "processing" if event_type == "order.created" else "completed",
        "currency": "USD",
        "date_created": "2026-04-13T10:00:00",
        "total": str(order_amount),
        "total_tax": "25.00",
        "shipping_total": "0.00",
        "billing": {
            "first_name": "Demo",
            "last_name": f"Customer {fake_order_id}",
            "email": email,
            "phone": "+1-800-555-0199",
            "city": "Bengaluru",
            "country": "IN"
        },
        "shipping": {
            "first_name": "Demo",
            "last_name": f"Customer {fake_order_id}",
            "city": "Bengaluru",
            "country": "IN"
        },
        "payment_method_title": "Credit Card (Simulated)",
        "customer_note": "Demo event from hackathon presentation",
        "line_items": [
            {
                "id": 1,
                "name": "Smart Ultra Earbuds",
                "product_id": 105,
                "quantity": 1,
                "subtotal": str(order_amount),
                "total": str(order_amount),
                "price": order_amount
            }
        ]
    }

    order = CRMService.sync_order_from_wc_data(db, fake_order_payload)
    return {
        "status": "simulated",
        "event": event_type,
        "generated_order_id": order.id,
        "wc_order_id": order.wc_order_id,
        "customer_email": order.customer_email,
        "order_total": order.total,
        "order_status": order.status
    }
