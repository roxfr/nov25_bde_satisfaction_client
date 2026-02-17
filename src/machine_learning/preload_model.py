# File: src\machine_learning\preload_model.py

"""Module pour précharger le modèle Hugging Face avant le démarrage de l'API Docker."""

from transformers import pipeline, logging


# --- Configuration ---
logging.set_verbosity_error()  # Désactive les warnings inutiles

print("Téléchargement du modèle de sentiment...")

# Préchargement du modèle et du tokenizer Hugging Face
pipeline(
    task="sentiment-analysis",
    model="cmarkea/distilcamembert-base-sentiment",
    tokenizer="cmarkea/distilcamembert-base-sentiment",
    truncation=True,
)

print("Modèle téléchargé avec succès !")
