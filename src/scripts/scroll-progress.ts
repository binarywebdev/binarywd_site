// Прогресс-полоска вверху страницы — ширина = доля прокрутки.
export function initScrollProgress(barId = 'progress') {
  const p = document.getElementById(barId) as HTMLElement | null;
  if (!p) return;
  const update = () => {
    const h = document.documentElement;
    const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
    p.style.width = pct + '%';
  };
  window.addEventListener('scroll', update, { passive: true });
  update();
}

initScrollProgress();
