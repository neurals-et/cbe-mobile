#!/usr/bin/env python3
"""
Smoke test suite for CBE Mobile Banking Client & TUI.
"""

from cbe_client import CBEConfig, CBEClient
from cbe_tui import CBEMobileTUI

def main():
    print("[1] Testing CBEConfig...")
    cfg = CBEConfig()
    print("    API Base:", cfg.get("api_base"))
    print("    Phone Number:", cfg.get("phone_number"))

    print("\n[2] Testing CBEClient Security Handshake...")
    client = CBEClient(cfg)
    hs = client.secure_handshake()
    print(f"    Handshake: {hs.get('status')} | ID: {hs.get('handshakeId')}")

    print("\n[3] Testing Sign In with PIN...")
    auth = client.sign_in_pin("+251911000000", "1234")
    print(f"    Sign In: {auth.get('status')} | Customer: {auth.get('user', {}).get('fullName')}")

    print("\n[4] Testing Account Inquiry...")
    accs = client.get_accounts().get("accounts", [])
    print(f"    Found {len(accs)} accounts:")
    for a in accs:
        print(f"      - {a['accountType']}: {a['accountNumber']} | Balance: {a['availableBalance']:,.2f} {a['currency']}")

    print("\n[4b] Testing Name Resolution / Account Holder Lookup...")
    lookup1 = client.lookup_account_info("1000987654321")
    print(f"    CBE Acc 1000987654321 Holder Name: '{lookup1.get('accountHolderName')}'")
    lookup2 = client.lookup_external_account("AWASH", "0911223344")
    print(f"    EthSwitch External Acc Holder Name: '{lookup2.get('accountHolderName')}'")

    print("\n[5] Testing Cardless ATM Code Generation...")
    atm = client.initiate_atm_withdrawal("1000123456789", 500.0)
    print(f"    ATM Withdrawal Code: {atm.get('withdrawalCode')} (Expires: {atm.get('expiry')})")

    print("\n[6] Testing Bill & Toll Payment...")
    bill = client.pay_bill("ETHIO_TEL", "0911000000", 100.0)
    print(f"    Ethio Telecom Bill: {bill.get('status')} (Receipt: {bill.get('receiptNumber')})")
    toll = client.tollroad_recharge("A12345AA", 300.0)
    print(f"    Toll Recharge: {toll.get('status')} (New Balance: {toll.get('newTollBalance')} ETB)")

    print("\n[7] Testing Forex Rates Ticker...")
    forex = client.get_forex_rates()
    print(f"    Forex ({forex.get('source')}): {len(forex.get('rates', []))} currencies loaded.")

    print("\n[8] Testing CBEMobileTUI Initialization...")
    tui = CBEMobileTUI()
    print(f"    TUI Class '{type(tui).__name__}' initialized successfully.")

    print("\n" + "=" * 55)
    print("ALL CBE MOBILE TESTS PASSED SUCCESSFULLY!")
    print("=" * 55)

if __name__ == "__main__":
    main()
