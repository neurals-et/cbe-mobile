#!/usr/bin/env python3
"""
Test suite for CBE package.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cbe import CBEConfig, CBEClient, CBEMobileTUI

def main():
    print("[1] Testing CBEConfig...")
    cfg = CBEConfig()
    print("    API Base:", cfg.get("api_base"))

    print("[2] Testing CBEClient...")
    client = CBEClient(cfg)
    hs = client.secure_handshake()
    print("    Handshake status:", hs.get("status"))

    print("[3] Testing Name Resolution / Lookup...")
    info = client.lookup_account_info("1000987654321")
    print(f"    Account 1000987654321 Holder: '{info.get('accountHolderName')}'")
    assert info.get("accountHolderName") == "Tigist Haile"

    print("[4] Testing CBEMobileTUI...")
    tui = CBEMobileTUI()
    print("    TUI instance created:", type(tui).__name__)

    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
