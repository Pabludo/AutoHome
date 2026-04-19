"""Action and event models."""

from datetime import datetime

from pydantic import BaseModel


class TriggeredAction(BaseModel):
    """An action that was triggered by the condition engine."""

    rule_name: str
    action: str
    property_id: str
    prospect_id: str
    priority: str = "medium"
    context: dict = {}


class ActionResult(BaseModel):
    """Result of executing an action."""

    action: str
    property_id: str
    status: str  # success, failed, skipped
    details: str = ""
    clientify_deal_id: int | None = None
    timestamp: datetime
