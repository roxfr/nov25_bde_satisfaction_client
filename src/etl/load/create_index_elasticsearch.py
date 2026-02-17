# File: src\etl\load\create_index_elasticsearch.py

"""Gère la création de l'index Elasticsearch des avis s'il n'existe pas."""

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError, TransportError
from loguru import logger

from etl.load.mapping_reviews import MAPPING_REVIEWS


def create_index_if_not_exists(es: Elasticsearch, index: str = "reviews") -> None:
    """Crée l'index Elasticsearch avec son mapping s'il est absent."""
    try:
        index_exists: bool = es.indices.exists(index=index)
        if not index_exists:
            es.indices.create(index=index, body={"mappings": MAPPING_REVIEWS})
            logger.success(f"Index '{index}' créé avec succès")
        else:
            logger.info(f"Index '{index}' existe déjà")
    except RequestError as error:
        logger.exception(f"Erreur création index '{index}': {error}")
        raise
    except TransportError as error:
        logger.exception(f"Erreur transport Elasticsearch '{index}': {error}")
        raise
    except Exception as error:
        logger.exception(f"Erreur inattendue index '{index}': {error}")
        raise
