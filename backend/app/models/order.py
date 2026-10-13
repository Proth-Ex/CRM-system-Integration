from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from backend.app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    wc_order_id = Column(Integer, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    
    customer_email = Column(String(255), index=True, nullable=False)
    status = Column(String(50), index=True, default="pending")  # pending, processing, on-hold, completed, cancelled, refunded
    currency = Column(String(10), default="USD")
    total = Column(Float, default=0.0)
    tax_total = Column(Float, default=0.0)
    shipping_total = Column(Float, default=0.0)
    
    # Order items list: [{id, name, product_id, quantity, price, subtotal}]
    line_items = Column(JSON, default=list)
    
    # Billing & Shipping snapshot
    billing = Column(JSON, default=dict)
    shipping = Column(JSON, default=dict)
    
    payment_method = Column(String(100), default="Direct Bank Transfer")
    customer_note = Column(Text, default="")
    internal_notes = Column(Text, default="")
    
    wc_created_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")


# Pydantic Schemas
class OrderLineItem(BaseModel):
    id: Optional[int] = None
    name: str
    product_id: Optional[int] = None
    quantity: int = 1
    price: float = 0.0
    subtotal: float = 0.0


class OrderBase(BaseModel):
    wc_order_id: int
    customer_email: str
    status: str = "pending"
    currency: str = "USD"
    total: float = 0.0
    tax_total: float = 0.0
    shipping_total: float = 0.0
    line_items: List[dict] = []
    billing: Optional[dict] = {}
    shipping: Optional[dict] = {}
    payment_method: Optional[str] = "card"
    customer_note: Optional[str] = ""
    internal_notes: Optional[str] = ""


class OrderUpdateStatus(BaseModel):
    status: str
    internal_notes: Optional[str] = None


class OrderResponse(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: Optional[int] = None
    wc_created_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
