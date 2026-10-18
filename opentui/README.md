# cbe-tui

> High-performance terminal interface for **Commercial Bank of Ethiopia (CBE Mobile)** built with [OpenTUI](https://github.com/opentui/opentui) and [Bun](https://bun.sh).

Strictly engineered according to modern minimal terminal UI specifications:
- **Pure Black Canvas (`#000000`)** with clean white single-line borders (`#FFFFFF`)
- **Top Bar**: User identity (`+251911000000`) and quick shortcuts (`q: quit   r: reload   <ctrl-r>: traffic   l: lookup   h: help`)
- **Main Viewport**: Single-box framing dynamic workspace content
- **Footer Tabs**: 6 instant workspace modes (`[1-6]`) with `#353535` active pills

---

## Workspaces

1. **`1: balance`**: Primary Savings & Current accounts, total balance badge, and live refresh spinner.
2. **`2: transfer`**: Internal CBE Account-to-Account (`A2A`) with live name lookup, and EthSwitch interbank transfer with searchable destination bank selector (`b`).
3. **`3: cardless atm`**: Generate 6-digit ATM cash withdrawal authorization codes valid for 2 hours at any CBE ATM.
4. **`4: bill & toll`**: Utility bill settlements (Telecom, Water, Power) and Expressway Toll Pass top-ups.
5. **`5: forex`**: CBE Daily Exchange Rates live feed directly from CBE servers (USD, EUR, GBP, AED, SAR, CAD).
6. **`6: cards/loans`**: Linked debit cards management and CBE digital microloan eligibility & status.

---

## Popups & Overlays

- **`<Ctrl-R>`**: Live API traffic history inspector showing network requests, status codes, and payloads.
- **`l`**: Recipient account name resolution dialog.
- **`b`**: Searchable EthSwitch interbank directory popup.
- **`h`**: Keyboard shortcuts and help modal.
- **`Escape`**: Dismisses any active overlay.

---

## Installation & Running

Ensure [Bun](https://bun.sh) is installed on your system:

```bash
cd cbe-tui
bun install
bun run start
```
