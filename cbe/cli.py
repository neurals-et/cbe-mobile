"""
CBE Mobile Banking CLI Entry Point
"""

import sys
import argparse
from .client import CBEClient
from .config import CBEConfig
from .tui import CBEMobileTUI


def main():
    parser = argparse.ArgumentParser(
        prog="cbe",
        description="CBE Mobile Banking CLI & TUI - Commercial Bank of Ethiopia Client"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # tui command
    subparsers.add_parser("tui", help="Launch interactive Textual TUI")

    # balance command
    subparsers.add_parser("balance", help="View account balances")

    # lookup command
    lookup_p = subparsers.add_parser("lookup", help="Lookup recipient name for an account number")
    lookup_p.add_argument("account", help="13-digit CBE account number")

    # forex command
    subparsers.add_parser("forex", help="Fetch CBE live daily exchange rates")

    args = parser.parse_args()

    if args.command == "tui" or args.command is None:
        app = CBEMobileTUI()
        app.run()

    elif args.command == "balance":
        client = CBEClient()
        res = client.get_accounts()
        print("=== CBE Account Balances ===")
        for a in res.get("accounts", []):
            print(f"[{a['accountType']}] {a['accountNumber']}: {a['availableBalance']:,.2f} {a['currency']}")

    elif args.command == "lookup":
        client = CBEClient()
        res = client.lookup_account_info(args.account)
        print(f"Account: {args.account}")
        print(f"Holder:  {res.get('accountHolderName')}")
        print(f"Status:  {res.get('status')}")

    elif args.command == "forex":
        client = CBEClient()
        res = client.get_forex_rates()
        print(f"=== CBE Daily Forex Rates ({res.get('source')}) ===")
        for r in res.get("rates", []):
            print(f"{r.get('currency', '-'):6} | Buying: {r.get('buying', 0):8.2f} ETB | Selling: {r.get('selling', 0):8.2f} ETB | {r.get('name', '')}")


if __name__ == "__main__":
    main()
