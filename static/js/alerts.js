// Price alert management
const AlertMgr = {
  onQuote(_msg) {},  // evaluation is server-side

  onTriggered(msg) {
    const body  = `${msg.code} is now ${msg.last_price} (threshold: ${msg.threshold})`;
    const title = `Alert: ${msg.label || msg.code}`;
    if (Notification.permission === 'granted') new Notification(title, { body });
    else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then(p => { if (p === 'granted') new Notification(title, { body }); });
    }
    const div = document.createElement('div');
    div.className = 'alert-triggered';
    div.textContent = `[${new Date().toLocaleTimeString()}] ${title} — ${body}`;
    document.getElementById('alerts-list').prepend(div);
  },

  addAlert() {
    const code      = document.getElementById('alert-code').value.trim().toUpperCase();
    const direction = document.getElementById('alert-dir').value;
    const threshold = parseFloat(document.getElementById('alert-threshold').value);
    const label     = document.getElementById('alert-label').value.trim();
    if (!code || isNaN(threshold)) { alert('Enter a symbol code and threshold price.'); return; }
    App.send({ cmd: 'add_alert', code, direction, threshold, label });
    const div = document.createElement('div');
    div.className = 'alert-rule';
    div.innerHTML = `<span>${code}</span><span>${direction}</span><span>${threshold}</span><span style="color:var(--muted)">${label}</span>`;
    document.getElementById('active-alerts').prepend(div);
    document.getElementById('alert-code').value = '';
    document.getElementById('alert-threshold').value = '';
    document.getElementById('alert-label').value = '';
  },
};

document.addEventListener('DOMContentLoaded', () => {
  if (Notification && Notification.permission === 'default') Notification.requestPermission();
  document.getElementById('alert-code').addEventListener('focus', function () {
    if (!this.value && App.selectedSymbol) this.value = App.selectedSymbol;
  });
});
