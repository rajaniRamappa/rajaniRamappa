// Candlestick chart management
const ChartMgr = {
  chart: null,

  init() {
    const ctx = document.getElementById('price-chart').getContext('2d');
    this.chart = new Chart(ctx, {
      type: 'candlestick',
      data: {
        datasets: [{
          label: '',
          data: [],
          color: { up: '#3fb950', down: '#f85149', unchanged: '#8b949e' },
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label(ctx) {
                const d = ctx.raw;
                return `O:${d.o}  H:${d.h}  L:${d.l}  C:${d.c}`;
              },
            },
          },
        },
        scales: {
          x: {
            type: 'time',
            time: { unit: 'minute', displayFormats: { minute: 'HH:mm' } },
            ticks: { color: '#8b949e', maxTicksLimit: 8 },
            grid: { color: '#21262d' },
          },
          y: {
            position: 'right',
            ticks: { color: '#8b949e' },
            grid: { color: '#21262d' },
          },
        },
      },
    });
  },

  async load(symbol, ktype) {
    try {
      const r = await fetch(`/api/klines/${encodeURIComponent(symbol)}?ktype=${ktype}&num=120`);
      const { data } = await r.json();
      this.chart.data.datasets[0].label = `${symbol} ${ktype}`;
      this.chart.data.datasets[0].data = data.map(d => ({
        x: new Date(d.time_key).getTime(),
        o: d.open, h: d.high, l: d.low, c: d.close,
      }));
      this.chart.update('none');
    } catch (e) { console.error('Failed to load klines', e); }
  },

  onKlineUpdate(msg) {
    if (msg.code !== App.selectedSymbol) return;
    const ktypeMap = { 'K_1M': '1min', 'K_5M': '5min', 'K_15M': '15min' };
    if (ktypeMap[msg.ktype] !== App.selectedKtype) return;
    const ds = this.chart.data.datasets[0];
    const newCandle = {
      x: new Date(msg.time_key).getTime(),
      o: msg.open, h: msg.high, l: msg.low, c: msg.close,
    };
    const last = ds.data[ds.data.length - 1];
    if (last && last.x === newCandle.x) ds.data[ds.data.length - 1] = newCandle;
    else {
      ds.data.push(newCandle);
      if (ds.data.length > 200) ds.data.shift();
    }
    this.chart.update('none');
  },
};

document.addEventListener('DOMContentLoaded', () => ChartMgr.init());
