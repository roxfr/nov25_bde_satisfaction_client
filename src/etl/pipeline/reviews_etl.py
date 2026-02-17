# File: src\etl\pipeline\reviews_etl.py

"""Orchestration de l'ETL des avis clients (extract, transform, load)."""

import logging
import asyncio
from typing import List, Dict
from etl.extract.reviews_scraper import get_reviews_from_trustpilot
from etl.transform.transform_reviews import transform_reviews_for_elasticsearch
from etl.load.elasticsearch_bulk_loader import load_reviews_to_elasticsearch_bulk
from etl.utils.files_utils import FileUtils


# Configuration du logger Airflow
log = logging.getLogger("airflow.task")


def run_extract(data_path: str, max_pages: int) -> None:
    """Extrait les avis depuis Trustpilot et sauvegarde les données brutes."""
    log.info("[EXTRACT] Démarrage extraction")
    extract_raw: List[Dict] = []
    try:
        extract_raw = asyncio.run(get_reviews_from_trustpilot(max_pages=max_pages))
        if not extract_raw:
            raise ValueError("Aucune donnée extraite")
        FileUtils.save_to_json(extract_raw, "extract_raw", data_path)
        log.info(f"[EXTRACT] {len(extract_raw)} entreprises extraites")
    except Exception as e:
        log.error(f"[EXTRACT] Erreur : {e}")
        raise

def run_transform(data_path: str) -> None:
    """Transforme les avis bruts en documents prêts pour Elasticsearch."""
    log.info("[TRANSFORM] Démarrage transformation")
    transform_docs: List[Dict] = []
    try:
        extract_raw = FileUtils.load_last_json(data_path)
        if not extract_raw:
            raise ValueError("Aucune donnée brute trouvée")
        transform_docs = transform_reviews_for_elasticsearch(extract_raw)
        if not transform_docs:
            raise ValueError("Aucun document transformé")
        FileUtils.save_to_jsonl(transform_docs, "reviews", data_path)
        FileUtils.delete_all_json_files(data_path)  # RGPD : suppression des JSON bruts
        log.info(f"[TRANSFORM] {len(transform_docs)} documents transformés")
    except Exception as e:
        log.error(f"[TRANSFORM] Erreur : {e}")
        raise

def run_load(data_path: str) -> None:
    """Charge les documents transformés dans Elasticsearch via bulk upsert."""
    log.info("[LOAD] Chargement vers Elasticsearch")
    try:
        transform_docs = FileUtils.load_last_jsonl(data_path)
        if not transform_docs:
            raise ValueError("Aucun document à charger")
        load_reviews_to_elasticsearch_bulk(transform_docs, index="reviews")
        log.info("[LOAD] Chargement terminé")
    except Exception as e:
        log.error(f"[LOAD] Erreur : {e}")
        raise
