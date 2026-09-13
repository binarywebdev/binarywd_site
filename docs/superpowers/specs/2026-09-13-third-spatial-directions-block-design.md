# Third spatial directions block

## Goal

Add a new third screen to the BinaryWD home page after the existing Directions section. The first two screens must remain visually and structurally unchanged.

## Content

- Heading: «Создаём продукты на границе физического и цифрового.»
- Description: «Проектируем виртуальные пространства, интерактивные приложения и цифровые сервисы — от первой идеи до запуска.»
- VR / AR: «Виртуальные тренажёры, музейные проекты и дополненная реальность.»
- Interactive / Games: «Игры, сенсорные инсталляции и интерактивные 3D-продукты.»
- Web / Mobile: «Приложения, сервисы и цифровые системы для бизнеса.»
- CTA: «Есть идея? Давайте превратим её в работающий продукт.»
- Button: «Обсудить проект» linking to `mailto:hello@binarywd.com`.

The existing RU / EN switch must translate every Russian string in the new section. Direction names remain unchanged in both languages.

## Visual contract

The section is a separate full-width third screen on the existing warm ivory page background. Inside it sits a restrained dark graphite panel related to the current Directions panel without copying its layout.

The heading and description form a compact two-column introduction. The generated `spatial-symbols-concept-v1.png` is then shown as one uninterrupted panoramic image so its shared camera, lighting, reflections, and spacing remain intact. Below it, three text columns align with the left, centre, and right symbols. The CTA closes the screen instead of floating over the artwork.

The image must not be cropped on desktop. The panel must not add glow, gradients outside the source artwork, decorative particles, cards, labels, or extra navigation.

## Responsive behaviour

- Desktop: panoramic artwork at full available width; three aligned text columns.
- Tablet: retain the panoramic artwork and reduce gaps and type scale.
- Mobile: show the complete artwork at its native aspect ratio, then stack the three direction descriptions vertically. Do not crop individual symbols or introduce horizontal scrolling.
- Respect `prefers-reduced-motion`.

## Motion

Use one subtle entrance treatment only: the artwork and copy may fade and translate slightly when the section enters the viewport. No continuous floating, particle animation, or excessive glow.

## Implementation boundary

- Add one new template part for the third screen.
- Include it after `template-parts/directions-spatial` in `front-page.php`.
- Add narrowly scoped styles to the existing front-page stylesheet and use the existing localization mechanism.
- Reuse the already generated image from `assets/images/spatial-symbols-concept-v1.png`.
- Do not modify the Hero, existing Directions markup, existing artwork, navigation, footer, or unrelated theme files.

## Verification

- Confirm the third section appears after Directions at desktop and mobile widths.
- Confirm all three symbols are fully visible and the text aligns correctly.
- Confirm RU / EN switching updates all new copy.
- Confirm the CTA target and keyboard focus state.
- Confirm no PHP syntax errors, broken image requests, horizontal overflow, or new browser console errors.
