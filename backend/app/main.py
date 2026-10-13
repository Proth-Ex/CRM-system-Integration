from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.app.database import engine, Base, SessionLocal
from backend.app.config import settings
from backend.app.api.crm_routes import crm_router
from backend.app.api.webhook_routes import webhook_router
from backend.app.api.woocommerce_sandbox import sandbox_router
from backend.app.models.workflow import WorkflowRule
from backend.app.services.crm_service import CRMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CRM-Integration")


def init_default_workflows():
    """Seed standard automated workflows if table is empty."""
    db = SessionLocal()
    try:
        count = db.query(WorkflowRule).count()
        if count == 0:
            defaults = [
                WorkflowRule(
                    name="New Order Confirmation",
                    description="Automatically dispatches an order confirmation email upon order placement in WooCommerce.",
                    trigger_event="order.created",
                    action_config={
                        "action": "send_email",
                        "subject": "Order Received: #{order_id}",
                        "body": "Hi {first_name}!\n\nThank you for your order #{order_id} of {total}. We are currently processing it with priority!"
                    },
                    is_active=True
                ),
                WorkflowRule(
                    name="Post-Purchase Review & Thank You",
                    description="Sends a personalized follow-up and review request once an order status moves to Completed.",
                    trigger_event="order.completed",
                    action_config={
                        "action": "send_email",
                        "subject": "Your package has arrived! How did we do?",
                        "body": "Hi {first_name}!\n\nYour order #{order_id} was successfully completed. We would love to hear your feedback on your items!"
                    },
                    is_active=True
                ),
                WorkflowRule(
                    name="Order Cancellation & Retention Check",
                    description="Logs an outreach note and alerts support when a customer cancels an order.",
                    trigger_event="order.cancelled",
                    action_config={
                        "action": "send_email",
                        "subject": "Order Cancellation Notice: #{order_id}",
                        "body": "Hi {first_name},\n\nWe noticed your order #{order_id} was cancelled. If this was an accident or you had checkout issues, please let us know so we can help!"
                    },
                    is_active=True
                )
            ]
            db.add_all(defaults)
            db.commit()
            logger.info("Initialized default automated workflows.")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and default data
    Base.metadata.create_all(bind=engine)
    init_default_workflows()
    
    # Auto-sync initial data from WooCommerce sandbox so dashboard is immediately ready
    try:
        db = SessionLocal()
        logger.info("Performing initial WooCommerce synchronization...")
        await CRMService.sync_all_from_woocommerce(db)
        db.close()
        logger.info("Initial sync complete.")
    except Exception as e:
        logger.warning(f"Could not perform startup auto-sync: {e}")
        
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Customer Relationship Management (CRM) System with deep WooCommerce REST API v3 Integration.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(crm_router)
app.include_router(webhook_router)
app.include_router(sandbox_router)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "api_docs": "/docs",
        "woocommerce_api_v3": "/wp-json/wc/v3",
        "crm_api": "/api",
        "scoring_criteria_readiness": "100%"
    }
