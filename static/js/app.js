// Global application state and WebSocket management
const App = {
  ws: null,
  selectedSymbol: null,
  selectedKtype: '1min',
  watchlist: [],
  tradeUnlocked: false,

  init() {
    this.connectWS();
    this.updateMarketStatus();
    setInterval(() => this.updateMarketStatus(), 60000);
  },

  connectWS() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    this.ws = new WebSocket(`${proto}://${location.host}/ws`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.loadInitialData();
    };

    this.ws.onmessage = (evt) => {
      try { this.handleMessage(JSON.parse(evt.data)); }
      catch (e) { console.error('WS parse error', e); }
    };

    this.ws.onclose = () => {
      console.warn('WS disconnected, reconnecting in 3s...');
      setTimeout(() => this.connectWS(), 3000);
    };
  },

  send(cmd) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN)
      this.ws.send(JSON.stringify(cmd));
  },

  handleMessage(msg) {
    switch (msg.type) {
      case 'quote':           Watchlist.updateQuote(msg); Orderbook.update(msg); AlertMgr.onQuote(msg); break;
      case 'kline':           ChartMgr.onKlineUpdate(msg); break;
      case 'order_update':    Orders.onUpdate(msg); break;
      case 'alert_triggered': AlertMgr.onTriggered(msg); break;
      case 'unlock_result':   handleUnlockResult(msg); break;
      case 'watchlist_update':Watchlist.onAdded(msg); break;
    }
  },

  async loadInitialData() {
    try {
      const r = await fetch('/api/symbols');
      const { symbols } = await r.json();
      symbols.forEach(s => Watchlist.addRow(s));
      if (symbols.length > 0) this.selectSymbol(symbols[0]);
    } catch (e) { console.error('Failed to load symbols', e); }
    Account.refresh();
    Orders.refresh();
  },

  selectSymbol(symbol) {
    this.selectedSymbol = symbol;
    document.getElementById('selected-symbol').textContent = symbol;
    document.querySelectorAll('.watchlist-row').forEach(el =>
      el.classList.toggle('selected', el.dataset.symbol === symbol)
    );
    ChartMgr.load(symbol, this.selectedKtype);
    OrderPanel.setSymbol(symbol);
  },

  updateMarketStatus() {
    // SGX: 09:00-17:00 SGT (UTC+8), Mon-Fri
    const now = new Date();
    const utcMin = now.getUTCHours() * 60 + now.getUTCMinutes();
    const sgMin  = (utcMin + 8 * 60) % (24 * 60);
    const day    = (now.getUTCDay() + (utcMin + 480 >= 1440 ? 1 : 0)) % 7;
    const isOpen = day >= 1 && day <= 5 && sgMin >= 540 && sgMin < 1020;
    const el = document.getElementById('market-status');
    if (el) {
      el.textContent = isOpen ? '● SGX OPEN' : '○ SGX CLOSED';
      el.className   = isOpen ? 'open' : 'closed';
    }
  },
};

function unlockTrade() {
  const pw = document.getElementById('trade-password').value;
  if (!pw) return;
  App.send({ cmd: 'unlock_trade', password: pw });
  document.getElementById('trade-password').value = '';
}

function handleUnlockResult(msg) {
  App.tradeUnlocked = msg.ok;
  const el = document.getElementById('unlock-status');
  if (msg.ok) {
    el.textContent = '✓ Trading UNLOCKED';
    el.className = '';
    document.getElementById('unlock-section').querySelector('button').textContent = 'Unlocked';
  } else {
    el.textContent = '✗ ' + (msg.msg || 'Failed');
    el.className = 'error';
  }
}

function setKtype(kt) {
  App.selectedKtype = kt;
  document.querySelectorAll('.ktype-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.kt === kt)
  );
  if (App.selectedSymbol) ChartMgr.load(App.selectedSymbol, kt);
}

document.addEventListener('DOMContentLoaded', () => App.init());
