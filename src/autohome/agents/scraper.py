"""Idealista scraper agent."""

from autohome.agents.base import BaseAgent
from autohome.connectors.idealista import IdealistaConnector
from autohome.models.property import PropertySnapshot


class ScraperAgent(BaseAgent):
    """Scrapes property statistics from Idealista for a list of URLs."""

    def __init__(self):
        super().__init__("scraper")

    async def run(self, urls: list[str]) -> list[PropertySnapshot]:
        """Scrape metrics for a list of Idealista property URLs."""
        self.log_start()
        results = []

        async with IdealistaConnector() as scraper:
            # Login first
            logged_in = await scraper.login()
            if not logged_in:
                self.logger.warning("Could not authenticate on Idealista, trying without login")

            for url in urls:
                try:
                    raw = await scraper.scrape_property_stats(url)
                    snapshot = PropertySnapshot(**raw)
                    results.append(snapshot)
                    self.logger.info("Scraped %s: %s", url, raw.get("metrics"))
                except Exception as e:
                    self.log_error(e)

        self.log_complete(len(results))
        return results
