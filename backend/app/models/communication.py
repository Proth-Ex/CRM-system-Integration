from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from backend.app.database import Base


class CommunicationLog(Base):
    __tablename__ = "communication_logs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    channel = Column(String(50), default="email")  # email, sms, phone, ticket, system_notification
    direction = Column(String(20), default="outbound")  # outbound, inbound
    subject = Column(String(255), default="")
    content = Column(Text, nullable=False)
    status = Column(String(50), default="sent")  # sent, delivered, failed, scheduled
    
    # Workflow trigger context (e.g., 'workflow:order_completed_followup', 'manual', 'support_ticket')
    trigger_source = Column(String(100), default="manual")
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="communications")


# Pydantic Schemas
class CommunicationCreate(BaseModel):
    customer_id: int
    channel: Optional[str] = "email"
    direction: Optional[str] = "outbound"
    subject: Optional[str] = ""
    content: str
    status: Optional[str] = "sent"
    trigger_source: Optional[str] = "manual"


class CommunicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    channel: str
    direction: str
    subject: str
    content: str
    status: str
    trigger_source: str
    created_at: datetime
