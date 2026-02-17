# File: src\api\routes\predict_internal.py

"""Module FastAPI pour prédire le sentiment d'avis clients via un modèle ML pour l'ETL."""

from fastapi import APIRouter, HTTPException
from api.schemas import PredictRequest, PredictResponse
from machine_learning.predict import predict_sentiment


router = APIRouter(tags=["Predict Internal"])

@router.post(
    "/",
    summary="Prédiction pour la transformation des avis",
    description="Prédit le sentiment d'un avis client sans besoin de token d'authentification, utilisé en interne.",
    response_model=PredictResponse,
    response_description="Le sentiment prédit de l'avis client",
)
def predict_internal_endpoint(
    request: PredictRequest
) -> PredictResponse:
    """Prédit le sentiment d'un avis client à partir d'un texte fourni pour l'ETL (sans token)."""
    try:
        return predict_sentiment(request.text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
