# File: src\etl\transform\transform_reviews.py

"""Transformation des avis bruts en documents prêts pour Elasticsearch."""

import math
import re
import requests
from typing import Dict, Any, List
from loguru import logger
from etl.utils.data_utils import DataUtils


def anonymize_text(text: str) -> str:
    """Anonymise un texte en masquant emails, numéros, noms et salutations."""
    text = re.sub(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "[EMAIL_SUPPRIMÉ]", text)
    text = re.sub(r"(?:\+33\s*\(?0?\)?|0)[1-9](?:[\s.\-]?\d{2}){4}", "[TÉLÉPHONE_SUPPRIMÉ]", text)
    text = re.sub(r"(?im)^(Bonour|Bonnour|Bonjouir|Bonsoir|Bonoir)", "Bonjour", text)
    text = re.sub(r"(?im)^Bonjour\s+[^\n,]+(?:\s*,)?\s*$", "Bonjour [NOM_ANONYMISÉ],", text)
    text = re.sub(
        r"\b(MR|M|MME|Mme|Monsieur|Madame|Melle)\s+[A-Za-zÀ-ÖØ-öø-ÿ-]+(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ-]+)*\b",
        "[NOM_ANONYMISÉ]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"(?m)^(?:[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ-]+)(?:\s+[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿ-]+)*[.,]?$", "[NOM_ANONYMISÉ]", text)
    return text


def predict_sentiment_from_api(text: str) -> Dict[str, Any]:
    """Appelle l'API FastAPI pour prédire le sentiment d'un texte."""
    PREDICT_API_URL = "http://fastapi:8000/predict/internal"
    payload = {"text": text}
    try:
        response = requests.post(PREDICT_API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Erreur lors de l'appel à FastAPI: {e}")
        return {"sentiment": "Indéfini"}


def transform_reviews_for_elasticsearch(raw_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transforme les avis bruts en documents formatés pour Elasticsearch."""
    all_transformed_reviews: List[Dict[str, Any]] = []
    total_reviews = 0

    for raw in raw_list:
        reviews = raw.get("reviews", [])
        total_reviews += len(reviews)
        enterprise_url: str = raw.get("enterprise_url", "")
        enterprise_info: Dict[str, Any] = raw.get("enterprise", {})

        ratings = enterprise_info.get("ratings", {})
        total = max(ratings.get("total", 0), 1)
        pct_one = math.ceil(ratings.get("one", 0) / total * 100)
        pct_two = math.ceil(ratings.get("two", 0) / total * 100)
        pct_three = math.ceil(ratings.get("three", 0) / total * 100)
        pct_four = math.ceil(ratings.get("four", 0) / total * 100)
        pct_five = math.ceil(ratings.get("five", 0) / total * 100)

        for review in reviews:
            user = review.get("consumer", {})
            reply = review.get("reply", {})
            dates = review.get("dates", {})
            verification = review.get("labels", {}).get("verification", {})

            text_clean = DataUtils.clean_text(review.get("text"))
            text_clean = "indisponible" if not text_clean else anonymize_text(text_clean)
            review_length = len(text_clean)

            reply_clean = DataUtils.clean_text(reply.get("message") if reply else None)
            reply_clean = "indisponible" if not reply_clean else anonymize_text(reply_clean)

            try:
                user_sentiment = (
                    predict_sentiment_from_api(text_clean).get("sentiment", "Indéfini")
                    if text_clean != "indisponible"
                    else "Indéfini"
                )
            except Exception as e:
                logger.warning(f"Erreur API sentiment: {e}")
                user_sentiment = "Indéfini"

            all_transformed_reviews.append({
                "id_review": review.get("id"),
                "is_verified": bool(verification.get("isVerified", False)),
                "date_review": DataUtils.format_date(dates.get("publishedDate")),
                "id_user": DataUtils.clean_text(user.get("id")),
                "user_review": text_clean,
                "user_review_length": review_length,
                "user_rating": DataUtils.to_float(review.get("rating")),
                "user_sentiment": user_sentiment,
                "date_response": DataUtils.format_date(reply.get("publishedDate") if reply else None),
                "enterprise_response": reply_clean,
                "enterprise_name": DataUtils.clean_text(enterprise_info.get("name") or enterprise_url),
                "enterprise_url": enterprise_url,
                "enterprise_rating": DataUtils.to_float(enterprise_info.get("enterprise_rating")),
                "enterprise_review_number": DataUtils.to_int(enterprise_info.get("enterprise_review_number")),
                "enterprise_percentage_one_star": pct_one,
                "enterprise_percentage_two_star": pct_two,
                "enterprise_percentage_three_star": pct_three,
                "enterprise_percentage_four_star": pct_four,
                "enterprise_percentage_five_star": pct_five,
            })

    logger.info(f"[INFO] Total reviews traitées : {total_reviews}")
    return all_transformed_reviews
