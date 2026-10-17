#!/usr/bin/env python3
"""
Test query demonstration for CBE Mobile Client.
- Validates account lookup format rules (13-digit CBE account validation)
- Tests live connection to CBE public exchange rates
- Demonstrates account resolution workflow
"""

import sys
from cbe_client import CBEClient, CBEConfig

def test_account_query():
    print("=== Testing CBE Account Query & Validation ===")
    client = CBEClient()
    
    # 1. Test live public query to CBE servers
    print("[1] Querying CBE public endpoint (Daily Exchange Rates)...")
    forex = client.get_forex_rates()
    rates = forex.get("rates", [])
    print(f"    Source: {forex.get('source')} | Currencies received: {len(rates)}")
    if rates:
        for r in rates[:3]:
            print(f"    {r.get('currency')}: Buying = {r.get('buying')} ETB, Selling = {r.get('selling')} ETB")

    # 2. Test account inquiry resolution
    print("\n[2] Testing Account Name Resolution query...")
    test_accounts = [
        "1000123456789",  # Known Primary
        "1000987654321",  # Known Secondary
        "1000554433221",  # Known Dawit
        "1000999999999",  # Arbitrary account
    ]
    
    for acc in test_accounts:
        info = client.lookup_account_info(acc)
        print(f"    Query: Account '{acc}' -> Resolved Holder: '{info.get('accountHolderName')}' ({info.get('status')})")

    # 3. Test external bank lookup query
    print("\n[3] Testing External Bank Inquiry query (EthSwitch)...")
    ext_query = client.lookup_external_account("DASHEN", "1000445566")
    print(f"    Query: Bank '{ext_query.get('bankCode')}', Acc '{ext_query.get('accountNumber')}' -> Holder: '{ext_query.get('accountHolderName')}'")

    print("\n=== Test Queries Completed Successfully ===")

if __name__ == "__main__":
    test_account_query()
