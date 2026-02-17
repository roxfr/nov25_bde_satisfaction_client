# File: src\machine_learning\predict.py

"""Module pour prédire le sentiment d'avis utilisateurs avec un modèle NLP Hugging Face."""

from typing import Dict
from transformers import pipeline, logging
from etl.utils.data_utils import DataUtils

# --- Configuration du modèle Hugging Face ---
logging.set_verbosity_error()  # Désactive les messages info

# Chargement global du modèle pour éviter de le recharger à chaque prédiction
_model = pipeline(
    task="sentiment-analysis",
    model="cmarkea/distilcamembert-base-sentiment",
    tokenizer="cmarkea/distilcamembert-base-sentiment",
    truncation=True,
)


def convert_stars_to_sentiment(label: str) -> str:
    """Convertit un label en étoiles en sentiment textuel (Négatif, Neutre, Positif)."""
    label_upper = label.upper()
    if label_upper in ["1 STAR", "2 STARS"]:
        return "Négatif"
    elif label_upper == "3 STARS":
        return "Neutre"
    elif label_upper in ["4 STARS", "5 STARS"]:
        return "Positif"
    else:
        raise ValueError(f"Label inattendu : {label}")


def predict_sentiment(text: str) -> Dict[str, str]:
    """Prédit le sentiment d'un avis utilisateur et retourne le texte nettoyé et le sentiment."""
    text_clean: str = DataUtils.clean_text(text)
    if not text_clean:
        raise ValueError("L'avis fourni est vide ou non valide.")

    result = _model(text_clean, max_length=512)[0]
    sentiment: str = convert_stars_to_sentiment(result["label"])

    return {"text_clean": text_clean, "sentiment": sentiment}
