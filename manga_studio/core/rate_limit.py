"""Limitation de débit Redis pour les opérations API coûteuses."""

import hashlib
import os
import time

from redis import Redis
from redis.exceptions import RedisError


class RateLimiterUnavailable(RuntimeError):
    """Redis est requis mais indisponible pour appliquer la limite."""


def enforce_rate_limit(identity: str) -> None:
    """Applique une fenêtre fixe par identité et lève si le quota est dépassé.

    Le limiteur est désactivable explicitement avec une limite à zéro, utile pour
    les tests locaux. Les clés Redis contiennent uniquement un SHA-256 de la clé
    API, jamais le secret en clair.
    """
    limit = int(os.getenv("MANGA_STUDIO_API_RATE_LIMIT_PER_MINUTE", "30"))
    if limit <= 0:
        return

    redis_url = os.getenv("MANGA_STUDIO_REDIS_URL", "redis://localhost:6379/0")
    bucket = int(time.time() // 60)
    identity_hash = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    redis_key = f"manga-studio:rate-limit:{identity_hash}:{bucket}"
    try:
        client = Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=5)
        used = client.incr(redis_key)
        if used == 1:
            client.expire(redis_key, 120)
    except RedisError as exc:
        raise RateLimiterUnavailable("Redis indisponible pour le rate limiting.") from exc

    if used > limit:
        raise PermissionError("Limite de requêtes atteinte ; réessayez dans une minute.")
