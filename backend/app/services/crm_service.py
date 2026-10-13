from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.app.models.customer import Customer
from backend.app.models.order import Order
from backend.app.models.communication import CommunicationLog
from backend.app.models.workflow import WorkflowRule
from backend.app.services.woocommerce_client import woo_client
import logging

logger = logging.getLogger(__name__)


class CRMService:
    @staticmethod
    def calculate_customer_tier(total_spent: float, orders_count: int, last_order_date: Optional[datetime] = None) -> str:
        """Calculates RFM customer tier based on INR lifetime value and order frequency."""
        if total_spent >= 30000.0 or orders_count >= 4:
            return "VIP"
        elif total_spent >= 10000.0 or orders_count >= 2:
            return "Loyal"
        elif orders_count == 1:
            return "New"
        elif orders_count == 0:
            return "Lead"
        return "Regular"

    @classmethod
    async def sync_all_from_woocommerce(cls, db: Session) -> Dict[str, int]:
        """Full bidirectional sync: Ingests Customers and Orders from WooCommerce."""
        synced_customers = 0
        synced_orders = 0

        # 1. Sync Customers
        wc_customers = await woo_client.get_customers()
        for wc_c in wc_customers:
            c = cls.sync_customer_from_wc_data(db, wc_c)
            if c:
                synced_customers += 1

        # 2. Sync Orders
        wc_orders = await woo_client.get_orders()
        for wc_o in wc_orders:
            o = cls.sync_order_from_wc_data(db, wc_o)
            if o:
                synced_orders += 1

        # 3. Recalculate customer metrics based on synced orders
        cls.recalculate_all_customer_metrics(db)

        return {"synced_customers": synced_customers, "synced_orders": synced_orders}

    @classmethod
    def sync_customer_from_wc_data(cls, db: Session, wc_data: Dict[str, Any]) -> Customer:
        """Creates or updates a customer in CRM from WooCommerce payload."""
        email = wc_data.get("email") or wc_data.get("billing", {}).get("email")
        if not email:
            return None

        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            customer = Customer(email=email)
            db.add(customer)

        customer.wc_id = wc_data.get("id")
        customer.first_name = wc_data.get("first_name") or wc_data.get("billing", {}).get("first_name", "")
        customer.last_name = wc_data.get("last_name") or wc_data.get("billing", {}).get("last_name", "")
        customer.phone = wc_data.get("billing", {}).get("phone", "") or customer.phone
        customer.billing_address = wc_data.get("billing", {})
        customer.shipping_address = wc_data.get("shipping", {})

        total_spent = float(wc_data.get("total_spent", 0.0) or 0.0)
        orders_count = int(wc_data.get("orders_count", 0) or 0)
        customer.total_spent = total_spent
        customer.orders_count = orders_count
        customer.avg_order_value = round(total_spent / orders_count, 2) if orders_count > 0 else 0.0
        customer.tier = cls.calculate_customer_tier(total_spent, orders_count)

        db.commit()
        db.refresh(customer)
        return customer

    @classmethod
    def sync_order_from_wc_data(cls, db: Session, wc_data: Dict[str, Any]) -> Order:
        """Ingests WooCommerce order into CRM, binds to Customer, and triggers workflows."""
        wc_order_id = wc_data.get("id")
        if not wc_order_id:
            return None

        order = db.query(Order).filter(Order.wc_order_id == wc_order_id).first()
        is_new = order is None
        old_status = order.status if order else None

        if not order:
            order = Order(wc_order_id=wc_order_id)
            db.add(order)

        # Parse customer info
        billing = wc_data.get("billing", {})
        email = billing.get("email") or ""
        order.customer_email = email
        order.status = wc_data.get("status", "pending")
        order.currency = wc_data.get("currency", "USD")
        order.total = float(wc_data.get("total", 0.0) or 0.0)
        order.tax_total = float(wc_data.get("total_tax", 0.0) or 0.0)
        order.shipping_total = float(wc_data.get("shipping_total", 0.0) or 0.0)
        order.line_items = wc_data.get("line_items", [])
        order.billing = billing
        order.shipping = wc_data.get("shipping", {})
        order.payment_method = wc_data.get("payment_method_title") or wc_data.get("payment_method", "")
        order.customer_note = wc_data.get("customer_note", "")

        # Associate with customer
        customer = None
        if email:
            customer = db.query(Customer).filter(Customer.email == email).first()
            if not customer:
                # Create customer if doesn't exist yet
                customer = Customer(
                    email=email,
                    first_name=billing.get("first_name", ""),
                    last_name=billing.get("last_name", ""),
                    phone=billing.get("phone", ""),
                    billing_address=billing,
                    shipping_address=wc_data.get("shipping", {})
                )
                db.add(customer)
                db.flush()
            order.customer_id = customer.id

        # Parse creation date
        date_str = wc_data.get("date_created")
        if date_str:
            try:
                order.wc_created_at = datetime.fromisoformat(date_str)
            except Exception:
                pass

        db.commit()
        db.refresh(order)

        # Recalculate metrics for this customer
        if customer:
            cls.recalculate_customer_metrics(db, customer.id)

        # Trigger Workflows
        if is_new:
            cls.trigger_workflow(db, "order.created", order, customer)
            if order.status and order.status != "pending":
                cls.trigger_workflow(db, f"order.{order.status}", order, customer)
        elif old_status != order.status:
            cls.trigger_workflow(db, f"order.{order.status}", order, customer)

        return order

    @classmethod
    def recalculate_customer_metrics(cls, db: Session, customer_id: int):
        """Updates total spent, order counts, AOV, and tier for a customer."""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return

        orders = db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.status.in_(["completed", "processing", "pending"])
        ).all()

        total = sum(o.total for o in orders)
        count = len(orders)
        aov = round(total / count, 2) if count > 0 else 0.0
        
        last_order = db.query(Order).filter(Order.customer_id == customer_id).order_by(desc(Order.created_at)).first()
        if last_order:
            customer.last_order_date = last_order.created_at

        customer.total_spent = total
        customer.orders_count = count
        customer.avg_order_value = aov
        customer.tier = cls.calculate_customer_tier(total, count, customer.last_order_date)

        db.commit()

    @classmethod
    def recalculate_all_customer_metrics(cls, db: Session):
        customers = db.query(Customer).all()
        for c in customers:
            cls.recalculate_customer_metrics(db, c.id)

    @classmethod
    def trigger_workflow(cls, db: Session, event_name: str, order: Optional[Order], customer: Optional[Customer]):
        """Executes matched automated communication workflows based on events."""
        if not customer:
            return

        rules = db.query(WorkflowRule).filter(
            WorkflowRule.trigger_event == event_name,
            WorkflowRule.is_active == True
        ).all()

        for rule in rules:
            config = rule.action_config or {}
            subject = config.get("subject", f"Update regarding your order #{order.wc_order_id if order else ''}")
            body = config.get(
                "body",
                f"Hello {customer.first_name},\n\nWe have an update regarding your order #{order.wc_order_id if order else ''}. Status: {order.status if order else 'Updated'}."
            )
            # Personalize placeholders
            if order:
                body = body.replace("{first_name}", customer.first_name or "there")
                body = body.replace("{order_id}", str(order.wc_order_id))
                body = body.replace("{total}", f"${order.total:.2f}")

            log = CommunicationLog(
                customer_id=customer.id,
                channel="email",
                direction="outbound",
                subject=subject,
                content=body,
                status="sent",
                trigger_source=f"workflow:{rule.name}"
            )
            db.add(log)
            rule.execution_count += 1
            rule.last_triggered_at = datetime.utcnow()

        db.commit()

    @classmethod
    def get_crm_analytics(cls, db: Session) -> Dict[str, Any]:
        """Aggregate stats for dashboard KPIs."""
        total_customers = db.query(Customer).count()
        total_orders = db.query(Order).count()
        total_revenue = db.query(func.sum(Order.total)).filter(Order.status != "cancelled").scalar() or 0.0
        pending_orders = db.query(Order).filter(Order.status.in_(["pending", "processing", "on-hold"])).count()
        
        tier_counts = {
            "VIP": db.query(Customer).filter(Customer.tier == "VIP").count(),
            "Loyal": db.query(Customer).filter(Customer.tier == "Loyal").count(),
            "Regular": db.query(Customer).filter(Customer.tier == "Regular").count(),
            "New": db.query(Customer).filter(Customer.tier == "New").count(),
            "Lead": db.query(Customer).filter(Customer.tier == "Lead").count(),
        }

        recent_orders = db.query(Order).order_by(desc(Order.created_at)).limit(5).all()
        recent_comms = db.query(CommunicationLog).order_by(desc(CommunicationLog.created_at)).limit(5).all()

        return {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "pending_orders": pending_orders,
            "tier_distribution": tier_counts,
            "recent_orders_count": len(recent_orders),
            "recent_communications_count": len(recent_comms),
        }
