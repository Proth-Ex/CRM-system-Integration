from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional, Dict, Any

from backend.app.database import get_db
from backend.app.models.customer import Customer, CustomerResponse, CustomerUpdate
from backend.app.models.order import Order, OrderResponse, OrderUpdateStatus
from backend.app.models.communication import CommunicationLog, CommunicationResponse, CommunicationCreate
from backend.app.models.workflow import WorkflowRule, WorkflowRuleResponse, WorkflowRuleCreate
from backend.app.services.crm_service import CRMService
from backend.app.services.woocommerce_client import woo_client

crm_router = APIRouter(prefix="/api", tags=["CRM Management API"])


# --- Analytics & Dashboard KPIs ---
@crm_router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """Return key CRM KPIs, customer tiers distribution, and revenue summary."""
    return CRMService.get_crm_analytics(db)


# --- WooCommerce Bidirectional Sync ---
@crm_router.post("/sync")
async def sync_woocommerce(db: Session = Depends(get_db)):
    """Fetch latest customer profiles and orders from WooCommerce into CRM."""
    try:
        result = await CRMService.sync_all_from_woocommerce(db)
        return {
            "status": "success",
            "message": "WooCommerce data synchronized successfully.",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sync error: {str(e)}. Check WooCommerce connection and credentials."
        )


# --- Customers Management ---
@crm_router.get("/customers", response_model=List[CustomerResponse])
def get_customers(
    search: Optional[str] = None,
    tier: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                Customer.email.ilike(search_fmt),
                Customer.first_name.ilike(search_fmt),
                Customer.last_name.ilike(search_fmt)
            )
        )
    if tier:
        query = query.filter(Customer.tier == tier)
    
    return query.order_by(desc(Customer.total_spent)).offset(skip).limit(limit).all()


@crm_router.get("/customers/{customer_id}")
def get_customer_details(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(desc(Order.created_at)).all()
    communications = db.query(CommunicationLog).filter(CommunicationLog.customer_id == customer_id).order_by(desc(CommunicationLog.created_at)).all()

    return {
        "customer": CustomerResponse.model_validate(customer),
        "orders": [OrderResponse.model_validate(o) for o in orders],
        "communications": [CommunicationResponse.model_validate(c) for c in communications]
    }


@crm_router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if payload.first_name is not None:
        customer.first_name = payload.first_name
    if payload.last_name is not None:
        customer.last_name = payload.last_name
    if payload.phone is not None:
        customer.phone = payload.phone
    if payload.notes is not None:
        customer.notes = payload.notes
    if payload.tags is not None:
        customer.tags = payload.tags
    if payload.status is not None:
        customer.status = payload.status

    db.commit()
    db.refresh(customer)
    return customer


# --- Communication Logs ---
@crm_router.get("/communications", response_model=List[CommunicationResponse])
def get_all_communications(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    return db.query(CommunicationLog).order_by(desc(CommunicationLog.created_at)).limit(limit).all()


@crm_router.post("/customers/{customer_id}/communications", response_model=CommunicationResponse)
def log_communication(
    customer_id: int,
    payload: CommunicationCreate,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    log = CommunicationLog(
        customer_id=customer_id,
        channel=payload.channel,
        direction=payload.direction,
        subject=payload.subject,
        content=payload.content,
        status=payload.status,
        trigger_source=payload.trigger_source
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# --- Order Tracking ---
@crm_router.get("/orders", response_model=List[OrderResponse])
def get_orders(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Order)
    if status and status != "all":
        query = query.filter(Order.status == status)
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    return query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()


@crm_router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@crm_router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    payload: OrderUpdateStatus,
    sync_to_wc: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Updates order status in CRM and pushes change back to WooCommerce."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = payload.status
    if payload.internal_notes:
        order.internal_notes = payload.internal_notes
    
    db.commit()
    db.refresh(order)

    # Sync to WooCommerce if requested
    wc_synced = False
    if sync_to_wc and order.wc_order_id:
        try:
            await woo_client.update_order_status(order.wc_order_id, payload.status)
            wc_synced = True
        except Exception as e:
            # We don't fail the CRM update if WC is unreachable, but record warning
            pass

    # Trigger workflow on status change
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first() if order.customer_id else None
    if old_status != payload.status:
        CRMService.trigger_workflow(db, f"order.{payload.status}", order, customer)
        if customer:
            CRMService.recalculate_customer_metrics(db, customer.id)

    return {
        "status": "success",
        "order": OrderResponse.model_validate(order),
        "synced_to_woocommerce": wc_synced
    }


# --- Automated Communication Workflows ---
@crm_router.get("/workflows", response_model=List[WorkflowRuleResponse])
def get_workflows(db: Session = Depends(get_db)):
    return db.query(WorkflowRule).order_by(WorkflowRule.id).all()


@crm_router.post("/workflows", response_model=WorkflowRuleResponse)
def create_workflow(payload: WorkflowRuleCreate, db: Session = Depends(get_db)):
    rule = WorkflowRule(
        name=payload.name,
        description=payload.description,
        trigger_event=payload.trigger_event,
        action_config=payload.action_config,
        is_active=payload.is_active
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


# --- AI Agent & LLM Deployment Endpoints ---
from backend.app.services.ai_agent_service import AIAgentService


@crm_router.get("/ai/incentive-policies")
def get_incentive_policies():
    """
    Returns available merchant-controlled retention incentive categories:
    (Free Delivery, 6-Month Warranty, Complimentary Gift, Capped 5% Coupon, VIP Concierge).
    Prevents arbitrary large discount giveaways.
    """
    return AIAgentService.get_incentive_policies()


@crm_router.post("/ai/draft-communication")
def ai_draft_communication(
    customer_id: int,
    intent: str = Query("festive_loyalty_offer"),
    channel: str = Query("email"),
    incentive_type: str = Query("auto"),
    db: Session = Depends(get_db)
):
    """
    [LLM Deployment Point 1]: Generates hyper-personalized outreach
    using customer LTV, location, and past order profile, autonomously selecting
    the best margin-safe incentive.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return AIAgentService.draft_personalized_communication(
        customer,
        channel=channel,
        intent=intent,
        incentive_type=incentive_type
    )


@crm_router.get("/ai/churn-risk/{customer_id}")
def ai_churn_risk(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    [LLM Deployment Point 2]: Predictive Churn Risk & Health Scoring Agent.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return AIAgentService.evaluate_churn_risk_score(customer, orders)


@crm_router.get("/ai/slipping-customers")
def get_slipping_customers(
    db: Session = Depends(get_db)
):
    """
    Detects which customers are about to slip/churn based on behavior,
    order cadence, and status bottlenecks.
    """
    customers = db.query(Customer).all()
    orders = db.query(Order).all()
    return AIAgentService.get_slipping_customers(customers, orders)


@crm_router.post("/ai/retention-strategy/{customer_id}")
def generate_retention_strategy(
    customer_id: int,
    incentive_type: str = Query("auto"),
    db: Session = Depends(get_db)
):
    """
    Calls Live Google Gemini to diagnose why the customer is slipping
    and autonomously selects the most appropriate margin-safe incentive
    (Free Delivery, Warranty, Gift, Capped 5%, or VIP Concierge) based on context.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return AIAgentService.generate_retention_strategy(
        customer,
        orders,
        incentive_type=incentive_type
    )


# --- 1. Automated Support & Helpdesk Ticket Resolution ---
@crm_router.post("/ai/helpdesk-triage")
def ai_helpdesk_triage(
    customer_id: int,
    subject: str = Query(...),
    message: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    [Feature 1: Helpdesk Resolution]:
    - Context-Aware Ticket Deflection
    - Sentiment & Urgency Triage
    - Ticket Summarization (2-sentence brief)
    - One-Click Agent Co-pilot Reply
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return AIAgentService.process_helpdesk_ticket(subject, message, customer, orders)


# --- 4. Natural Language CRM Database Query ---
@crm_router.post("/ai/nl-query")
def ai_nl_query(
    query: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    [Feature 4: Natural Language Database Search]:
    Translates English questions (e.g. 'Show VIP customers in Bengaluru')
    into CRM filters and returns matching data.
    """
    customers = db.query(Customer).all()
    orders = db.query(Order).all()
    return AIAgentService.natural_language_crm_query(query, customers, orders)


@crm_router.post("/ai/triage-note")
def ai_triage_note(
    note: str = Query(...)
):
    """
    [LLM Deployment Point 3]: Autonomous Webhook Note Triage & NLP Tagging.
    """
    return AIAgentService.triage_incoming_order_note(note)

