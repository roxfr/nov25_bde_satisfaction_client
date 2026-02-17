# File: src\tests\test_transform_reviews.py

"""Test de la transformation des avis pour Elasticsearch avec sentiment utilisateur."""

from typing import Any, Dict, List
from unittest.mock import patch
from etl.transform.transform_reviews import transform_reviews_for_elasticsearch
from etl.load.mapping_reviews import MAPPING_REVIEWS


# Exemple de données brutes pour le test
raw_reviews: List[Dict[str, Any]] = [
    {
        "reviews": [
            {
                "id": "review_1",
                "consumer": {"id": "user_1"},
                "text": "Great product!",
                "rating": 5,
                "dates": {"publishedDate": "2023-01-01"},
                "reply": {"message": "Thank you!"},
                "labels": {"verification": {"isVerified": True}}
            }
        ],
        "enterprise": {
            "name": "Example Enterprise",
            "ratings": {
                "total": 10,
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 2,
                "five": 2
            },
            "enterprise_rating": 4.5,
            "enterprise_review_number": 10
        }
    }
]

@patch("etl.transform.transform_reviews.predict_sentiment_from_api")
def test_transform_reviews_for_elasticsearch(mock_predict) -> None:
    """Vérifie que les avis bruts sont transformés correctement pour Elasticsearch."""
    # Mock du modèle de sentiment
    mock_predict.side_effect = lambda text: {"text_clean": text, "sentiment": "Neutre"}

    transformed_reviews: List[Dict[str, Any]] = transform_reviews_for_elasticsearch(raw_reviews)

    # Vérification du nombre de documents
    assert len(transformed_reviews) == 1

    first_review: Dict[str, Any] = transformed_reviews[0]

    # Vérification du champ user_sentiment
    assert first_review["user_sentiment"] == "Neutre"

    # Vérification que tous les champs du mapping sont présents dans le document transformé
    excluded_fields: set[str] = {"created_at", "updated_at"}
    expected_fields: set[str] = set(MAPPING_REVIEWS["properties"].keys()) - excluded_fields
    doc_fields: set[str] = set(first_review.keys())
    missing_fields: set[str] = expected_fields - doc_fields
    extra_fields: set[str] = doc_fields - expected_fields

    assert not missing_fields, f"Champs manquants dans le document : {missing_fields}"
    assert not extra_fields, f"Champs non déclarés dans le mapping : {extra_fields}"
