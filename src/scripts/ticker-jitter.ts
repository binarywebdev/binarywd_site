// Лёгкое подёргивание цифр в крипто-тикере — раз в 1.8с двигаем цены на ±0.05%.
export function initTickerJitter(intervalMs = 1800) {
  if (!document.querySelector('.ticker')) return;
  setInterval(() => {
    document.querySelectorAll<HTMLElement>('.ticker b').forEach(b => {
      const txt = b.textContent ?? '';
      if (!txt.startsWith('$')) return;
      const n = parseFloat(txt.replace(/[$,]/g, ''));
      const delta = (Math.random() - .5) * n * 0.001;
      const next = n + delta;
      b.textContent = '$' + next.toLocaleString('en-US', { maximumFractionDigits: next > 1000 ? 0 : 2 });
    });
  }, intervalMs);
}
