import json
import time
from pathlib import Path
from typing import Optional

from . import config


class TokenStore:
    """Persists auth tokens locally (gitignored file, 0600 permissions).

    Never commit the file this points to (config.TOKEN_STORE_PATH) to git.
    """

    def __init__(self, path: Path = config.TOKEN_STORE_PATH):
        self.path = path

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text())

    def save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2))
        self.path.chmod(0o600)

    @property
    def access_token(self) -> Optional[str]:
        return self.load().get("access_token")

    @property
    def refresh_cookie(self) -> Optional[str]:
        return self.load().get("keycloak_refresh_token")

    @property
    def user_id(self) -> Optional[int]:
        return self.load().get("user_id")

    def update(
        self,
        *,
        access_token: Optional[str] = None,
        refresh_cookie: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        data = self.load()
        if access_token is not None:
            data["access_token"] = access_token
        if refresh_cookie is not None:
            data["keycloak_refresh_token"] = refresh_cookie
        if user_id is not None:
            data["user_id"] = user_id
        data["updated_at"] = time.time()
        self.save(data)
