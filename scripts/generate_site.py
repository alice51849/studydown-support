#!/usr/bin/env python3
"""Generate the exact-50 Studydown support and privacy website."""

from __future__ import annotations

import argparse
import html
import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "source" / "locales"
BASE_URL = "https://alice51849.github.io/studydown-support/"
ASSET_ROOT = "/studydown-support/assets/"
EMAIL = "hourstag.app@gmail.com"
UPDATED = "2026-09-05"
PAGES = ("index", "support", "privacy")
PAGE_FILES = {"index": "index.html", "support": "support.html", "privacy": "privacy.html"}
LOCALES = [
    "ar-SA", "bn-BD", "ca", "zh-Hans", "zh-Hant", "hr", "cs", "da",
    "nl-NL", "en-AU", "en-CA", "en-GB", "en-US", "fi", "fr-CA",
    "fr-FR", "de-DE", "el", "gu-IN", "he", "hi", "hu", "id", "it",
    "ja", "kn-IN", "ko", "ms", "ml-IN", "mr-IN", "no", "or-IN", "pl",
    "pt-BR", "pt-PT", "pa-IN", "ro", "ru", "sk", "sl-SI", "es-MX",
    "es-ES", "sv", "ta-IN", "te-IN", "th", "tr", "uk", "ur-PK", "vi",
]
RTL = {"ar-SA", "he", "ur-PK"}
OG_LOCALES = {
    "ar-SA": "ar_SA", "bn-BD": "bn_BD", "ca": "ca_ES",
    "zh-Hans": "zh_CN", "zh-Hant": "zh_TW", "hr": "hr_HR",
    "cs": "cs_CZ", "da": "da_DK", "nl-NL": "nl_NL",
    "en-AU": "en_AU", "en-CA": "en_CA", "en-GB": "en_GB",
    "en-US": "en_US", "fi": "fi_FI", "fr-CA": "fr_CA",
    "fr-FR": "fr_FR", "de-DE": "de_DE", "el": "el_GR",
    "gu-IN": "gu_IN", "he": "he_IL", "hi": "hi_IN", "hu": "hu_HU",
    "id": "id_ID", "it": "it_IT", "ja": "ja_JP", "kn-IN": "kn_IN",
    "ko": "ko_KR", "ms": "ms_MY", "ml-IN": "ml_IN", "mr-IN": "mr_IN",
    "no": "nb_NO", "or-IN": "or_IN", "pl": "pl_PL", "pt-BR": "pt_BR",
    "pt-PT": "pt_PT", "pa-IN": "pa_IN", "ro": "ro_RO", "ru": "ru_RU",
    "sk": "sk_SK", "sl-SI": "sl_SI", "es-MX": "es_MX",
    "es-ES": "es_ES", "sv": "sv_SE", "ta-IN": "ta_IN",
    "te-IN": "te_IN", "th": "th_TH", "tr": "tr_TR", "uk": "uk_UA",
    "ur-PK": "ur_PK", "vi": "vi_VN",
}
EXPECTED_KEYS = {
    "language_name", "language_label", "navigation_label", "skip_link", "nav",
    "footer", "contact", "home", "facts", "support", "faqs", "privacy",
    "privacy_sections", "support_details", "privacy_details",
}


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def load_translations() -> dict[str, dict[str, Any]]:
    files = {path.stem: path for path in SOURCE_DIR.glob("*.json")}
    if set(files) != set(LOCALES):
        missing = ", ".join(sorted(set(LOCALES) - set(files))) or "none"
        extra = ", ".join(sorted(set(files) - set(LOCALES))) or "none"
        raise SystemExit(f"locale files mismatch; missing: {missing}; extra: {extra}")
    data: dict[str, dict[str, Any]] = {}
    for locale in LOCALES:
        try:
            item = json.loads(files[locale].read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit(f"{locale}: unreadable locale file: {error}") from error
        if set(item) != EXPECTED_KEYS:
            raise SystemExit(f"{locale}: locale schema keys are not exact")
        if not isinstance(item["nav"], list) or len(item["nav"]) != 3:
            raise SystemExit(f"{locale}: nav must contain three labels")
        if not isinstance(item["contact"], list) or len(item["contact"]) != 3:
            raise SystemExit(f"{locale}: contact must contain three strings")
        if not isinstance(item["home"], list) or len(item["home"]) != 3:
            raise SystemExit(f"{locale}: home must contain three strings")
        if not isinstance(item["facts"], list) or len(item["facts"]) != 4:
            raise SystemExit(f"{locale}: facts must contain four pairs")
        if not isinstance(item["support"], list) or len(item["support"]) != 3:
            raise SystemExit(f"{locale}: support must contain three strings")
        if not isinstance(item["faqs"], list) or len(item["faqs"]) != 4:
            raise SystemExit(f"{locale}: faqs must contain four pairs")
        if not isinstance(item["privacy"], list) or len(item["privacy"]) != 3:
            raise SystemExit(f"{locale}: privacy must contain three strings")
        if not isinstance(item["privacy_sections"], list) or len(item["privacy_sections"]) != 6:
            raise SystemExit(f"{locale}: privacy_sections must contain six pairs")
        if not isinstance(item["support_details"], list) or len(item["support_details"]) != 2:
            raise SystemExit(f"{locale}: support_details must contain two pairs")
        if not isinstance(item["privacy_details"], list) or len(item["privacy_details"]) != 3:
            raise SystemExit(f"{locale}: privacy_details must contain three pairs")
        for group in ("facts", "faqs", "privacy_sections", "support_details", "privacy_details"):
            if any(not isinstance(pair, list) or len(pair) != 2 for pair in item[group]):
                raise SystemExit(f"{locale}: {group} entries must be title/body pairs")
        data[locale] = item
    return data


def page_url(locale: str | None, page: str) -> str:
    prefix = f"{locale}/" if locale else ""
    suffix = "" if page == "index" else PAGE_FILES[page]
    return f"{BASE_URL}{prefix}{suffix}"


def output_path(locale: str | None, page: str) -> pathlib.Path:
    return ROOT / locale / PAGE_FILES[page] if locale else ROOT / PAGE_FILES[page]


def alternates(page: str) -> str:
    rows = [
        f'<link rel="alternate" hreflang="{locale}" href="{page_url(locale, page)}">'
        for locale in LOCALES
    ]
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{page_url(None, page)}">')
    return "\n  ".join(rows)


def navigation(locale: str | None, current: str, labels: list[str]) -> str:
    rows = []
    for page, label in zip(PAGES, labels, strict=True):
        active = ' aria-current="page"' if page == current else ""
        rows.append(f'<a href="{page_url(locale, page)}"{active}>{esc(label)}</a>')
    return "\n        ".join(rows)


def language_picker(
    translations: dict[str, dict[str, Any]], current_locale: str, page: str
) -> str:
    rows = []
    for locale in LOCALES:
        active = ' aria-current="page"' if locale == current_locale else ""
        rows.append(
            f'<li><a lang="{locale}" hreflang="{locale}" dir="auto" '
            f'href="{page_url(locale, page)}"{active}>'
            f'{esc(translations[locale]["language_name"])}</a></li>'
        )
    return "\n          ".join(rows)


def contact_markup(item: dict[str, Any]) -> str:
    heading, body, button = item["contact"]
    return f"""
<section class="card contact-card" aria-labelledby="contact-heading">
  <h2 id="contact-heading">{esc(heading)}</h2>
  <p>{esc(body)}</p>
  <address class="contact-actions">
    <a class="mail-button" href="mailto:{EMAIL}">{esc(button)}</a>
    <a class="mail-address" href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a>
  </address>
</section>""".strip()


def home_markup(item: dict[str, Any]) -> str:
    cards = "\n".join(
        f'<li><article class="card"><h3>{esc(title)}</h3><p>{esc(body)}</p></article></li>'
        for title, body in item["facts"]
    )
    return f"""
<section aria-labelledby="facts-heading">
  <h2 class="section-heading" id="facts-heading">{esc(item["home"][2])}</h2>
  <ul class="fact-grid" role="list">
    {cards}
  </ul>
</section>
{contact_markup(item)}""".strip()


def support_markup(item: dict[str, Any]) -> str:
    free_fact, pro_fact = item["facts"][1], item["facts"][2]
    entries = [*item["faqs"][:2], free_fact, pro_fact, *item["faqs"][2:], *item["support_details"]]
    rows = "\n".join(
        f'<details class="faq"><summary>{esc(title)}</summary><p>{esc(body)}</p></details>'
        for title, body in entries
    )
    return f"""
<section aria-labelledby="faq-heading">
  <h2 class="section-heading" id="faq-heading">{esc(item["support"][2])}</h2>
  <div class="faq-list">
    {rows}
  </div>
</section>
{contact_markup(item)}""".strip()


def privacy_markup(item: dict[str, Any]) -> str:
    rows = "\n".join(
        f'<section class="card"><h2>{esc(title)}</h2><p>{esc(body)}</p></section>'
        for title, body in [*item["privacy_sections"], *item["privacy_details"]]
    )
    return f"""
<div class="policy-list">
  {rows}
</div>
{contact_markup(item)}""".strip()


def render_page(
    translations: dict[str, dict[str, Any]], locale: str | None, page: str
) -> str:
    content_locale = locale or "en-US"
    item = translations[content_locale]
    block = item["home" if page == "index" else page]
    direction = "rtl" if content_locale in RTL else "ltr"
    canonical = page_url(locale, page)
    title = f"{block[0]} — Studydown"
    body = {"index": home_markup, "support": support_markup, "privacy": privacy_markup}[page](item)
    updated = (
        f'\n        <p class="updated">{esc(block[2])}: <time datetime="{UPDATED}" dir="ltr">{UPDATED}</time></p>'
        if page == "privacy" else ""
    )
    is_router = locale is None and page == "index"
    csp_script = "'self'" if is_router else "'none'"
    router = (
        f'\n  <script src="{ASSET_ROOT}locale-redirect.js" defer></script>'
        if is_router else ""
    )
    return f"""<!doctype html>
<!-- Generated by scripts/generate_site.py. Do not edit directly. -->
<html lang="{content_locale}" dir="{direction}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#f8f5fc" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#100d1b" media="(prefers-color-scheme: dark)">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="referrer" content="no-referrer">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src {csp_script}; connect-src 'none'; font-src 'none'; object-src 'none'; frame-src 'none'; media-src 'none'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(block[1])}">
  <link rel="canonical" href="{canonical}">
  {alternates(page)}
  <link rel="icon" href="{ASSET_ROOT}site-icon.png" type="image/png" sizes="256x256">
  <link rel="apple-touch-icon" href="{ASSET_ROOT}site-icon.png" sizes="256x256">
  <link rel="stylesheet" href="{ASSET_ROOT}site.css">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Studydown">
  <meta property="og:locale" content="{OG_LOCALES[content_locale]}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(block[1])}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{BASE_URL}assets/social-card.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Studydown">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(block[1])}">
  <meta name="twitter:image" content="{BASE_URL}assets/social-card.png">{router}
</head>
<body>
  <a class="skip-link" href="#main">{esc(item["skip_link"])}</a>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{page_url(locale, "index")}" dir="ltr">
        <img src="{ASSET_ROOT}site-icon.svg" width="64" height="64" alt="">
        <span>Studydown</span>
      </a>
      <nav class="primary-nav" aria-label="{esc(item["navigation_label"])}">
        {navigation(locale, page, item["nav"])}
      </nav>
      <details class="language-picker">
        <summary>{esc(item["language_label"])}</summary>
        <ul class="language-list" role="list">
          {language_picker(translations, content_locale, page)}
        </ul>
      </details>
    </div>
  </header>
  <main class="page-shell" id="main" tabindex="-1">
    <header class="hero">
      <div>
        <p class="eyebrow">Studydown</p>
        <h1>{esc(block[0])}</h1>
        <p class="lead">{esc(block[1])}</p>{updated}
      </div>
      <div class="hero-art" aria-hidden="true">
        <img class="hero-mark" src="{ASSET_ROOT}site-icon.svg" width="256" height="256" alt="">
      </div>
    </header>
    {body}
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <p>{esc(item["footer"])}</p>
      <address><a href="mailto:{EMAIL}" dir="ltr">{EMAIL}</a></address>
    </div>
  </footer>
</body>
</html>
"""


def render_sitemap() -> str:
    urls = [page_url(None, page) for page in PAGES]
    urls.extend(page_url(locale, page) for locale in LOCALES for page in PAGES)
    rows = "\n".join(
        f"  <url><loc>{esc(url)}</loc><lastmod>{UPDATED}</lastmod></url>" for url in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{rows}\n</urlset>\n"
    )


def expected_outputs(translations: dict[str, dict[str, Any]]) -> dict[pathlib.Path, str]:
    outputs = {
        output_path(locale, page): render_page(translations, locale, page)
        for locale in [None, *LOCALES]
        for page in PAGES
    }
    outputs[ROOT / "sitemap.xml"] = render_sitemap()
    outputs[ROOT / "robots.txt"] = (
        f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n"
    )
    return outputs


def write_outputs(outputs: dict[pathlib.Path, str]) -> None:
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Generated {3 * (len(LOCALES) + 1)} HTML pages for {len(LOCALES)} locales.")


def check_outputs(outputs: dict[pathlib.Path, str]) -> None:
    failures = []
    for path, expected in outputs.items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            failures.append(f"stale {path.relative_to(ROOT)}")
    expected_html = {path.resolve() for path in outputs if path.suffix == ".html"}
    actual_html = {path.resolve() for path in ROOT.rglob("*.html")}
    failures.extend(
        f"unexpected {path.relative_to(ROOT.resolve())}"
        for path in sorted(actual_html - expected_html)
    )
    if failures:
        raise SystemExit("\n".join(f"FAIL: {failure}" for failure in failures))
    print(f"PASS generator check: {len(expected_html)} deterministic HTML pages.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = expected_outputs(load_translations())
    check_outputs(outputs) if args.check else write_outputs(outputs)


if __name__ == "__main__":
    main()
