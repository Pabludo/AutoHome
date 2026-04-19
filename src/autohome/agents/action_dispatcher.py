"""Action dispatcher agent - executes actions on Clientify."""

from datetime import UTC, datetime

from autohome.agents.base import BaseAgent
from autohome.connectors.clientify import ClientifyConnector
from autohome.models.action import ActionResult, TriggeredAction


class ActionDispatcherAgent(BaseAgent):
    """Dispatches triggered actions to Clientify."""

    def __init__(self):
        super().__init__("action-dispatcher")

    async def run(self, actions: list[TriggeredAction]) -> list[ActionResult]:
        """Execute all triggered actions."""
        self.log_start()
        results = []

        async with ClientifyConnector() as clientify:
            for action in actions:
                result = await self._execute_action(clientify, action)
                results.append(result)

        self.log_complete(len(results))
        return results

    async def _execute_action(
        self, clientify: ClientifyConnector, action: TriggeredAction
    ) -> ActionResult:
        """Execute a single action."""
        try:
            handler = self._get_handler(action.action)
            if handler:
                return await handler(clientify, action)
            return ActionResult(
                action=action.action,
                property_id=action.property_id,
                status="skipped",
                details=f"No handler for action: {action.action}",
                timestamp=datetime.now(UTC),
            )
        except Exception as e:
            self.log_error(e)
            return ActionResult(
                action=action.action,
                property_id=action.property_id,
                status="failed",
                details=str(e),
                timestamp=datetime.now(UTC),
            )

    def _get_handler(self, action_name: str):
        """Map action names to handler methods."""
        handlers = {
            "notify_high_interest": self._handle_high_interest,
            "suggest_price_reduction": self._handle_price_reduction,
            "recommend_reactivation": self._handle_reactivation,
        }
        return handlers.get(action_name)

    async def _handle_high_interest(
        self, clientify: ClientifyConnector, action: TriggeredAction
    ) -> ActionResult:
        """Handle high interest notification — create/update deal with high priority."""
        # Find or create contact
        # Create deal with metrics context
        deal_data = {
            "name": f"High Interest - Property {action.property_id}",
            "custom_fields": {
                "property_id": action.property_id,
                "idealista_visits": action.context.get("visits"),
                "idealista_contacts": action.context.get("email_contacts"),
                "trigger_rule": action.rule_name,
            },
        }
        deal = await clientify.create_deal(deal_data)

        return ActionResult(
            action=action.action,
            property_id=action.property_id,
            status="success",
            details=f"Deal created: {deal.get('id')}",
            clientify_deal_id=deal.get("id"),
            timestamp=datetime.now(UTC),
        )

    async def _handle_price_reduction(
        self, clientify: ClientifyConnector, action: TriggeredAction
    ) -> ActionResult:
        """Handle price reduction suggestion."""
        # TODO: Implement price reduction logic
        return ActionResult(
            action=action.action,
            property_id=action.property_id,
            status="skipped",
            details="Price reduction handler not yet implemented",
            timestamp=datetime.now(UTC),
        )

    async def _handle_reactivation(
        self, clientify: ClientifyConnector, action: TriggeredAction
    ) -> ActionResult:
        """Handle reactivation recommendation."""
        # TODO: Implement reactivation logic
        return ActionResult(
            action=action.action,
            property_id=action.property_id,
            status="skipped",
            details="Reactivation handler not yet implemented",
            timestamp=datetime.now(UTC),
        )
