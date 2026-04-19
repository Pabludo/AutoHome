"""CRM reader agent for Inmovilla."""

from autohome.agents.base import BaseAgent
from autohome.connectors.inmovilla import InmovillaConnector
from autohome.models.prospect import Contact, Prospect


class CrmReaderAgent(BaseAgent):
    """Reads prospects from Inmovilla CRM."""

    def __init__(self):
        super().__init__("crm-reader")

    async def run(self) -> list[Prospect]:
        """Fetch all active prospects from Inmovilla."""
        self.log_start()
        prospects = []

        try:
            async with InmovillaConnector() as client:
                raw_prospects = await client.list_prospects(status="active")

                for raw in raw_prospects:
                    prospect = self._parse_prospect(raw)
                    if prospect and prospect.idealista_url:
                        prospects.append(prospect)
        except ValueError:
            self.logger.warning("Inmovilla not configured, skipping CRM read")
        except Exception as e:
            self.log_error(e)

        self.log_complete(len(prospects))
        return prospects

    def _parse_prospect(self, raw: dict) -> Prospect | None:
        """Parse raw API response into a Prospect model.

        NOTE: Field mappings need to be adjusted once real Inmovilla
        API response structure is confirmed.
        """
        try:
            return Prospect(
                prospect_id=str(raw.get("id", "")),
                client=Contact(
                    name=raw.get("name", ""),
                    email=raw.get("email"),
                    phone=raw.get("phone"),
                ),
                property_id=str(raw.get("property_id", "")),
                idealista_url=raw.get("idealista_url", raw.get("portal_url", "")),
            )
        except Exception:
            self.logger.warning("Could not parse prospect: %s", raw.get("id"))
            return None
