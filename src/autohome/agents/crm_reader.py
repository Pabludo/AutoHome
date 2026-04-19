"""CRM reader agent for Inmovilla.

Reads properties marked as prospecto, resolves their Idealista URLs,
and builds Prospect objects with owner information.
"""

from autohome.agents.base import BaseAgent
from autohome.connectors.inmovilla import InmovillaConnector
from autohome.models.prospect import Owner, Prospect


class CrmReaderAgent(BaseAgent):
    """Reads prospects from Inmovilla CRM."""

    def __init__(self):
        super().__init__("crm-reader")

    async def run(self) -> list[Prospect]:
        """Fetch active prospects that have an Idealista listing."""
        self.log_start()
        prospects: list[Prospect] = []

        try:
            async with InmovillaConnector() as client:
                all_props = await client.list_properties()

                # Filter: prospecto=True and available
                active = [
                    p for p in all_props
                    if p.get("prospecto") and not p.get("nodisponible")
                ]
                self.logger.info(
                    "Found %d active prospects out of %d total",
                    len(active),
                    len(all_props),
                )

                for prop in active:
                    try:
                        prospect = await self._build_prospect(
                            client, prop,
                        )
                        if prospect:
                            prospects.append(prospect)
                    except Exception as e:
                        self.logger.warning(
                            "Skip %s: %s", prop.get("cod_ofer"), e,
                        )

        except ValueError:
            self.logger.warning(
                "Inmovilla not configured, skipping CRM read",
            )
        except Exception as e:
            self.log_error(e)

        self.log_complete(len(prospects))
        return prospects

    async def _build_prospect(
        self, client: InmovillaConnector, prop: dict,
    ) -> Prospect | None:
        """Resolve Idealista URL and owner for a single property."""
        cod_ofer = str(prop["cod_ofer"])

        idealista_url = await client.get_idealista_url(cod_ofer)
        if not idealista_url:
            return None

        owner_data = await client.get_owner_by_property(cod_ofer)
        owner = Owner(
            cod_cli=owner_data.get("cod_cli", 0),
            nombre=owner_data.get("nombre", ""),
            apellidos=owner_data.get("apellidos", ""),
            email=owner_data.get("email", ""),
            telefono1=owner_data.get("telefono1", ""),
            telefono2=owner_data.get("telefono2", ""),
        )

        return Prospect(
            cod_ofer=int(cod_ofer),
            ref=prop.get("ref", ""),
            owner=owner,
            idealista_url=idealista_url,
            prospecto=True,
        )
