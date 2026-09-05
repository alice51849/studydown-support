# Studydown — Support & Privacy

Canonical GitHub Pages source for Studydown:

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
- Free use includes up to three Activities and 300 seconds (five minutes) of
  total recorded time, Today and This Week summaries, and basic CSV. The
  allowance does not reset daily. A face-down session already underway is saved
  without trimming; new recordings require remaining allowance. Manual additions
  and duration increases must fit the remaining allowance in full.
- A one-time Lifetime Pro unlock adds unlimited Activities, month/year/custom
  analysis, weekly goals, Deadlines, Apple Watch, Widgets, advanced hero
  styles, and complete JSON backup/restore, and removes the recorded-time limit.
  No price is hard-coded.
- App records stay on-device. There is no account, developer server, ad,
  analytics, or tracking SDK.
- Widgets read the local App Group; Live Activities do not use server push.
  WatchConnectivity exchanges Activity identifiers/names, times, summaries,
  preferences, and entitlement state with the user's paired Apple Watch.
- Apple handles product/price loading, entitlement verification, purchase, and
  restore networking through StoreKit. Core timing needs no internet connection.
- Optional reminders use local iOS notifications, not a remote push service.
  Permission is requested through the reminder controls, not on first launch.
- CoreMotion processes orientation and movement on-device, without camera
  images. Automatic time accumulation and motion sampling stop when inactive.
- User-created CSV/JSON files go only to destinations the user chooses.
- Erasing local app records does not guarantee removal of exported files, Watch
  copies, or Apple-managed device backups; system backup settings apply.
- The static site itself sets no cookies and loads no third-party scripts.
- The only public contact address is `hourstag.app@gmail.com`.

`support_details` and `privacy_details` in every locale contain the short-session
test, reminder controls, Apple service disclosures, and device/deletion details.
The validator requires these sections, exact-50 coverage, both numeric free
limits (including native decimal digits), and all relevant Apple framework names.

Local generation is not proof of deployment or App Privacy approval. Before
publication, bind the policy to the final Release candidate and verify its
frameworks, entitlements, privacy manifest, and runtime data flows. In particular,
DEBUG-only motion trails must not ship. After a separately authorized deployment,
read back the live localized URLs; a local lint pass does not prove their content.
