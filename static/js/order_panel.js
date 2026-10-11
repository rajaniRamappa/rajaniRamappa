// Order entry panel and open orders list
const OrderPanel = {
  setSymbol(symbol) {
    const el = document.getElementById('order-code-display');
    if (el) el.textContent = symbol;
  },
};

const Orders = {
  async refresh() {
    try {
      const [oRes, pRes] = await Promise.all([fetch('/api/orders'), fetch('/api/positions')]);
      const { orders }    = await oRes.json();
      const { positions } = await pRes.json();
      this.renderOrders(orders);
      Account.renderPositions(positions);
    } catch (e) { console.error('Failed to refresh orders', e); }
  },

  renderOrders(orders) {
    const el = document.getElementById('orders-list');
    if (!orders || !orders.length) { el.innerHTML = '<p class="empty">No open orders</p>'; return; }
    el.innerHTML = orders.map(o => {
      const side = String(o.trd_side || '').includes('BUY') ? 'BUY' : 'SELL';
      const cls  = side === 'BUY' ? 'up' : 'down';
      return `<div class="order-row">
        <span class="${cls}">${side}</span>
        <span>${o.code}</span>
        <span>${o.qty}@${parseFloat(o.price).toFixed(3)}</span>
        <span class="status">${o.order_status || ''}</span>
        <button class="btn-danger btn-sm" onclick="cancelOrder('${o.order_id}')">Cancel</button>
      </div>`;
    }).join('');
  },

  onUpdate(_msg) { this.refresh(); },
};

async function placeOrder() {
  if (!App.tradeUnlocked) { alert('Please unlock trading first.'); return; }
  const code = App.selectedSymbol;
  if (!code) { alert('Select a symbol from the watchlist first.'); return; }
  const side  = document.getElementById('order-side').value;
  const otype = document.getElementById('order-type').value;
  const qty   = parseInt(document.getElementById('order-qty').value, 10);
  const priceRaw = parseFloat(document.getElementById('order-price').value);
  const price = isNaN(priceRaw) ? null : priceRaw;
  if (!qty || qty <= 0) { alert('Enter a valid quantity.'); return; }
  if (otype === 'LIMIT' && !price) { alert('Enter a price for limit orders.'); return; }
  try {
    const r = await fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, side, order_type: otype, qty, price }),
    });
    const result = await r.json();
    if (result.error) alert(`Order failed: ${result.error}`);
    else { alert(`Order placed! ID: ${result.order_id}`); Orders.refresh(); }
  } catch (e) { alert('Network error placing order.'); }
}

async function cancelOrder(orderId) {
  if (!confirm(`Cancel order ${orderId}?`)) return;
  try {
    await fetch(`/api/order/${encodeURIComponent(orderId)}`, { method: 'DELETE' });
    Orders.refresh();
  } catch (e) { alert('Failed to cancel order.'); }
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('order-type').addEventListener('change', function () {
    document.getElementById('order-price').disabled = this.value === 'MARKET';
    if (this.value === 'MARKET') document.getElementById('order-price').value = '';
  });
});
