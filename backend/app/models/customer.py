from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from backend.app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    wc_id = Column(Integer, unique=True, index=True, nullable=True)  # WooCommerce Customer ID
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), default="")
    last_name = Column(String(100), default="")
    phone = Column(String(50), default="")
    
    # Financial & RFM Metrics
    total_spent = Column(Float, default=0.0)
    orders_count = Column(Integer, default=0)
    avg_order_value = Column(Float, default=0.0)
    tier = Column(String(50), default="New")  # New, Regular, VIP, At-Risk, Inactive
    
    # Address details (JSON)
    billing_address = Column(JSON, default=dict)
    shipping_address = Column(JSON, default=dict)
    
    # CRM metadata
    notes = Column(Text, default="")
    tags = Column(JSON, default=list)  # e.g., ["Tech Enthusiast", "High Spender"]
    status = Column(String(50), default="active")  # active, lead, dormant
    
    last_order_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    communications = relationship("CommunicationLog", back_populates="customer", cascade="all, delete-orphan")


# Pydantic Schemas
class CustomerBase(BaseModel):
    email: str
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    phone: Optional[str] = ""
    billing_address: Optional[dict] = {}
    shipping_address: Optional[dict] = {}
    notes: Optional[str] = ""
    tags: Optional[List[str]] = []
    status: Optional[str] = "active"


class CustomerCreate(CustomerBase):
    wc_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wc_id: Optional[int] = None
    total_spent: float
    orders_count: int
    avg_order_value: float
    tier: str
    last_order_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
