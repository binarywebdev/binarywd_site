// Точка входа для главной — собирает все инициализаторы клиентского JS.
import { initHeroCanvas } from './hero-canvas';
import { initGlowCursor } from './glow-cursor';
import { initTickerJitter } from './ticker-jitter';
import './contact-form'; // self-registering listener

initHeroCanvas();
initGlowCursor();
initTickerJitter();
