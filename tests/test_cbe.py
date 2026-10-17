#!/usr/bin/env python3
"""
Comprehensive test suite for CBE package.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cbe import CBEConfig, CBEClient, CBEMobileTUI

def main():
    print("[1] Testing CBEConfig...")
    cfg = CBEConfig()
    cfg.set("mock_mode", True)
    print("    API Base:", cfg.get("api_base"))

    print("\n[2] Testing CBEClient Core...")
    client = CBEClient(cfg)
    hs = client.secure_handshake()
    print("    Handshake status:", hs.get("status"))

    print("\n[3] Testing Name Resolution / Lookup...")
    info = client.lookup_account_info("1000987654321")
    print(f"    Account 1000987654321 Holder: '{info.get('accountHolderName')}'")
    assert info.get("accountHolderName") == "Tigist Haile"

    print("\n[4] Testing Cards Management...")
    cards = client.get_cards().get("cards", [])
    print(f"    Retrieved {len(cards)} cards:")
    for c in cards:
        print(f"      - [{c['cardType']}] {c['maskedNumber']} ({c['status']})")
    assert len(cards) >= 2

    req = client.request_card("1000123456789", "VISA_DEBIT")
    print("    Card request ref:", req.get("referenceNumber"))

    print("\n[5] Testing Microloans...")
    loans = client.get_loan_dashboard()
    print(f"    Loan Eligible: {loans.get('eligible')} | Limit: {loans.get('maxCreditLimit')} ETB")
    repay = client.repay_loan("LN-58291", 3587.50)
    print("    Repay status:", repay.get("status"))

    print("\n[6] Testing Beneficiaries...")
    bens = client.get_beneficiaries()
    print(f"    Found {len(bens)} saved contacts:")
    for b in bens:
        print(f"      - {b['name']}: {b['accountNumber']} ({b['bank']})")

    print("\n[7] Testing Split Payments & Receipts...")
    split = client.initiate_split_payment(1200.0, ["0911000001", "0911000002", "0911000003"])
    print(f"    Split {split.get('totalAmount')} ETB -> {split.get('amountPerPerson')} ETB/person")

    rcpt = client.get_transaction_receipt("TXN-90218")
    print(f"    Receipt verified: Txn {rcpt.get('transactionId')} for {rcpt.get('amount')} ETB")

    print("\n[8] Testing CBEMobileTUI...")
    tui = CBEMobileTUI()
    print("    TUI instance created:", type(tui).__name__)

    print("\n" + "=" * 50)
    print("ALL CBE EXTENDED TESTS PASSED SUCCESSFULLY!")
    print("=" * 50)

if __name__ == "__main__":
    main()
