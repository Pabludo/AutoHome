"""Idealista property statistics scraper using Playwright."""

import random
import re
from datetime import UTC, datetime

from playwright.async_api import async_playwright

from autohome.config import get_settings


class IdealistaConnector:
    """Scrapes property statistics from Idealista using Playwright."""

    def __init__(self):
        settings = get_settings()
        self._email = settings.idealista_email
        self._password = settings.idealista_password
        self._delay_min = settings.scraper_delay_min_seconds
        self._delay_max = settings.scraper_delay_max_seconds
        self._playwright = None
        self._browser = None
        self._context = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        return self

    async def __aexit__(self, *args):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def _random_delay(self):
        """Wait a random time to mimic human behavior."""
        import asyncio

        delay = random.uniform(self._delay_min, self._delay_max)  # noqa: S311
        await asyncio.sleep(delay)

    async def login(self) -> bool:
        """Authenticate on Idealista."""
        page = await self._context.new_page()
        try:
            await page.goto("https://www.idealista.com/login", wait_until="networkidle")
            await self._random_delay()

            # Fill login form — selectors may need updating
            await page.fill('input[name="email"]', self._email)
            await page.fill('input[name="password"]', self._password)
            await self._random_delay()
            await page.click('button[type="submit"]')
            await page.wait_for_load_state("networkidle")

            # Check if login succeeded
            is_logged = await page.query_selector('[class*="user-menu"]') is not None
            return is_logged
        finally:
            await page.close()

    async def scrape_property_stats(self, url: str) -> dict:
        """Scrape statistics for a single property listing.

        Args:
            url: Idealista property URL (e.g. https://www.idealista.com/inmueble/111029821/)

        Returns:
            Dictionary with property_id, timestamp, and metrics.
        """
        # Extract property ID from URL
        match = re.search(r"/inmueble/(\d+)", url)
        property_id = match.group(1) if match else "unknown"

        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            await self._random_delay()

            metrics = {
                "visits": await self._extract_number(page, "visitas"),
                "email_contacts": await self._extract_number(page, "contactos por email"),
                "favorites": await self._extract_number(page, "guardado como favorito"),
                "phone_contacts": await self._extract_number(page, "contactos telefónicos"),
            }

            # Try to get last updated date
            last_updated = await self._extract_date(page)

            return {
                "property_id": property_id,
                "url": url,
                "timestamp": datetime.now(UTC).isoformat(),
                "metrics": metrics,
                "last_updated": last_updated,
            }
        finally:
            await page.close()

    async def _extract_number(self, page, label: str) -> int | None:
        """Extract a numeric metric by its associated label text.

        This uses the statistics panel structure visible in the Idealista UI.
        The pattern is: <strong>NUMBER</strong> followed by label text.
        """
        try:
            # Strategy 1: Look for text content near the label
            locator = page.locator(f"text=/{label}/i").first
            parent = locator.locator("..")
            number_el = parent.locator("strong").first
            text = await number_el.text_content()
            if text:
                return int(text.strip().replace(".", "").replace(",", ""))
        except Exception:  # noqa: S110
            pass

        try:
            # Strategy 2: XPath based approach
            elements = await page.query_selector_all("strong")
            for el in elements:
                sibling_text = await el.evaluate(
                    "(node) => node.parentElement?.textContent || ''"
                )
                if label.lower() in sibling_text.lower():
                    text = await el.text_content()
                    if text:
                        clean = re.sub(r"[^\d]", "", text.strip())
                        return int(clean) if clean else None
        except Exception:  # noqa: S110
            pass

        return None

    async def _extract_date(self, page) -> str | None:
        """Extract the 'last updated' date from the statistics panel."""
        try:
            locator = page.locator("text=/actualizado/i").first
            text = await locator.text_content()
            if text:
                return text.strip()
        except Exception:  # noqa: S110
            pass
        return None
