# File: src\api\routes\predict_user.py

"""Module FastAPI pour prédire le sentiment d'avis clients via un modèle ML pour les utilisateurs."""

from fastapi import APIRouter, HTTPException, Depends
from api.routes.auth import get_current_user
from api.schemas import PredictRequest, PredictResponse
from machine_learning.predict import predict_sentiment


router = APIRouter(tags=["Predict User"])

@router.post(
    "/",
    summary="Prédire le sentiment d'un avis client",
    description="Analyse un texte d'avis client et retourne le sentiment prédit (Négatif, Neutre ou Positif).",
    response_model=PredictResponse,
    response_description="Le sentiment prédit de l'avis client",
)
def predict_user_endpoint(
    request: PredictRequest,
    current_user: str = Depends(get_current_user)
) -> PredictResponse:
    """Prédit le sentiment d'un avis client à partir d'un texte fourni pour l'utilisateur."""
    try:
        return predict_sentiment(request.text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
