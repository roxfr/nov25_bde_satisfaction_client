# File: src\etl\utils\http_client.py

"""Client HTTP asynchrone singleton basé sur httpx.AsyncClient."""

from typing import Optional
from httpx import AsyncClient


class HttpClient:
    """Gestion d'un client HTTP asynchrone unique (Singleton)."""

    _client: Optional[AsyncClient] = None

    @classmethod
    def get_client(cls) -> AsyncClient:
        """Retourne l'instance unique d'AsyncClient ou la crée si elle n'existe pas."""
        if cls._client is None:
            cls._client = AsyncClient(
                http2=True,
                headers={
                    "accept-language": "fr-FR,fr;q=0.9",
                    "user-agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/96.0.4664.110 Safari/537.36"
                    ),
                    "accept": (
                        "text/html,application/xhtml+xml,application/xml;q=0.9,"
                        "image/webp,image/apng,*/*;q=0.8"
                    ),
                    "accept-encoding": "gzip, deflate, br",
                },
                timeout=30.0,
            )
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Ferme proprement le client HTTP unique si présent."""
        if cls._client:
            await cls._client.aclose()
            cls._client = None
