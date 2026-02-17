# File: src\etl\extract\reviews_scraper.py

"""Extrait les avis Trustpilot et les métadonnées associées via l'API interne."""

import asyncio
import json
from typing import Any, Dict, List
from loguru import logger
from parsel import Selector
from etl.config.config import ENTERPRISES
from etl.utils.http_client import HttpClient


client: Any = HttpClient.get_client()
logger.info(f"Entreprises configurées : {[e['enterprise_url'] for e in ENTERPRISES]}")


async def get_reviews_url_api(url_base: str) -> str:
    """Construit dynamiquement l'URL API des avis à partir du buildId."""
    try:
        response: Any = await client.get(url_base)
        selector: Selector = Selector(response.text)
        raw_data: str | None = selector.xpath("//script[@id='__NEXT_DATA__']/text()").get()
        if not raw_data:
            raise RuntimeError(f"__NEXT_DATA__ introuvable sur {url_base}")
        build_id: str = json.loads(raw_data)["buildId"]
        business_unit: str = url_base.split("review/")[-1]
        return (
            f"https://www.trustpilot.com/_next/data/{build_id}/review/"
            f"{business_unit}.json?sort=recency&businessUnit={business_unit}&languages=fr"
        )
    except Exception as error:
        logger.exception(f"[get_reviews_url_api] Erreur pour {url_base}: {error}")
        raise


async def scrape_reviews(url_base: str, max_pages: int = 1) -> List[Dict[str, Any]]:
    """Récupère les avis paginés d'une entreprise via l'API Next.js."""
    try:
        url_api: str = await get_reviews_url_api(url_base)
    except Exception:
        logger.error(f"[scrape_reviews] URL API invalide pour {url_base}")
        return []
    try:
        first_page: Any = await client.post(url_api)
        first_page.raise_for_status()
        data: Dict[str, Any] = json.loads(first_page.text)["pageProps"]
        reviews_data: List[Dict[str, Any]] = data["reviews"]
        total_pages: int = data["filters"]["pagination"]["totalPages"]
        if max_pages and max_pages < total_pages:
            total_pages = max_pages
        logger.info(f"Total pages à scraper : {total_pages}")
    except Exception as error:
        logger.error(f"[scrape_reviews] Erreur première page {url_base}: {error}")
        return []
    other_pages = [
        client.post(f"{url_api}&page={page_number}")
        for page_number in range(2, total_pages + 1)
    ]
    for page_number, response_future in zip(
        range(2, total_pages + 1),
        asyncio.as_completed(other_pages),
    ):
        logger.info(f"Scraping page {page_number}/{total_pages}")
        try:
            response: Any = await response_future
            response.raise_for_status()
            page_json: Dict[str, Any] = json.loads(response.text)
            page_reviews: List[Dict[str, Any]] = page_json["pageProps"].get("reviews", [])
            reviews_data.extend(page_reviews)
            logger.info(f"Page {page_number}: {len(page_reviews)} avis")
        except Exception as error:
            logger.error(f"[scrape_reviews] Erreur page {page_number}: {error}")
    logger.info(f"Extraction terminée : {len(reviews_data)} avis")
    return reviews_data


async def get_reviews_from_trustpilot(max_pages: int) -> List[Dict[str, Any]]:
    """Extrait les avis et statistiques pour toutes les entreprises configurées."""
    results: List[Dict[str, Any]] = []
    if not ENTERPRISES:
        logger.warning("Aucune entreprise configurée")
        return results
    for enterprise in ENTERPRISES:
        enterprise_url: str | None = enterprise.get("enterprise_url")
        if not enterprise_url:
            logger.warning("Entreprise sans 'enterprise_url' ignorée")
            continue
        url_base: str = f"https://www.trustpilot.com/review/{enterprise_url}"
        try:
            reviews_data: List[Dict[str, Any]] = await scrape_reviews(url_base, max_pages)
            url_api: str = await get_reviews_url_api(url_base)
            first_page: Any = await client.post(url_api)
            first_page.raise_for_status()
            page_props: Dict[str, Any] = json.loads(first_page.text)["pageProps"]
            review_stats: Dict[str, Any] = page_props.get("filters", {}).get("reviewStatistics", {})
            ratings: Dict[str, Any] = review_stats.get("ratings", {})
            enterprise_info: Dict[str, Any] = {
                "enterprise_rating": page_props.get("businessUnit", {}).get("trustScore"),
                "enterprise_review_number": page_props.get("businessUnit", {}).get("numberOfReviews"),
                "ratings": ratings,
                "name": page_props.get("businessUnit", {}).get("displayName") or enterprise_url,
            }
            results.append(
                {
                    "enterprise_url": enterprise_url,
                    "enterprise": enterprise_info,
                    "reviews": reviews_data,
                }
            )
        except Exception as error:
            logger.error(f"[get_reviews_from_trustpilot] Erreur {url_base}: {error}")
            results.append(
                {
                    "enterprise_url": enterprise_url,
                    "enterprise": {},
                    "reviews": [],
                }
            )
    return results
