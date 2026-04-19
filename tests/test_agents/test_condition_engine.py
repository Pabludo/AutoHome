"""Tests for the condition engine."""

from autohome.agents.condition_engine import ConditionEngineAgent
from autohome.models.property import PropertyMetrics, PropertySnapshot


async def test_high_interest_rule_triggers(tmp_path):
    """Test that high_interest rule triggers for high-traffic property."""
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text("""
rules:
  - name: high_interest
    type: threshold
    conditions:
      - metric: visits
        operator: ">="
        value: 1000
      - metric: email_contacts
        operator: ">="
        value: 10
    operator: AND
    action: notify_high_interest
    priority: high
    enabled: true
""")

    engine = ConditionEngineAgent(rules_path=str(rules_yaml))
    snapshot = PropertySnapshot(
        property_id="111029821",
        url="https://www.idealista.com/inmueble/111029821/",
        timestamp="2026-04-19T14:00:00Z",
        metrics=PropertyMetrics(visits=1619, email_contacts=11, favorites=88),
    )

    triggered = await engine.run([snapshot])
    assert len(triggered) == 1
    assert triggered[0].action == "notify_high_interest"
    assert triggered[0].property_id == "111029821"


async def test_low_visits_does_not_trigger_high_interest(tmp_path):
    """Test that low visits don't trigger high interest rule."""
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text("""
rules:
  - name: high_interest
    type: threshold
    conditions:
      - metric: visits
        operator: ">="
        value: 1000
    action: notify_high_interest
    enabled: true
""")

    engine = ConditionEngineAgent(rules_path=str(rules_yaml))
    snapshot = PropertySnapshot(
        property_id="999",
        url="https://www.idealista.com/inmueble/999/",
        timestamp="2026-04-19T14:00:00Z",
        metrics=PropertyMetrics(visits=50, email_contacts=1, favorites=3),
    )

    triggered = await engine.run([snapshot])
    assert len(triggered) == 0
