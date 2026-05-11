// Отправка брифа в PocketBase. Без зависимостей — pb-клиент импортируем напрямую.
import { submitBrief } from '~/lib/pocketbase';
import type { Locale } from '~/i18n/utils';

const form = document.querySelector<HTMLFormElement>('form.cf-right');
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const btn = form.querySelector<HTMLButtonElement>('.cf-send');
    const legal = form.querySelector<HTMLElement>('.cf-submit .legal');
    if (!btn) return;

    // соберём данные
    const inputs = form.querySelectorAll<HTMLInputElement>('input[type="text"]');
    const story = form.querySelector<HTMLTextAreaElement>('textarea');
    const checked = Array.from(form.querySelectorAll<HTMLInputElement>('.cf-services input:checked'))
      .map(i => i.nextElementSibling?.textContent?.trim() ?? '');
    const budget = form.querySelector<HTMLInputElement>('.cf-budget input:checked');
    const budgetText = budget?.nextElementSibling?.textContent?.trim();

    const [name, contact, company] = Array.from(inputs).map(i => i.value.trim());
    const lang = (document.documentElement.lang || 'ru') as Locale;

    if (!name || !contact || !story?.value.trim()) {
      flashLegal(legal, 'заполни обязательные поля', 'warn');
      return;
    }

    const originalLabel = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = 'sending…';

    try {
      await submitBrief({
        name,
        contact,
        company,
        services: checked,
        budget: budgetText,
        story: story.value.trim(),
        lang,
      });
      btn.innerHTML = 'sent OK ↗';
      flashLegal(legal, 'спасибо. вернёмся в течение 24 часов.', 'ok');
      form.reset();
      setTimeout(() => { btn.innerHTML = originalLabel; btn.disabled = false; }, 4000);
    } catch (err) {
      console.error('[brief] submit failed', err);
      btn.innerHTML = 'try again';
      btn.disabled = false;
      flashLegal(legal, 'не дошло. напиши на hi@impuls.studio', 'warn');
    }
  });
}

function flashLegal(el: HTMLElement | null, text: string, kind: 'ok' | 'warn') {
  if (!el) return;
  el.textContent = text;
  el.style.color = kind === 'ok' ? 'var(--acid)' : 'var(--warm)';
}
