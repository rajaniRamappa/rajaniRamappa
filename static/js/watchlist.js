// Watchlist panel
const Watchlist = {
  addRow(symbol) {
    if (App.watchlist.includes(symbol)) return;
    App.watchlist.push(symbol);
    const id  = symbol.replace('.', '-');
    const div = document.createElement('div');
    div.className = 'watchlist-row';
    div.dataset.symbol = symbol;
    div.onclick = () => App.selectSymbol(symbol);
    div.innerHTML = `
      <span class="wl-symbol">${symbol}</span>
      <span class="wl-price"  id="wlp-${id}">--</span>
      <span class="wl-change" id="wlc-${id}">--</span>
      <button class="wl-remove btn-sm" title="Remove"
        onclick="event.stopPropagation();Watchlist.remove('${symbol}')">&#x2715;</button>`;
    document.getElementById('watchlist-items').appendChild(div);
  },

  remove(symbol) {
    App.send({ cmd: 'remove_watchlist', symbol });
    App.watchlist = App.watchlist.filter(s => s !== symbol);
    document.querySelectorAll(`.watchlist-row[data-symbol="${symbol}"]`).forEach(el => el.remove());
    if (App.selectedSymbol === symbol) {
      App.selectedSymbol = null;
      document.getElementById('selected-symbol').textContent = '-';
    }
  },

  updateQuote(msg) {
    const id = msg.code.replace('.', '-');
    const priceEl = document.getElementById(`wlp-${id}`);
    const chgEl   = document.getElementById(`wlc-${id}`);
    if (!priceEl) return;
    priceEl.textContent = msg.last_price.toFixed(3);
    const chg = msg.change_pct;
    chgEl.textContent = `${chg >= 0 ? '+' : ''}${chg.toFixed(2)}%`;
    chgEl.className   = `wl-change ${chg >= 0 ? 'up' : 'down'}`;
  },

  onAdded(msg) {
    if (msg.ok) this.addRow(msg.symbol);
    else alert(`Could not add ${msg.symbol}: ${msg.msg}`);
  },
};

function addToWatchlist() {
  const input = document.getElementById('symbol-input');
  const sym   = input.value.trim().toUpperCase();
  if (!sym) return;
  App.send({ cmd: 'add_watchlist', symbol: sym });
  input.value = '';
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('symbol-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') addToWatchlist();
  });
});
