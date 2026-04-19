"""Condition engine agent - evaluates rules against metrics."""

import operator as op
from pathlib import Path

import yaml

from autohome.agents.base import BaseAgent
from autohome.models.action import TriggeredAction
from autohome.models.property import PropertySnapshot
from autohome.models.rule import Rule, ThresholdCondition

OPERATORS = {
    ">=": op.ge,
    "<=": op.le,
    ">": op.gt,
    "<": op.lt,
    "==": op.eq,
    "!=": op.ne,
}


class ConditionEngineAgent(BaseAgent):
    """Evaluates property metrics against configurable rules."""

    def __init__(self, rules_path: str = "rules/example_rules.yaml"):
        super().__init__("condition-engine")
        self._rules_path = Path(rules_path)
        self._rules: list[Rule] = []

    def load_rules(self):
        """Load rules from YAML file."""
        if not self._rules_path.exists():
            self.logger.warning("Rules file not found: %s", self._rules_path)
            return

        with open(self._rules_path) as f:
            data = yaml.safe_load(f)

        self._rules = []
        for rule_data in data.get("rules", []):
            conditions = []
            for cond in rule_data.get("conditions", []):
                if "operator" in cond:
                    conditions.append(ThresholdCondition(**cond))
            self._rules.append(
                Rule(
                    name=rule_data["name"],
                    description=rule_data.get("description", ""),
                    rule_type=rule_data.get("type", "threshold"),
                    conditions=conditions,
                    action=rule_data["action"],
                    priority=rule_data.get("priority", "medium"),
                    cooldown_hours=rule_data.get("cooldown_hours", 24),
                    enabled=rule_data.get("enabled", True),
                )
            )
        self.logger.info("Loaded %d rules from %s", len(self._rules), self._rules_path)

    async def run(
        self,
        snapshots: list[PropertySnapshot],
        prospect_map: dict[str, str] | None = None,
    ) -> list[TriggeredAction]:
        """Evaluate all rules against provided snapshots."""
        self.log_start()
        self.load_rules()

        triggered = []
        prospect_map = prospect_map or {}

        for snapshot in snapshots:
            for rule in self._rules:
                if not rule.enabled:
                    continue
                if self._evaluate_rule(rule, snapshot):
                    action = TriggeredAction(
                        rule_name=rule.name,
                        action=rule.action,
                        property_id=snapshot.property_id,
                        prospect_id=prospect_map.get(snapshot.property_id, ""),
                        priority=rule.priority,
                        context={
                            "visits": snapshot.metrics.visits,
                            "email_contacts": snapshot.metrics.email_contacts,
                            "favorites": snapshot.metrics.favorites,
                        },
                    )
                    triggered.append(action)
                    self.logger.info(
                        "Rule '%s' triggered for property %s",
                        rule.name,
                        snapshot.property_id,
                    )

        self.log_complete(len(triggered))
        return triggered

    def _evaluate_rule(self, rule: Rule, snapshot: PropertySnapshot) -> bool:
        """Evaluate a single rule against a snapshot."""
        results = []

        for condition in rule.conditions:
            if isinstance(condition, ThresholdCondition):
                actual = getattr(snapshot.metrics, condition.metric, None)
                if actual is None:
                    results.append(False)
                    continue
                op_func = OPERATORS.get(condition.operator)
                if op_func:
                    results.append(op_func(actual, condition.value))
                else:
                    results.append(False)

        if not results:
            return False

        if rule.operator == "AND":
            return all(results)
        return any(results)  # OR
