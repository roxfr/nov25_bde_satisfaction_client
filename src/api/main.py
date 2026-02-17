# File: src\api\main.py

"""Initialise l'application FastAPI et configure les routes ainsi que les métriques Prometheus."""

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import PrometheusFastApiInstrumentator
from api.routes import auth, es_queries, predict_user, predict_internal


def create_app() -> FastAPI:
    """Crée et configure l'application FastAPI."""
    app_instance: FastAPI = FastAPI(
        title="API de prédiction de sentiment des avis clients",
        description="API permettant de prédire le sentiment des avis clients.",
        version="1.0.0",
    )
    app_instance.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app_instance.include_router(predict_user.router, prefix="/predict", tags=["Predict User"])
    app_instance.include_router(predict_internal.router, prefix="/predict/internal", tags=["Predict Internal"])
    app_instance.include_router(es_queries.router, prefix="/es", tags=["Elasticsearch Queries"])

    # Instrumentation Prometheus
    PrometheusFastApiInstrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
    ).instrument(app_instance).expose(app_instance)
    
    return app_instance


app: FastAPI = create_app()

# Compteur de métriques Prometheus
api_requests_total: Counter = Counter(
    name="api_requests_total",
    documentation="Nombre total de requêtes traitées par l'API",
    labelnames=["method", "route", "status"],
)

# Middleware Prometheus
@app.middleware("http")
async def metrics_middleware(request: Request, call_next) -> Response:
    """Incrémente un compteur Prometheus pour chaque requête HTTP."""
    response: Response = await call_next(request)
    route = request.scope.get("route")
    route_path: str = route.path if route else "unknown"
    api_requests_total.labels(
        method=request.method,
        route=route_path,
        status=response.status_code,
    ).inc()
    return response
