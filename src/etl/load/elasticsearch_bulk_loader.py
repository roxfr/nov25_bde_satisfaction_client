# File: src\etl\load\elasticsearch_bulk_loader.py

"""Charge les avis dans Elasticsearch via une opération bulk avec upsert."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch, helpers
from elasticsearch.exceptions import ConnectionError as elastic_connection_error
from loguru import logger
from etl.load.create_index_elasticsearch import create_index_if_not_exists


def load_reviews_to_elasticsearch_bulk(
    documents: List[Dict[str, Any]],
    es_host: Optional[str] = "http://elasticsearch:9200",
    index: str = "reviews",
    use_id: bool = True,
) -> None:
    """Insère ou met à jour des documents dans Elasticsearch en mode bulk upsert."""
    if not es_host:
        raise ValueError("es_host n'est pas défini")
    try:
        es: Elasticsearch = Elasticsearch(es_host)
        if not es.ping():
            raise elastic_connection_error("Connexion Elasticsearch impossible")
    except elastic_connection_error as error:
        logger.exception(f"Connexion Elasticsearch échouée : {error}")
        raise
    create_index_if_not_exists(es=es, index=index)
    if not documents:
        logger.warning("Aucun document à charger")
        return
    actions: List[Dict[str, Any]] = []
    now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for document in documents:
        if use_id and not document.get("id_review"):
            logger.warning("Document ignoré : 'id_review' manquant")
            continue
        doc: Dict[str, Any] = {**document, "updated_at": now}
        upsert_doc: Dict[str, Any] = {**doc}
        upsert_doc.setdefault("created_at", now)
        action: Dict[str, Any] = {
            "_op_type": "update",
            "_index": index,
            "_id": doc.get("id_review"),
            "doc": doc,
            "upsert": upsert_doc,
        }
        actions.append(action)
    try:
        success: int
        errors: List[Any]
        success, errors = helpers.bulk(es, actions, raise_on_error=False)
        logger.success(f"{success} documents insérés ou mis à jour")
        if errors:
            logger.warning(f"Erreurs bulk détectées : {errors}")
    except Exception as error:
        logger.exception(f"Erreur critique bulk Elasticsearch : {error}")
        raise
