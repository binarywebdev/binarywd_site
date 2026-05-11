// Курсорное glow-пятно: двигает CSS-переменные на .glow за мышью.
export function initGlowCursor() {
  const g = document.querySelector('.glow') as HTMLElement | null;
  if (!g) return;
  document.addEventListener('mousemove', e => {
    g.style.setProperty('--mx', e.clientX + 'px');
    g.style.setProperty('--my', e.clientY + 'px');
  });
}
