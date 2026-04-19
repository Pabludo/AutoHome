"""Idealista scraper agent.

Flow:
1. Receive list of (cod_ofer, idealista_url) pairs.
2. Login to Idealista once.
3. For each URL, scrape the 'Estadísticas' card.
4. Return list of PropertySnapshot.
"""

from autohome.agents.base import BaseAgent
from autohome.connectors.idealista import IdealistaConnector
from autohome.models.property import PropertyMetrics, PropertySnapshot


class ScraperAgent(BaseAgent):
    """Scrapes property statistics from Idealista."""

    def __init__(self):
        super().__init__("scraper")

    async def run(
        self, targets: list[tuple[str, str]],
    ) -> list[PropertySnapshot]:
        """Scrape metrics for a list of (cod_ofer, idealista_url) pairs."""
        self.log_start()
        results: list[PropertySnapshot] = []

        async with IdealistaConnector() as scraper:
            logged_in = await scraper.login()
            if not logged_in:
                self.logger.warning(
                    "Idealista login may have failed, trying anyway",
                )

            for cod_ofer, url in targets:
                try:
                    raw = await scraper.scrape_property_stats(url)
                    snapshot = PropertySnapshot(
                        property_id=cod_ofer,
                        url=raw["url"],
                        timestamp=raw["timestamp"],
                        metrics=PropertyMetrics(**raw["metrics"]),
                        last_updated=raw.get("last_updated"),
                    )
                    results.append(snapshot)
                    self.logger.info(
                        "Scraped %s (%s): %s",
                        cod_ofer,
                        url,
                        raw["metrics"],
                    )
                except Exception as e:
                    self.log_error(e)

        self.log_complete(len(results))
        return results
