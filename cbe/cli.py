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
    bal_p = subparsers.add_parser("balance", help="View account balances")
    bal_p.add_argument("--token", "-t", help="JWT Access Token (or uses saved config)")

    # lookup command
    lookup_p = subparsers.add_parser("lookup", help="Lookup recipient name for an account number")
    lookup_p.add_argument("account", help="13-digit CBE account number")
    lookup_p.add_argument("--token", "-t", help="JWT Access Token (or uses saved config)")

    # forex command
    subparsers.add_parser("forex", help="Fetch CBE live daily exchange rates")

    # login command
    login_p = subparsers.add_parser("login", help="Log in with Phone + PIN or request SMS OTP")
    login_p.add_argument("--phone", "-p", required=True, help="Phone number (+251...)")
    login_p.add_argument("--pin", help="4-digit CBE mobile banking PIN")
    login_p.add_argument("--otp", action="store_true", help="Request SMS OTP code instead of PIN")

    # verify-otp command
    otp_p = subparsers.add_parser("verify-otp", help="Verify SMS OTP and save session JWT")
    otp_p.add_argument("code", help="SMS OTP code received on phone")
    otp_p.add_argument("--tfa", required=True, help="TFA token received from login/otp request")

    # config command
    cfg_p = subparsers.add_parser("config", help="View or update credentials and settings")
    cfg_p.add_argument("--token", help="Set JWT Access Token")
    cfg_p.add_argument("--phone", help="Set Phone Number (+251...)")
    cfg_p.add_argument("--device-id", help="Set Device Unique ID")
    cfg_p.add_argument("--live", action="store_true", help="Switch to Live mode (disable mock)")
    cfg_p.add_argument("--mock", action="store_true", help="Switch to Mock simulation mode")

    args = parser.parse_args()

    if args.command == "tui" or args.command is None:
        app = CBEMobileTUI()
        app.run()

    elif args.command == "balance":
        client = CBEClient(token=args.token)
        res = client.get_accounts()
        print("=== CBE Account Balances ===")
        for a in res.get("accounts", []):
            print(f"[{a['accountType']}] {a['accountNumber']}: {a['availableBalance']:,.2f} {a['currency']}")

    elif args.command == "lookup":
        client = CBEClient(token=args.token)
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

    elif args.command == "login":
        client = CBEClient()
        if args.otp:
            res = client.request_otp(args.phone)
            print(f"Status:   {res.get('status')}")
            print(f"Message:  {res.get('message')}")
            print(f"TFA Token: {res.get('tfaToken')}")
            print("\nRun: cbe verify-otp <code> --tfa <TFA_TOKEN> to complete login.")
        else:
            if not args.pin:
                print("Error: --pin is required (or use --otp to request SMS code).", file=sys.stderr)
                sys.exit(1)
            res = client.sign_in_pin(args.phone, args.pin)
            if res.get("status") == "SUCCESS":
                print("[OK] Logged in successfully!")
                print(f"Customer: {res.get('user', {}).get('fullName')}")
                print(f"JWT Token: {res.get('accessToken')[:30]}...")
            else:
                print(f"Login failed: {res}")

    elif args.command == "verify-otp":
        client = CBEClient()
        res = client.verify_otp(args.tfa, args.code)
        if res.get("status") == "SUCCESS":
            token = res.get("accessToken")
            print("[OK] OTP verified successfully!")
            print(f"Session JWT saved: {token[:30]}...")
            print("You are now authenticated for live CBE queries.")
        else:
            print(f"Verification failed: {res}")

    elif args.command == "config":
        cfg = CBEConfig()
        updated = False
        if args.token:
            cfg.set("access_token", args.token)
            updated = True
        if args.phone:
            cfg.set("phone_number", args.phone)
            updated = True
        if args.device_id:
            cfg.set("device_id", args.device_id)
            updated = True
        if args.live:
            cfg.set("mock_mode", False)
            updated = True
        elif args.mock:
            cfg.set("mock_mode", True)
            updated = True

        if updated:
            cfg.save()
            print("[OK] Configuration updated successfully.")

        print("=== Current Configuration ===")
        print(f"  API Base:    {cfg.get('api_base')}")
        print(f"  Phone:       {cfg.get('phone_number')}")
        print(f"  Device ID:   {cfg.get('device_id')}")
        token = cfg.get('access_token')
        print(f"  JWT Token:   {token[:25] + '...' if token else '(None Set)'}")
        print(f"  Mode:        {'MOCK (Simulated)' if cfg.get('mock_mode') else 'LIVE (CBE Gateway)'}")


if __name__ == "__main__":
    main()
