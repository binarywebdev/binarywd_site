// Hero canvas — свечной график, drifting orbs, тонкая сетка.
// Стартует если на странице есть #heroCanvas, иначе тихо выходит.

export function initHeroCanvas() {
  const cv = document.getElementById('heroCanvas') as HTMLCanvasElement | null;
  if (!cv) return;
  const ctx = cv.getContext('2d');
  if (!ctx) return;

  let W = 0, H = 0, dpr = 1;
  const candles: { open: number; close: number; high: number; low: number }[] = [];
  const orbs = [
    { x: .2,  y: .4,  r: 280, color: '214,255,61',  vx:  .00012, vy:  .00008, a: .10 },
    { x: .75, y: .65, r: 340, color: '255,90,31',   vx: -.00009, vy:  .00011, a: .07 },
    { x: .55, y: .25, r: 220, color: '120,180,255', vx:  .0001,  vy: -.00007, a: .05 },
  ];
  let lastPrice = 100, scrollX = 0, t = 0;
  let rangeMin: number | null = null, rangeMax: number | null = null;
  const CW = 14, GAP = 4;

  const resize = () => {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    const rect = cv.getBoundingClientRect();
    W = rect.width; H = rect.height;
    cv.width = W * dpr; cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  resize();
  new ResizeObserver(resize).observe(cv);

  // seed
  const count = Math.ceil(W / (CW + GAP)) + 20;
  for (let i = 0; i < count; i++) {
    const open = lastPrice;
    const close = open + (Math.random() - .48) * 4;
    candles.push({
      open, close,
      high: Math.max(open, close) + Math.random() * 2.5,
      low:  Math.min(open, close) - Math.random() * 2.5,
    });
    lastPrice = close;
  }

  const tick = () => {
    t += 1;
    ctx.clearRect(0, 0, W, H);

    // grid
    ctx.strokeStyle = 'rgba(255,255,255,0.025)';
    ctx.lineWidth = 1;
    const gs = 60;
    const offset = (t * .2) % gs;
    for (let x = -offset; x < W; x += gs) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = -offset; y < H; y += gs) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    // orbs
    orbs.forEach(o => {
      o.x += o.vx; o.y += o.vy;
      if (o.x < .05 || o.x > .95) o.vx *= -1;
      if (o.y < .1  || o.y > .9)  o.vy *= -1;
      const cx = o.x * W, cy = o.y * H;
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, o.r);
      g.addColorStop(0, `rgba(${o.color},${o.a})`);
      g.addColorStop(1, `rgba(${o.color},0)`);
      ctx.fillStyle = g;
      ctx.fillRect(cx - o.r, cy - o.r, o.r * 2, o.r * 2);
    });

    // shift candles right→left
    scrollX += .35;
    if (scrollX >= CW + GAP) {
      scrollX -= (CW + GAP);
      candles.shift();
      const open = lastPrice;
      const close = open + (Math.random() - .48) * 4;
      candles.push({
        open, close,
        high: Math.max(open, close) + Math.random() * 2.5,
        low:  Math.min(open, close) - Math.random() * 2.5,
      });
      lastPrice = close;
    }

    // y-scale eased
    let min = Infinity, max = -Infinity;
    candles.forEach(c => { if (c.low < min) min = c.low; if (c.high > max) max = c.high; });
    const pad = (max - min) * .15;
    const tMin = min - pad, tMax = max + pad;
    if (rangeMin === null) { rangeMin = tMin; rangeMax = tMax; }
    else { rangeMin += (tMin - rangeMin) * .04; rangeMax! += (tMax - rangeMax!) * .04; }
    const baseY = H * .55, chartH = H * .40;
    const py = (p: number) => baseY + chartH - ((p - rangeMin!) / (rangeMax! - rangeMin!)) * chartH;

    // candles
    candles.forEach((c, i) => {
      const fromRight = candles.length - 1 - i;
      const x = W - 40 - scrollX - fromRight * (CW + GAP);
      if (x < -CW || x > W + CW) return;
      const up = c.close >= c.open;
      const color = up ? 'rgba(214,255,61,.55)' : 'rgba(255,90,31,.55)';
      ctx.strokeStyle = color;
      ctx.fillStyle = up ? 'rgba(214,255,61,.18)' : 'rgba(255,90,31,.18)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + CW / 2, py(c.high));
      ctx.lineTo(x + CW / 2, py(c.low));
      ctx.stroke();
      const yO = py(c.open), yC = py(c.close);
      const top = Math.min(yO, yC), bh = Math.max(2, Math.abs(yC - yO));
      ctx.fillRect(x, top, CW, bh);
      ctx.strokeRect(x + .5, top + .5, CW - 1, bh - 1);
    });

    // MA(8) overlay
    ctx.strokeStyle = 'rgba(244,241,234,0.35)';
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    const period = 8;
    for (let i = period; i < candles.length; i++) {
      let sum = 0;
      for (let j = i - period; j < i; j++) sum += candles[j].close;
      const avg = sum / period;
      const fromRight = candles.length - 1 - i;
      const x = W - 40 - scrollX - fromRight * (CW + GAP) + CW / 2;
      const y = py(avg);
      if (i === period) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();

    requestAnimationFrame(tick);
  };
  tick();
}
