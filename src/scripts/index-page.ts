// Точка входа для главной — собирает три independent-инита.
import { initHeroCanvas } from './hero-canvas';
import { initGlowCursor } from './glow-cursor';
import { initTickerJitter } from './ticker-jitter';

initHeroCanvas();
initGlowCursor();
initTickerJitter();
