# File: src\api\schemas.py

"""Définit les schémas Pydantic pour la validation des requêtes et réponses de prédiction."""

from pydantic import BaseModel


class PredictRequest(BaseModel):
    """Modèle représentant le texte à analyser pour la prédiction."""
    text: str


class PredictResponse(BaseModel):
    """Modèle représentant le texte nettoyé et le sentiment retourné."""
    text_clean: str
    sentiment: str
