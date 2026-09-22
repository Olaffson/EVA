import argparse
import getpass

from . import config
from .client import EvaClient
from .db import get_connection


def cmd_login(args):
    client = EvaClient()
    email = args.email or config.EVA_EMAIL or input("Email: ")
    password = args.password or config.EVA_PASSWORD or getpass.getpass("Password: ")
    recaptcha_token = args.recaptcha_token or input(
        "Paste the x-recaptcha-token captured from the browser network tab: "
    )
    user = client.login(email=email, password=password, recaptcha_token=recaptcha_token)
    print(f"Logged in as {user['username']} (id={user['id']})")


def cmd_scrape(args):
    client = EvaClient()
    if not client.token_store.access_token:
        raise SystemExit("No stored access token. Run `login` first.")
    get_connection()
    print(
        "TODO: player stats GraphQL query not captured yet. "
        "Capture it from a profile page on app.eva.gg and wire it into "
        "eva_scraper/queries.py + a new scraper function."
    )


def main():
    parser = argparse.ArgumentParser(description="EVA.gg scraper")
    sub = parser.add_subparsers(dest="command", required=True)

    login_parser = sub.add_parser("login", help="Authenticate against EVA.gg")
    login_parser.add_argument("--email")
    login_parser.add_argument("--password")
    login_parser.add_argument("--recaptcha-token")
    login_parser.set_defaults(func=cmd_login)

    scrape_parser = sub.add_parser("scrape", help="Scrape player stats")
    scrape_parser.add_argument("usernames", nargs="+")
    scrape_parser.set_defaults(func=cmd_scrape)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
