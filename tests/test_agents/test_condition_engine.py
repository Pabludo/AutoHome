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
        value: 200
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
        property_id="28751504",
        url="https://www.idealista.com/inmueble/111051259/",
        timestamp="2026-04-19T14:00:00Z",
        metrics=PropertyMetrics(visits=303, email_contacts=15, favorites=32),
    )

    triggered = await engine.run([snapshot])
    assert len(triggered) == 1
    assert triggered[0].action == "notify_high_interest"
    assert triggered[0].property_id == "28751504"


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
        value: 200
    action: notify_high_interest
    enabled: true
""")

    engine = ConditionEngineAgent(rules_path=str(rules_yaml))
    snapshot = PropertySnapshot(
        property_id="99999",
        url="https://www.idealista.com/inmueble/99999/",
        timestamp="2026-04-19T14:00:00Z",
        metrics=PropertyMetrics(visits=50, email_contacts=1, favorites=3),
    )

    triggered = await engine.run([snapshot])
    assert len(triggered) == 0
