from typing import Optional

import requests

from . import config
from .auth import TokenStore
from .queries import LOGIN_MUTATION


class EvaApiError(RuntimeError):
    pass


class EvaClient:
    def __init__(self, token_store: Optional[TokenStore] = None):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "content-type": "application/json",
                "origin": config.EVA_APP_ORIGIN,
                "referer": config.EVA_APP_ORIGIN + "/",
            }
        )
        self.token_store = token_store or TokenStore()
        access_token = self.token_store.access_token
        if access_token:
            self.session.headers["authorization"] = f"Bearer {access_token}"

    def login(self, email: str, password: str, recaptcha_token: str, otp: Optional[str] = None) -> dict:
        """Perform the initial login.

        `recaptcha_token` must be captured manually from the browser (grab
        the `x-recaptcha-token` header sent by app.eva.gg on the login
        request) — automating reCAPTCHA solving is out of scope here, so
        this call is meant to be run interactively, not on a schedule.
        """
        response = self.session.post(
            config.EVA_API_URL,
            json={
                "operationName": "login",
                "query": LOGIN_MUTATION,
                "variables": {"email": email, "password": password, "otp": otp},
            },
            headers={"x-recaptcha-token": recaptcha_token},
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise EvaApiError(str(payload["errors"]))

        access_token = payload["data"]["login"]["accessToken"]
        refresh_cookie = self.session.cookies.get("keycloak_refresh_token", domain=".eva.gg")
        self.token_store.update(access_token=access_token, refresh_cookie=refresh_cookie)
        self.session.headers["authorization"] = f"Bearer {access_token}"
        return payload["data"]["login"]

    def refresh(self) -> None:
        """Renew the access token using the stored refresh cookie.

        TODO: not implemented yet. We only have the `login` request
        captured so far. To finish this, capture the network request the
        app.eva.gg SPA makes to silently renew its access token (it fires
        automatically on page load while the `keycloak_refresh_token`
        cookie is still valid) and port it here — that call is expected
        to *not* require a reCAPTCHA token, which is what makes unattended
        scraping practical.
        """
        raise NotImplementedError(
            "Refresh flow not captured yet — see the docstring on EvaClient.refresh."
        )

    def graphql(self, operation_name: str, query: str, variables: dict) -> dict:
        response = self.session.post(
            config.EVA_API_URL,
            json={"operationName": operation_name, "query": query, "variables": variables},
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise EvaApiError(str(payload["errors"]))
        return payload["data"]
