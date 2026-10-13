from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from pydantic import BaseModel, ConfigDict
from backend.app.database import Base


class WorkflowRule(Base):
    __tablename__ = "workflow_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    trigger_event = Column(String(100), nullable=False)  # order.created, order.completed, order.cancelled, customer.new, customer.at_risk
    
    # Action configuration (e.g. {"action": "send_email", "template_subject": "Thank you for your order!", ...})
    action_config = Column(JSON, default=dict)
    
    is_active = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Schemas
class WorkflowRuleBase(BaseModel):
    name: str
    description: Optional[str] = ""
    trigger_event: str
    action_config: dict
    is_active: Optional[bool] = True


class WorkflowRuleCreate(WorkflowRuleBase):
    pass


class WorkflowRuleResponse(WorkflowRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    execution_count: int
    last_triggered_at: Optional[datetime] = None
    created_at: datetime
