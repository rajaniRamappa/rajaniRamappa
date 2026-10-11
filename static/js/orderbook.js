// Live OHLCV bar for the selected symbol
const Orderbook = {
  update(msg) {
    if (msg.code !== App.selectedSymbol) return;
    const sign = msg.change_pct >= 0 ? '+' : '';
    const cls  = msg.change_pct >= 0 ? 'up' : 'down';
    document.getElementById('bid-ask-panel').innerHTML = `
      <span>Last: <b>${msg.last_price.toFixed(3)}</b></span>
      <span class="${cls}"><b>${sign}${msg.change_pct.toFixed(2)}%</b></span>
      <span>Open: ${msg.open_price.toFixed(3)}</span>
      <span>High: <span class="up">${msg.high_price.toFixed(3)}</span></span>
      <span>Low:  <span class="down">${msg.low_price.toFixed(3)}</span></span>
      <span>Prev: ${msg.prev_close.toFixed(3)}</span>
      <span>Vol: ${(msg.volume / 1000).toFixed(1)}K</span>`;
  },
};
