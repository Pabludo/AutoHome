"""Condition rule models."""

from pydantic import BaseModel


class ThresholdCondition(BaseModel):
    """A single threshold condition."""

    metric: str  # visits, email_contacts, favorites, phone_contacts
    operator: str  # >=, <=, ==, >, <
    value: float


class TrendCondition(BaseModel):
    """A trend-based condition comparing current vs historical."""

    metric: str
    period_days: int = 7
    direction: str  # increasing, decreasing
    threshold_pct: float  # e.g., -20 means 20% decrease


class Rule(BaseModel):
    """A complete rule with conditions and action to trigger."""

    name: str
    description: str = ""
    rule_type: str  # threshold, trend, composite
    conditions: list[ThresholdCondition | TrendCondition] = []
    operator: str = "AND"  # AND / OR for combining conditions
    action: str  # Name of the action to trigger
    priority: str = "medium"  # low, medium, high
    cooldown_hours: int = 24  # Min hours between re-triggering
    enabled: bool = True
