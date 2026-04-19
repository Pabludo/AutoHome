"""Idealista property statistics scraper using Playwright.

Stats are inside a lazy-loaded section:
  <div id="stats">
    <div id="stats-ondemand">
      <p>Anuncio actualizado el ...</p>
      <ul>
        <li><strong>303</strong><span>visitas</span></li>
        <li><strong>15</strong><span>contactos por email</span></li>
        <li><strong>32</strong><span>veces guardado como favorito</span></li>
      </ul>
    </div>
  </div>

The section only renders once scrolled into the viewport.
"""

import asyncio
import contextlib
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
        self._logged_in = False

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
        delay = random.uniform(self._delay_min, self._delay_max)  # noqa: S311
        await asyncio.sleep(delay)

    async def login(self) -> bool:
        """Authenticate on Idealista (2-step flow: email → password)."""
        page = await self._context.new_page()
        try:
            await page.goto(
                "https://www.idealista.com/login",
                wait_until="domcontentloaded",
            )
            await self._random_delay()

            # Accept cookies if present
            try:
                accept = page.locator("#didomi-notice-agree-button")
                if await accept.is_visible(timeout=5000):
                    await accept.click()
                    await self._random_delay()
            except Exception:  # noqa: S110
                pass

            # Step 1: Fill email and click Continuar
            email_sel = (
                'input[name="email"], input[type="email"], '
                '#email, input[id*="email"]'
            )
            await page.wait_for_selector(email_sel, timeout=10000)
            await page.fill(email_sel, self._email)
            await self._random_delay()
            await page.click('button:has-text("Continuar")')

            # Step 2: Wait for password field to appear
            await page.wait_for_selector(
                'input[type="password"]', timeout=10000,
            )
            await self._random_delay()
            await page.fill('input[type="password"]', self._password)
            await self._random_delay()

            # Click "Iniciar sesión"
            await page.click('button:has-text("Iniciar sesión")')
            await page.wait_for_load_state("domcontentloaded")
            await self._random_delay()

            # Check if login succeeded (redirected away from /login)
            self._logged_in = "/login" not in page.url
            return self._logged_in
        finally:
            await page.close()

    async def scrape_property_stats(self, url: str) -> dict:
        """Scrape the "Estadísticas" card for a single property listing.

        The stats section is lazy-loaded: we must scroll ``div#stats``
        into the viewport and wait for ``div#stats-ondemand`` children.

        Returns:
            Dictionary with property_id, url, timestamp, metrics and
            last_updated text.
        """
        match = re.search(r"/inmueble/(\d+)", url)
        property_id = match.group(1) if match else "unknown"

        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            await self._random_delay()

            # Scroll stats section into view to trigger lazy load
            stats_div = await page.query_selector("div#stats")
            if stats_div:
                await stats_div.scroll_into_view_if_needed()
                await asyncio.sleep(3)

            # Wait for the on-demand content to appear
            with contextlib.suppress(Exception):
                await page.wait_for_selector(
                    "div#stats-ondemand li", timeout=10000,
                )

            metrics = await self._parse_stats_ondemand(page)
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

    async def _parse_stats_ondemand(self, page) -> dict:
        """Parse ``div#stats-ondemand ul li`` items.

        Each ``<li>`` contains ``<strong>NUMBER</strong>``
        and ``<span>label</span>``.
        """
        result: dict[str, int | None] = {
            "visits": None,
            "email_contacts": None,
            "favorites": None,
            "phone_contacts": None,
        }

        label_map = {
            "visitas": "visits",
            "contactos por email": "email_contacts",
            "guardado como favorito": "favorites",
            "contactos telefónicos": "phone_contacts",
        }

        stats_od = await page.query_selector("div#stats-ondemand")
        if not stats_od:
            return result

        items = await stats_od.query_selector_all("li")
        for item in items:
            strong = await item.query_selector("strong")
            if not strong:
                continue
            num_text = (await strong.text_content() or "").strip()
            label_text = (await item.text_content() or "").strip()
            # label_text = "303visitas"  → remove the number prefix
            label_text = label_text.removeprefix(num_text).strip()

            for pattern, key in label_map.items():
                if pattern in label_text.lower():
                    clean = re.sub(r"[^\d]", "", num_text)
                    result[key] = int(clean) if clean else None
                    break

        return result

    async def _extract_date(self, page) -> str | None:
        """Extract the 'Anuncio actualizado el ...' text."""
        stats_od = await page.query_selector("div#stats-ondemand")
        if not stats_od:
            return None
        p_el = await stats_od.query_selector("p")
        if p_el:
            text = await p_el.text_content()
            if text:
                return text.strip()
        return None
