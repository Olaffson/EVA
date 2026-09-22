from typing import Optional

import requests

from . import config
from .auth import TokenStore
from .queries import LOGIN_MUTATION, REFRESH_TOKEN_MUTATION

REFRESH_COOKIE_NAME = "keycloak_refresh_token"
REFRESH_COOKIE_DOMAIN = ".eva.gg"


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
        tokens = self.token_store.load()
        access_token = tokens.get("access_token")
        refresh_cookie = tokens.get(REFRESH_COOKIE_NAME)
        if access_token:
            self.session.headers["authorization"] = f"Bearer {access_token}"
        if refresh_cookie:
            self.session.cookies.set(REFRESH_COOKIE_NAME, refresh_cookie, domain=REFRESH_COOKIE_DOMAIN, path="/")

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
        refresh_cookie = self.session.cookies.get(REFRESH_COOKIE_NAME, domain=REFRESH_COOKIE_DOMAIN)
        self.token_store.update(access_token=access_token, refresh_cookie=refresh_cookie)
        self.session.headers["authorization"] = f"Bearer {access_token}"
        return payload["data"]["login"]

    def refresh(self) -> str:
        """Renew the access token using the stored refresh cookie.

        Relies on the `keycloak_refresh_token` cookie the browser sent
        automatically on login — no reCAPTCHA needed, so this is safe to
        call unattended (e.g. before each scraping run).
        """
        if not self.session.cookies.get(REFRESH_COOKIE_NAME, domain=REFRESH_COOKIE_DOMAIN):
            raise EvaApiError("No stored refresh cookie. Run `login` first.")

        data = self.graphql("refreshToken", REFRESH_TOKEN_MUTATION, {}, allow_refresh=False)
        access_token = data["refreshToken"]["accessToken"]
        new_refresh_cookie = self.session.cookies.get(REFRESH_COOKIE_NAME, domain=REFRESH_COOKIE_DOMAIN)
        self.token_store.update(access_token=access_token, refresh_cookie=new_refresh_cookie)
        self.session.headers["authorization"] = f"Bearer {access_token}"
        return access_token

    def graphql(
        self, operation_name: str, query: str, variables: dict, *, allow_refresh: bool = True
    ) -> dict:
        response = self.session.post(
            config.EVA_API_URL,
            json={"operationName": operation_name, "query": query, "variables": variables},
        )
        if response.status_code == 401 and allow_refresh:
            self.refresh()
            return self.graphql(operation_name, query, variables, allow_refresh=False)
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            raise EvaApiError(str(payload["errors"]))
        return payload["data"]
