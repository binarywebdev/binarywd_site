// Показывает sticky CTA после прокрутки за hero, прячет когда форма уже видна.
const cta = document.getElementById('stickyCta');
const form = document.getElementById('start');

if (cta && form) {
  const onScroll = () => {
    const past = window.scrollY > window.innerHeight * 0.7;
    const formTop = form.getBoundingClientRect().top;
    const near = formTop < window.innerHeight * 0.8;
    cta.classList.toggle('show', past && !near);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}
