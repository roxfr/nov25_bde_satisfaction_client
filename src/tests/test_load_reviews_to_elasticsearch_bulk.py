# File: src\tests\test_load_reviews_to_elasticsearch_bulk.py

"""Tests unitaires pour la fonction load_reviews_to_elasticsearch_bulk."""

from typing import Generator
import pytest
from unittest.mock import patch
from etl.load.elasticsearch_bulk_loader import load_reviews_to_elasticsearch_bulk


@pytest.fixture
def mock_es() -> Generator:
    """Crée un mock de la connexion Elasticsearch."""
    with patch("etl.load.elasticsearch_bulk_loader.Elasticsearch") as mock_es_class:
        mock_es_instance = mock_es_class.return_value
        mock_es_instance.ping.return_value = True
        yield mock_es_instance


@patch("etl.load.elasticsearch_bulk_loader.helpers.bulk")
def test_load_reviews_bulk(mock_bulk, mock_es) -> None:
    """Vérifie l'insertion et la mise à jour de documents via le bulk API Elasticsearch."""
    documents = [
        {"id_review": "123", "review_text": "Super produit!"},
        {"id_review": "124", "review_text": "Moyen, mais correct."},
    ]

    # Simule le comportement de helpers.bulk
    mock_bulk.return_value = (2, [])  # 2 documents insérés, aucune erreur

    # Appel de la fonction
    load_reviews_to_elasticsearch_bulk(documents, es_host="http://localhost:9200/", index="reviews")

    # Vérifie que la méthode ping() a été appelée
    mock_es.ping.assert_called_once()

    # Vérifie que helpers.bulk a bien été appelé
    mock_bulk.assert_called_once()

    # Vérifie que chaque document a bien été transformé en action avec timestamps
    actions = mock_bulk.call_args[0][1]
    assert len(actions) == len(documents)
    for action in actions:
        assert "updated_at" in action["doc"]
        assert "created_at" in action["upsert"]
