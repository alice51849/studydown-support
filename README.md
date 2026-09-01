# Studydown — Support & Privacy

Production-ready GitHub Pages source for Studydown:

`https://alice51849.github.io/studydown-support/`

## Structure

- `source/locales/*.json` — native-quality copy for the exact 50 Apple locales
- `scripts/generate_site.py` — deterministic HTML, sitemap, and robots generator
- `scripts/validate_site.py` — fail-closed locale, product, privacy, link, and SEO checks
- `assets/site.css` — responsive, accessible light/dark presentation
- `assets/locale-redirect.js` — root-only browser-language routing with English fallback
- `source/site-icon.svg` — editable vector source for the local brand artwork
- `index.html`, `support.html`, `privacy.html` — English `x-default` fallback pages
- `<locale>/index.html`, `<locale>/support.html`, `<locale>/privacy.html` — exact locale pages

Generated HTML must not be edited by hand.

## Generate and validate

```sh
python3 scripts/generate_site.py
python3 scripts/generate_site.py --check
python3 scripts/validate_site.py
```

Rebuild the checked-in PNG artwork locally after changing the brand sources:

```sh
python3 scripts/generate_assets.py
```

The asset generator uses Pillow and the system SF font when available. Generated
PNG files are committed, so normal site generation only needs Python's standard
library.

The generated site contains 153 HTML pages: three `x-default` English fallback
pages plus three pages for every official Apple locale. Every page has a self
canonical, all 50 `hreflang` alternatives plus `x-default`, localized metadata,
an exact-50 language selector, and no analytics, advertising, cookies, or
remote page assets.

## Product and privacy facts

- Studydown is a general Activity-based face-down focus-time ledger for work,
  learning, and daily life.
- Free use includes unlimited focus sessions, up to three Activities, Today
  and This Week summaries, and basic CSV.
- A one-time Lifetime Pro unlock adds unlimited Activities, month/year/custom
  analysis, weekly goals, Deadlines, Apple Watch, Widgets, advanced hero
  styles, and complete JSON backup/restore. No price is hard-coded.
- App records stay on-device. There is no account, developer server, ad,
  analytics, or tracking SDK.
- Apple handles purchase and restore networking through StoreKit.
- User-created CSV/JSON files go only to destinations the user chooses.
- The static site itself sets no cookies and loads no third-party scripts.
- The only public contact address is `hourstag.app@gmail.com`.
