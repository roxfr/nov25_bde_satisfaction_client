# File: src\tests\test_reviews_scraper.py

"""Test de l'accessibilité d'une URL Trustpilot."""

import pytest
import aiohttp


@pytest.mark.asyncio
async def test_trustpilot_url() -> None:
    """Vérifie que la page Trustpilot d'une entreprise est accessible (HTTP 200)."""
    enterprise_url: str = "www.showroomprive.com"
    url_base: str = f"https://www.trustpilot.com/review/{enterprise_url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url_base) as response:
            assert response.status == 200
