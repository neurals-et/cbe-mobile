import {
  createCliRenderer,
  BoxRenderable,
  TextRenderable,
  type CliRenderer,
  type KeyEvent
} from "@opentui/core";
import { TerminalSpinner } from "./spinner";
import { CBEApi } from "./api";
import { TrafficHistory } from "./traffic";
import {
  SUPPORTED_EXTERNAL_BANKS,
  type AccountItem,
  type CardItem,
  type ForexItem,
  type WorkspaceMode
} from "./types";

export class CBETUIApp {
  private renderer!: CliRenderer;
  private traffic = new TrafficHistory();
  private api = new CBEApi(this.traffic);

  // State
  private currentMode: WorkspaceMode = 1;
  private showTrafficModal = false;
  private showBankSearchModal = false;
  private showLookupModal = false;
  private showPasswordModal = false;
  private showHelpModal = false;
  private isRefreshing = false;

  // Account Data
  private phoneNumber = "+251911000000";
  private accounts: AccountItem[] = [];
  private cards: CardItem[] = [];
  private forexRates: ForexItem[] = [];

  // Transfer State
  private internalToAccount = "1000987654321";
  private internalHolderName = "Tigist Haile";
  private internalAmount = "500.00";
  private externalBankIndex = 0;
  private externalToAccount = "0911223344";
  private externalAmount = "1000.00";

  // ATM Cardless State
  private atmCode = "582910";
  private atmExpiry = "2 hours";

  // Bill & Toll State
  private selectedBiller = "Ethio Telecom Airtime";
  private billRef = "0911000000";
  private billAmount = "100.00";
  private tollPlate = "A23456AA";

  // UI Renderables
  private rootBox!: BoxRenderable;
  private headerBox!: BoxRenderable;
  private mainFrame!: BoxRenderable;
  private contentBox!: BoxRenderable;
  private footerTabsBox!: BoxRenderable;

  async start() {
    this.renderer = await createCliRenderer({
      exitOnCtrlC: true
    });

    this.setupLayout();
    this.setupKeyBindings();

    await this.loadInitialData();
    this.renderCurrentView();
  }

  async waitForExit(): Promise<void> {
    if (this.renderer) {
      await this.renderer.closed;
    }
  }

  private clearChildren(box: BoxRenderable) {
    if (!box) return;
    const children = [...box.getChildren()];
    for (const child of children) {
      box.remove(child);
    }
  }

  private setupLayout() {
    // 1. Root Container
    this.rootBox = new BoxRenderable(this.renderer, {
      id: "root-container",
      backgroundColor: "#000000",
      flexDirection: "column",
      justifyContent: "space-between",
      alignItems: "center",
      width: "100%",
      height: "100%",
      padding: 1
    });
    this.renderer.root.add(this.rootBox);

    // 2. Top Header Bar
    this.headerBox = new BoxRenderable(this.renderer, {
      id: "header-bar",
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      width: "95%",
      height: 1
    });
    this.rootBox.add(this.headerBox);

    // 3. Main Center Workspace Frame (White border 0.5px #FFFFFF)
    this.mainFrame = new BoxRenderable(this.renderer, {
      id: "main-workspace-frame",
      backgroundColor: "#000000",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      width: "95%",
      flexGrow: 1,
      margin: 0
    });
    this.rootBox.add(this.mainFrame);

    this.contentBox = new BoxRenderable(this.renderer, {
      id: "content-container",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      width: "100%",
      height: "100%"
    });
    this.mainFrame.add(this.contentBox);

    // 4. Footer Tab Bar
    this.footerTabsBox = new BoxRenderable(this.renderer, {
      id: "footer-tabs-bar",
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "center",
      width: "95%",
      height: 3,
      padding: 0
    });
    this.rootBox.add(this.footerTabsBox);
  }

  private setupKeyBindings() {
    this.renderer.keyInput.on("keypress", (event: KeyEvent) => {
      this.handleKeyPress(event);
    });
  }

  private async loadInitialData() {
    this.accounts = await this.api.getAccounts();
    this.cards = await this.api.getCards();
    this.forexRates = await this.api.getForexRates();
  }

  private handleKeyPress(event: KeyEvent) {
    const key = event.name.toLowerCase();

    // Quit
    if (key === "q" && !this.showTrafficModal && !this.showBankSearchModal && !this.showLookupModal && !this.showHelpModal) {
      this.renderer.destroy();
      process.exit(0);
    }

    // Toggle Traffic Modal (Ctrl+R)
    if (event.ctrl && key === "r") {
      this.showTrafficModal = !this.showTrafficModal;
      this.renderCurrentView();
      return;
    }

    // Close Modals with Escape
    if (key === "escape") {
      if (this.showTrafficModal) this.showTrafficModal = false;
      if (this.showBankSearchModal) this.showBankSearchModal = false;
      if (this.showLookupModal) this.showLookupModal = false;
      if (this.showPasswordModal) this.showPasswordModal = false;
      if (this.showHelpModal) this.showHelpModal = false;
      this.renderCurrentView();
      return;
    }

    if (this.showTrafficModal || this.showHelpModal) return;

    if (this.showBankSearchModal) {
      if (key === "up") {
        this.externalBankIndex = Math.max(0, this.externalBankIndex - 1);
        this.renderCurrentView();
      } else if (key === "down") {
        this.externalBankIndex = Math.min(SUPPORTED_EXTERNAL_BANKS.length - 1, this.externalBankIndex + 1);
        this.renderCurrentView();
      } else if (key === "enter") {
        this.showBankSearchModal = false;
        this.renderCurrentView();
      }
      return;
    }

    if (this.showLookupModal) {
      if (key === "enter") {
        this.showLookupModal = false;
        this.renderCurrentView();
      }
      return;
    }

    if (this.showPasswordModal) {
      if (key === "enter") {
        this.showPasswordModal = false;
        this.traffic.record("POST /v1/transfers/internal-a2a", "200", "Transfer completed", {
          to: this.internalToAccount,
          holder: this.internalHolderName,
          amount: this.internalAmount
        });
        this.renderCurrentView();
      }
      return;
    }

    // Workspace Mode Switching [1-6]
    if (["1", "2", "3", "4", "5", "6"].includes(key)) {
      this.currentMode = parseInt(key, 10) as WorkspaceMode;
      this.renderCurrentView();
      return;
    }

    // Reload (r)
    if (key === "r") {
      this.triggerReload();
      return;
    }

    // Lookup shortcut (l)
    if (key === "l") {
      this.showLookupModal = true;
      this.renderCurrentView();
      return;
    }

    // Help (h)
    if (key === "h") {
      this.showHelpModal = !this.showHelpModal;
      this.renderCurrentView();
      return;
    }

    // Mode specific shortcuts
    if (this.currentMode === 2) {
      // Transfer mode
      if (key === "b") {
        this.showBankSearchModal = true;
        this.renderCurrentView();
      } else if (key === "enter") {
        this.showPasswordModal = true;
        this.renderCurrentView();
      }
    } else if (this.currentMode === 3) {
      // ATM code generate
      if (key === "enter" || key === "g") {
        this.api.generateAtmCode("1000123456789", 500).then((res) => {
          this.atmCode = res.code;
          this.atmExpiry = `Valid until ${res.expiry}`;
          this.renderCurrentView();
        });
      }
    }
  }

  private triggerReload() {
    this.isRefreshing = true;
    this.renderCurrentView();

    setTimeout(async () => {
      this.accounts = await this.api.getAccounts();
      this.forexRates = await this.api.getForexRates();
      this.isRefreshing = false;
      this.renderCurrentView();
    }, 600);
  }

  private renderCurrentView() {
    // 1. Top Header Bar
    this.clearChildren(this.headerBox);
    const phoneLabel = new TextRenderable(this.renderer, {
      content: `${this.phoneNumber}  [CBE Mobile]`
    });
    const headerShortcuts = new TextRenderable(this.renderer, {
      content: "q: quit   r: reload   <ctrl-r>: traffic   l: lookup   h: help"
    });
    this.headerBox.add(phoneLabel);
    this.headerBox.add(headerShortcuts);

    // 2. Main Center Frame Content
    this.clearChildren(this.contentBox);

    if (this.currentMode === 1) {
      this.renderBalanceView();
    } else if (this.currentMode === 2) {
      this.renderTransfersView();
    } else if (this.currentMode === 3) {
      this.renderAtmView();
    } else if (this.currentMode === 4) {
      this.renderBillTollView();
    } else if (this.currentMode === 5) {
      this.renderForexView();
    } else if (this.currentMode === 6) {
      this.renderCardsView();
    }

    // 3. Footer Tab Bar
    this.renderFooterTabs();

    // 4. Modals / Overlays
    if (this.showTrafficModal) {
      this.renderTrafficModal();
    } else if (this.showBankSearchModal) {
      this.renderBankSearchModal();
    } else if (this.showLookupModal) {
      this.renderLookupModal();
    } else if (this.showPasswordModal) {
      this.renderPasswordModal();
    } else if (this.showHelpModal) {
      this.renderHelpModal();
    }
  }

  // ---------------- VIEW RENDERERS ----------------

  private renderBalanceView() {
    const container = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      gap: 1,
      width: "80%"
    });

    const acc1 = this.accounts[0] || { availableBalance: 45280.50, accountNumber: "1000123456789" };
    const acc2 = this.accounts[1] || { availableBalance: 128400.00, accountNumber: "1000998877665" };
    const total = acc1.availableBalance + acc2.availableBalance;

    container.add(new TextRenderable(this.renderer, {
      content: `Primary Savings (${acc1.accountNumber}): ${acc1.availableBalance.toLocaleString()} ETB`
    }));

    container.add(new TextRenderable(this.renderer, {
      content: `Current Account (${acc2.accountNumber}): ${acc2.availableBalance.toLocaleString()} ETB`
    }));

    // Highlighted Total Balance Pill (#353535)
    const totalPill = new BoxRenderable(this.renderer, {
      backgroundColor: "#353535",
      padding: 0,
      width: 32,
      height: 1,
      justifyContent: "center",
      alignItems: "center"
    });
    totalPill.add(new TextRenderable(this.renderer, {
      content: `total balance ${total.toLocaleString()} ETB`
    }));
    container.add(totalPill);

    if (this.isRefreshing) {
      const spinner = new TerminalSpinner(this.renderer, "Refreshing live balances...");
      spinner.start();
      container.add(spinner.renderable);
    }

    this.contentBox.add(container);
  }

  private renderTransfersView() {
    const container = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      gap: 1,
      width: "75%"
    });

    // Internal Transfer Box (Rectangle 7)
    const internalBox = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "cbe transfer (a2a)",
      flexDirection: "column",
      padding: 1,
      width: "100%"
    });
    internalBox.add(new TextRenderable(this.renderer, { content: `account = ${this.internalToAccount}` }));
    internalBox.add(new TextRenderable(this.renderer, { content: `recipient name: [ ${this.internalHolderName} ]` }));
    internalBox.add(new TextRenderable(this.renderer, { content: `amount = ${this.internalAmount} ETB` }));

    // Other Banks Box (Rectangle 6)
    const bank = SUPPORTED_EXTERNAL_BANKS[this.externalBankIndex];
    const externalBox = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "other banks (ethswitch)",
      flexDirection: "column",
      padding: 1,
      width: "100%"
    });
    externalBox.add(new TextRenderable(this.renderer, { content: `bank < ${bank.name} >  [Press 'b' to change]` }));
    externalBox.add(new TextRenderable(this.renderer, { content: `account = ${this.externalToAccount}` }));
    externalBox.add(new TextRenderable(this.renderer, { content: `amount = ${this.externalAmount} ETB` }));

    container.add(internalBox);
    container.add(externalBox);
    container.add(new TextRenderable(this.renderer, { content: "[enter] confirm payment   [l] lookup name" }));
    this.contentBox.add(container);
  }

  private renderAtmView() {
    const card = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "cardless atm cash-out",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      width: "65%",
      padding: 1,
      gap: 1
    });

    card.add(new TextRenderable(this.renderer, { content: "Withdraw cash from any CBE ATM without a physical card." }));

    // 6-digit code box (Frame 7 style)
    const codePill = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      width: "70%",
      padding: 1,
      justifyContent: "center",
      alignItems: "center"
    });
    codePill.add(new TextRenderable(this.renderer, {
      content: `ATM CODE = [ ${this.atmCode} ]`
    }));

    // Green alert badge
    const alertBadge = new BoxRenderable(this.renderer, {
      backgroundColor: "#353535",
      padding: 0,
      height: 1
    });
    alertBadge.add(new TextRenderable(this.renderer, {
      content: `[the code is active: ${this.atmExpiry}]`
    }));

    card.add(codePill);
    card.add(alertBadge);
    card.add(new TextRenderable(this.renderer, { content: "[g] or [enter] to generate new 6-digit code" }));

    this.contentBox.add(card);
  }

  private renderBillTollView() {
    const card = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      gap: 1,
      width: "75%"
    });

    // Bill Pay Box
    const billBox = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "utility bill payments",
      flexDirection: "column",
      padding: 1,
      width: "100%"
    });
    billBox.add(new TextRenderable(this.renderer, { content: `biller: ${this.selectedBiller}` }));
    billBox.add(new TextRenderable(this.renderer, { content: `reference = ${this.billRef}` }));
    billBox.add(new TextRenderable(this.renderer, { content: `amount = ${this.billAmount} ETB` }));

    // Toll Road Box
    const tollBox = new BoxRenderable(this.renderer, {
      border: true,
      borderColor: "#4C4C4C",
      borderStyle: "single",
      title: "expressway toll road top-up",
      flexDirection: "column",
      padding: 1,
      width: "100%"
    });
    tollBox.add(new TextRenderable(this.renderer, { content: `plate number = ${this.tollPlate}` }));
    tollBox.add(new TextRenderable(this.renderer, { content: "amount = 300.00 ETB" }));

    const sendBtn = new BoxRenderable(this.renderer, {
      backgroundColor: "#353535",
      width: 18,
      height: 1,
      justifyContent: "center",
      alignItems: "center"
    });
    sendBtn.add(new TextRenderable(this.renderer, { content: "[ pay bill / toll ]" }));

    card.add(billBox);
    card.add(tollBox);
    card.add(sendBtn);
    this.contentBox.add(card);
  }

  private renderForexView() {
    const box = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      width: "80%",
      gap: 1
    });

    box.add(new TextRenderable(this.renderer, {
      content: `── CBE Daily Forex Exchange Rates (Live Market Feed) ──`
    }));

    const list = new BoxRenderable(this.renderer, { flexDirection: "column" });
    this.forexRates.slice(0, 6).forEach((r) => {
      list.add(new TextRenderable(this.renderer, {
        content: `• ${r.currency.padEnd(5, " ")} | Buying: ${r.buying.toFixed(2).padStart(7, " ")} ETB | Selling: ${r.selling.toFixed(2).padStart(7, " ")} ETB | ${r.name}`
      }));
    });

    box.add(list);
    box.add(new TextRenderable(this.renderer, { content: "Press 'r' to re-fetch latest daily rates from CBE servers." }));
    this.contentBox.add(box);
  }

  private renderCardsView() {
    const box = new BoxRenderable(this.renderer, {
      flexDirection: "column",
      width: "75%",
      gap: 1
    });

    box.add(new TextRenderable(this.renderer, { content: "── Linked CBE Debit Cards ──" }));
    this.cards.forEach((c) => {
      box.add(new TextRenderable(this.renderer, {
        content: `• [${c.cardType}] ${c.maskedNumber} (Exp: ${c.expiry}) - ${c.status}`
      }));
    });

    box.add(new TextRenderable(this.renderer, { content: "\n── CBE Digital Microloan (Credit) ──" }));
    box.add(new TextRenderable(this.renderer, { content: "• Status: ELIGIBLE | Credit Limit: 20,000.00 ETB" }));
    box.add(new TextRenderable(this.renderer, { content: "• Active Loan: LN-58291 | 3,587.50 ETB due soon" }));

    this.contentBox.add(box);
  }

  // ---------------- MODALS & OVERLAYS ----------------

  private renderTrafficModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#1E1E1E",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      flexDirection: "column",
      width: "85%",
      height: "80%",
      position: "absolute",
      padding: 1
    });

    modal.add(new TextRenderable(this.renderer, { content: "[Ctrl-R] Close   (Escape also closes)" }));
    modal.add(new TextRenderable(this.renderer, { content: this.traffic.formatOutput() }));
    this.rootBox.add(modal);
  }

  private renderBankSearchModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#0D0D0D",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      flexDirection: "column",
      width: "70%",
      height: "75%",
      position: "absolute",
      padding: 1,
      gap: 1
    });

    modal.add(new TextRenderable(this.renderer, { content: "esc: quit   [Up/Down + Enter to select bank]" }));
    modal.add(new TextRenderable(this.renderer, { content: "type to search: [ EthSwitch Interbank ]" }));

    const list = new BoxRenderable(this.renderer, { flexDirection: "column" });
    SUPPORTED_EXTERNAL_BANKS.forEach((b, idx) => {
      const isSel = idx === this.externalBankIndex;
      list.add(new TextRenderable(this.renderer, {
        content: isSel ? `> ${b.name} (${b.code}) <` : `  ${b.name} (${b.code})`
      }));
    });
    modal.add(list);
    this.rootBox.add(modal);
  }

  private renderLookupModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#0D0D0D",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "account name resolution",
      width: "60%",
      height: "45%",
      position: "absolute",
      justifyContent: "center",
      alignItems: "center",
      padding: 1,
      gap: 1
    });

    modal.add(new TextRenderable(this.renderer, { content: `CBE Account: ${this.internalToAccount}` }));
    modal.add(new TextRenderable(this.renderer, { content: `Resolved Name: ${this.internalHolderName}` }));
    modal.add(new TextRenderable(this.renderer, { content: "Status: ACTIVE & VERIFIED" }));
    modal.add(new TextRenderable(this.renderer, { content: "[enter] or [escape] to close" }));
    this.rootBox.add(modal);
  }

  private renderPasswordModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#0D0D0D",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      width: "50%",
      height: "30%",
      position: "absolute",
      justifyContent: "center",
      alignItems: "center",
      gap: 1
    });
    modal.add(new TextRenderable(this.renderer, { content: "Password [ ******* ]" }));
    modal.add(new TextRenderable(this.renderer, { content: "[enter] confirm transfer   esc: cancel" }));
    this.rootBox.add(modal);
  }

  private renderHelpModal() {
    const modal = new BoxRenderable(this.renderer, {
      backgroundColor: "#0D0D0D",
      border: true,
      borderColor: "#FFFFFF",
      borderStyle: "single",
      title: "CBE Terminal Help & Shortcuts",
      width: "65%",
      height: "55%",
      position: "absolute",
      padding: 1,
      gap: 1
    });

    modal.add(new TextRenderable(this.renderer, { content: "q: Quit application" }));
    modal.add(new TextRenderable(this.renderer, { content: "r: Reload balances & exchange rates (with spinner)" }));
    modal.add(new TextRenderable(this.renderer, { content: "<ctrl-r>: Toggle live API traffic history overlay" }));
    modal.add(new TextRenderable(this.renderer, { content: "l: Instant recipient account name lookup" }));
    modal.add(new TextRenderable(this.renderer, { content: "b: Bank search popup (on Transfers workspace)" }));
    modal.add(new TextRenderable(this.renderer, { content: "1 - 6: Switch workspace modes" }));
    modal.add(new TextRenderable(this.renderer, { content: "Escape: Close any open popup / modal" }));
    modal.add(new TextRenderable(this.renderer, { content: "\nPress Escape to close this help dialog" }));
    this.rootBox.add(modal);
  }

  // ---------------- FOOTER TABS ----------------

  private renderFooterTabs() {
    this.clearChildren(this.footerTabsBox);

    const tabsRow = new BoxRenderable(this.renderer, {
      flexDirection: "row",
      gap: 1
    });

    const modes: { id: WorkspaceMode; label: string }[] = [
      { id: 1, label: "1: balance" },
      { id: 2, label: "2: transfer" },
      { id: 3, label: "3: cardless atm" },
      { id: 4, label: "4: bill & toll" },
      { id: 5, label: "5: forex" },
      { id: 6, label: "6: cards/loans" }
    ];

    for (const m of modes) {
      const isActive = m.id === this.currentMode;
      const tabBox = new BoxRenderable(this.renderer, {
        backgroundColor: isActive ? "#353535" : undefined,
        padding: 0,
        height: 1
      });
      tabBox.add(new TextRenderable(this.renderer, { content: ` ${m.label} ` }));
      tabsRow.add(tabBox);
    }

    const helperText = new TextRenderable(this.renderer, {
      content: "[1-6] to change workspace (mode)"
    });

    this.footerTabsBox.add(tabsRow);
    this.footerTabsBox.add(helperText);
  }
}
