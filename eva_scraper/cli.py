import argparse
import getpass

from . import config
from .client import EvaClient
from .db import get_connection
from .scraper import scrape_last_matches


def cmd_login(args):
    client = EvaClient()
    email = args.email or config.EVA_EMAIL or input("Email: ")
    password = args.password or config.EVA_PASSWORD or getpass.getpass("Password: ")
    recaptcha_token = args.recaptcha_token or input(
        "Paste the x-recaptcha-token captured from the browser network tab: "
    )
    user = client.login(email=email, password=password, recaptcha_token=recaptcha_token)
    print(f"Logged in as {user['username']} (id={user['id']})")


def cmd_refresh(args):
    client = EvaClient()
    access_token = client.refresh()
    print(f"New access token stored ({access_token[:20]}...)")


def cmd_scrape(args):
    client = EvaClient()
    if not client.token_store.access_token:
        raise SystemExit("No stored access token. Run `login` first.")
    user_id = args.user_id or client.token_store.user_id
    if not user_id:
        raise SystemExit("No user id known. Pass --user-id or run `login` again.")

    conn = get_connection()
    count = scrape_last_matches(client, conn, user_id=user_id, season_id=args.season_id)
    print(f"Stored {count} matches for user {user_id}, season {args.season_id}")


def main():
    parser = argparse.ArgumentParser(description="EVA.gg scraper")
    sub = parser.add_subparsers(dest="command", required=True)

    login_parser = sub.add_parser("login", help="Authenticate against EVA.gg")
    login_parser.add_argument("--email")
    login_parser.add_argument("--password")
    login_parser.add_argument("--recaptcha-token")
    login_parser.set_defaults(func=cmd_login)

    refresh_parser = sub.add_parser("refresh", help="Renew the access token from the stored refresh cookie")
    refresh_parser.set_defaults(func=cmd_refresh)

    scrape_parser = sub.add_parser("scrape", help="Scrape player stats")
    scrape_parser.add_argument("--user-id", type=int, help="Defaults to the user id stored at login")
    scrape_parser.add_argument("--season-id", type=int, required=True)
    scrape_parser.set_defaults(func=cmd_scrape)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
