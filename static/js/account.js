// Account summary and positions
const Account = {
  async refresh() {
    try {
      const r    = await fetch('/api/account');
      const data = await r.json();
      if (data.error) { document.getElementById('account-info').innerHTML = `<p class="empty">${data.error}</p>`; return; }
      const pl = data.unrealized_pl || 0;
      document.getElementById('account-info').innerHTML = `
        <div>Cash: <b>S$${(data.cash || 0).toFixed(2)}</b></div>
        <div>Total Assets: S$${(data.total_assets || 0).toFixed(2)}</div>
        <div>Mkt Value: S$${(data.market_val || 0).toFixed(2)}</div>
        <div>Unrealized P&amp;L: <b class="${pl >= 0 ? 'up' : 'down'}">${pl >= 0 ? '+' : ''}${pl.toFixed(2)}</b></div>`;
    } catch (e) {
      document.getElementById('account-info').innerHTML = '<p class="empty">Connect OpenD to view account</p>';
    }
  },

  renderPositions(positions) {
    const el = document.getElementById('positions-list');
    if (!positions || !positions.length) { el.innerHTML = '<p class="empty">No positions</p>'; return; }
    el.innerHTML = positions.map(p => {
      const pl  = parseFloat(p.pl_val || 0);
      const pct = (parseFloat(p.pl_ratio || 0) * 100).toFixed(2);
      return `<div class="position-row">
        <span>${p.code}</span>
        <span>${p.qty}</span>
        <span>@${parseFloat(p.cost_price || 0).toFixed(3)}</span>
        <span class="${pl >= 0 ? 'up' : 'down'}">${pl >= 0 ? '+' : ''}${pl.toFixed(2)} (${pct}%)</span>
      </div>`;
    }).join('');
  },
};
