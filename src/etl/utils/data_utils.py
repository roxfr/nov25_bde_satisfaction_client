# File: src\etl\utils\data_utils.py

"""Utilitaires pour nettoyer, convertir et formater des données."""

import re
import unicodedata
from typing import Any, Optional
from datetime import datetime


class DataUtils:
    """Classe utilitaire pour nettoyer, convertir et formater les données."""

    @staticmethod
    def clean_text(text: Optional[str], max_length: int = 5000) -> Optional[str]:
        """Nettoie un texte et tronque à la longueur maximale."""
        if not text:
            return None
        text = unicodedata.normalize("NFKC", text).strip()
        text = re.sub(r"\s+", " ", text)
        if not re.search(r"[a-zA-Z0-9]", text):
            return None
        return text[:max_length]

    @staticmethod
    def to_float(value: Any, default: float = 0.0) -> float:
        """Convertit une valeur en float ou retourne la valeur par défaut si échec."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def to_int(value: Any, default: int = 0) -> int:
        """Convertit une valeur en int ou retourne la valeur par défaut si échec."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def format_date(date_str: Optional[str]) -> Optional[str]:
        """Formate une chaîne ISO 8601 en 'YYYY-MM-DD' ou retourne None si invalide."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date().isoformat()
        except Exception:
            return None
