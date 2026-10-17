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

    # cards command
    crd_p = subparsers.add_parser("cards", help="Manage debit cards")
    crd_p.add_argument("--request", choices=["VISA_DEBIT", "MASTERCARD_VIRTUAL"], help="Request a new card")

    # loans command
    loan_p = subparsers.add_parser("loans", help="Digital microloans (CBE credit)")
    loan_p.add_argument("--request", type=float, help="Request loan disbursal amount")
    loan_p.add_argument("--repay", help="Repay loan by ID")
    loan_p.add_argument("--amount", type=float, help="Repay amount")

    # beneficiaries command
    ben_p = subparsers.add_parser("beneficiaries", help="Saved transfer contacts")
    ben_p.add_argument("--add", help="Account number to add")
    ben_p.add_argument("--name", help="Account holder name")
    ben_p.add_argument("--bank", default="CBE", help="Bank name (default: CBE)")

    # receipt command
    rcpt_p = subparsers.add_parser("receipt", help="Verify and view transaction receipt")
    rcpt_p.add_argument("id", help="Transaction reference / ID")

    # scheduled command
    subparsers.add_parser("scheduled", help="View scheduled auto-transfers")

    # split command
    split_p = subparsers.add_parser("split", help="Initiate split bill request")
    split_p.add_argument("amount", type=float, help="Total bill amount")
    split_p.add_argument("--with-users", required=True, nargs="+", help="Phone numbers / accounts to split with")
    split_p.add_argument("--reason", default="Dinner / Group Bill", help="Reason for split")

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

    elif args.command == "cards":
        client = CBEClient()
        if args.request:
            r = client.request_card(client.config.get("account_number"), args.request)
            print(f"[OK] Card requested! Reference: {r.get('referenceNumber')}")
        else:
            res = client.get_cards()
            print("=== Linked CBE Cards ===")
            for c in res.get("cards", []):
                print(f"[{c['cardType']}] {c['maskedNumber']} (Exp: {c['expiry']}) -> {c['status']}")

    elif args.command == "loans":
        client = CBEClient()
        if args.request:
            r = client.request_loan(args.request)
            print(f"[OK] Microloan approved! ID: {r.get('loanId')} | Amount: {r.get('disbursedAmount')} ETB (Due: {r.get('dueDate')})")
        elif args.repay:
            amt = args.amount or 1000.0
            r = client.repay_loan(args.repay, amt)
            print(f"[OK] Microloan repayment successful! Receipt: {r.get('receiptNumber')}")
        else:
            d = client.get_loan_dashboard()
            print(f"=== CBE Digital Microloans (Eligible: {d.get('eligible')}) ===")
            print(f"Credit Limit: {d.get('maxCreditLimit'):,.2f} ETB")
            curr = d.get("currentLoan", {})
            if curr:
                print(f"Active Loan:  {curr.get('loanId')} | {curr.get('remainingAmount')} ETB due on {curr.get('dueDate')}")

    elif args.command == "beneficiaries":
        client = CBEClient()
        if args.add:
            name = args.name or "Contact"
            r = client.add_beneficiary(args.add, name, args.bank)
            print(f"[OK] Beneficiary added: {r.get('name')} ({r.get('accountNumber')})")
        else:
            bens = client.get_beneficiaries()
            print("=== Saved Transfer Contacts ===")
            for b in bens:
                print(f"  - {b['name']}: {b['accountNumber']} ({b['bank']})")

    elif args.command == "receipt":
        client = CBEClient()
        r = client.get_transaction_receipt(args.id)
        print("=== Official CBE Digital Receipt ===")
        print(f"Txn ID:    {r.get('transactionId')}")
        print(f"Reference: {r.get('reference')}")
        print(f"Payer:     {r.get('payer')}")
        print(f"Payee:     {r.get('payee')}")
        print(f"Amount:    {r.get('amount'):,.2f} ETB")
        print(f"Date:      {r.get('paymentDate')}")
        print(f"Status:    VERIFIED OFFICIAL")

    elif args.command == "scheduled":
        client = CBEClient()
        scheds = client.get_scheduled_payments()
        print("=== Scheduled Recurring Payments ===")
        for s in scheds:
            print(f"  - [{s['id']}] {s['title']}: {s['amount']:,.2f} ETB to {s['toAccount']} ({s['frequency']}, Next: {s['nextRun']})")

    elif args.command == "split":
        client = CBEClient()
        r = client.initiate_split_payment(args.amount, args.with_users, args.reason)
        print(f"[OK] Split Bill initiated! ID: {r.get('splitId')}")
        print(f"Total:      {r.get('totalAmount'):,.2f} ETB")
        print(f"Per Person: {r.get('amountPerPerson'):,.2f} ETB")
        print(f"With:       {', '.join(r.get('participants', []))}")

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
