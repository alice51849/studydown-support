#!/usr/bin/env python3
"""Fail-closed validation for the Studydown exact-50 website."""

from __future__ import annotations

import collections
import pathlib
import re
import struct
import sys
from html.parser import HTMLParser

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from generate_site import (  # noqa: E402
    ASSET_ROOT,
    BASE_URL,
    EMAIL,
    LOCALES,
    OG_LOCALES,
    PAGE_FILES,
    PAGES,
    ROOT,
    RTL,
    expected_outputs,
    load_translations,
    page_url,
    render_sitemap,
)

EXPECTED_PAGES = 3 * (len(LOCALES) + 1)
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|FIXME)\b|(?i:lorem ipsum)|\?\?\?|\{\{")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PRICE_RE = re.compile(r"(?:US\$|AU\$|CA\$|NZ\$|HK\$|NT\$|[$€£¥₹₩₽])\s*\d|\d[\d.,]*\s*(?:USD|EUR|GBP)")
TRACKING_RE = re.compile(
    r"google-analytics|googletagmanager|gtag\s*\(|facebook(?:\.net| pixel)|"
    r"mixpanel|segment\.com|hotjar|doubleclick|fingerprintjs|document\.cookie|"
    r"localStorage|sessionStorage|fetch\s*\(|XMLHttpRequest",
    re.I,
)
SCHOOL_ONLY_RE = re.compile(
    r"\b(?:subjects?|exams?|students?|schoolwork|school subject)\b|"
    r"科目|考試|考试|學生|学生|試験|生徒|과목|시험|학생|"
    r"\b(?:asignaturas?|exámenes?|examen|estudiantes?|Schulfach|Prüfung|"
    r"étudiant(?:e|s|es)?|matière scolaire|esame|studente|"
    r"экзамен|ученик|школьн|предметы?)\b",
    re.I,
)
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.html: dict[str, str] = {}
        self.canonical: list[str] = []
        self.alternates: dict[str, list[str]] = collections.defaultdict(list)
        self.metas: dict[str, list[str]] = collections.defaultdict(list)
        self.hrefs: list[str] = []
        self.language_links: dict[str, str] = {}
        self.scripts: list[dict[str, str]] = []
        self.ids: set[str] = set()
        self.main_count = 0
        self.doctype = False

    def handle_decl(self, declaration: str) -> None:
        self.doctype = declaration.lower() == "doctype html"

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if tag not in VOID:
            self.stack.append(tag)
        if "style" in attrs:
            self.errors.append(f"inline style on <{tag}>")
        if any(key.lower().startswith("on") for key in attrs):
            self.errors.append(f"inline event handler on <{tag}>")
        if tag in {"iframe", "form", "object", "embed"}:
            self.errors.append(f"forbidden <{tag}>")
        if tag == "html":
            self.html = attrs
        if tag == "main":
            self.main_count += 1
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.errors.append(f"duplicate id {attrs['id']}")
            self.ids.add(attrs["id"])
        if tag == "a":
            self.hrefs.append(attrs.get("href", ""))
            if "hreflang" in attrs:
                self.language_links[attrs["hreflang"]] = attrs.get("href", "")
        if tag == "link":
            rel = set(attrs.get("rel", "").split())
            if "canonical" in rel:
                self.canonical.append(attrs.get("href", ""))
            if "alternate" in rel and "hreflang" in attrs:
                self.alternates[attrs["hreflang"]].append(attrs.get("href", ""))
        if tag == "meta":
            key = attrs.get("name") or attrs.get("property") or attrs.get("http-equiv")
            if key:
                self.metas[key].append(attrs.get("content", ""))
        if tag == "script":
            self.scripts.append(attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced closing </{tag}>")
            return
        self.stack.pop()


def all_strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(all_strings(item))
        return result
    if isinstance(value, dict):
        result = []
        for item in value.values():
            result.extend(all_strings(item))
        return result
    return []


def png_size(path: pathlib.Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise ValueError("not a PNG")
    return struct.unpack(">II", data[16:24])


def check_sources(errors: list[str], translations: dict[str, dict[str, object]]) -> None:
    if len(translations) != 50 or set(translations) != set(LOCALES):
        errors.append("translation locale set is not exact 50")
    all_text = []
    for locale in LOCALES:
        strings = all_strings(translations[locale])
        all_text.extend(strings)
        if any(not text.strip() for text in strings):
            errors.append(f"{locale}: empty localized string")
        joined = "\n".join(strings)
        if PLACEHOLDER.search(joined):
            errors.append(f"{locale}: placeholder text")
        if PRICE_RE.search(joined):
            errors.append(f"{locale}: hard-coded price")
        if SCHOOL_ONLY_RE.search(joined):
            errors.append(f"{locale}: school-only terminology")
        emails = set(EMAIL_RE.findall(joined))
        if emails and emails != {EMAIL}:
            errors.append(f"{locale}: unauthorized email")
        if locale not in {"en-AU", "en-CA", "en-GB", "en-US"}:
            if translations[locale]["home"] == translations["en-US"]["home"]:
                errors.append(f"{locale}: untranslated home copy")

    joined_all = "\n".join(all_text)
    if TRACKING_RE.search(joined_all):
        errors.append("translation source contains tracking/network code")
    en = translations["en-US"]
    required = [
        "work, learning, and daily life",
        "unlimited focus sessions",
        "up to 3 Activities",
        "Today and This Week",
        "basic CSV",
        "unlimited Activities",
        "month, year, and custom analysis",
        "weekly goals",
        "Deadlines",
        "Apple Watch",
        "Widgets",
        "advanced hero styles",
        "complete JSON backup and restore",
        "No subscription",
        "StoreKit",
        "GitHub Pages",
    ]
    for phrase in required:
        if phrase not in "\n".join(all_strings(en)):
            errors.append(f"en-US missing required fact: {phrase}")


def check_page(
    path: pathlib.Path, locale: str | None, page: str, errors: list[str]
) -> None:
    relative = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    parser = Parser()
    parser.feed(text)
    parser.close()
    content_locale = locale or "en-US"
    expected_canonical = page_url(locale, page)
    if not parser.doctype:
        errors.append(f"{relative}: missing HTML5 doctype")
    if parser.stack:
        errors.append(f"{relative}: unclosed tags")
    errors.extend(f"{relative}: {error}" for error in parser.errors)
    if parser.html.get("lang") != content_locale:
        errors.append(f"{relative}: wrong html lang")
    if parser.html.get("dir") != ("rtl" if content_locale in RTL else "ltr"):
        errors.append(f"{relative}: wrong direction")
    if parser.main_count != 1 or "main" not in parser.ids:
        errors.append(f"{relative}: main landmark is not exact")
    if parser.canonical != [expected_canonical]:
        errors.append(f"{relative}: canonical is not self-exact")
    expected_hreflangs = set(LOCALES) | {"x-default"}
    if set(parser.alternates) != expected_hreflangs:
        errors.append(f"{relative}: hreflang set is not exact")
    for code in LOCALES:
        if parser.alternates.get(code) != [page_url(code, page)]:
            errors.append(f"{relative}: bad hreflang URL for {code}")
    if parser.alternates.get("x-default") != [page_url(None, page)]:
        errors.append(f"{relative}: bad x-default URL")
    if set(parser.language_links) != set(LOCALES):
        errors.append(f"{relative}: language selector is not exact 50")
    if parser.metas.get("og:url") != [expected_canonical]:
        errors.append(f"{relative}: OpenGraph URL differs from canonical")
    if parser.metas.get("og:locale") != [OG_LOCALES[content_locale]]:
        errors.append(f"{relative}: wrong OpenGraph locale")
    if parser.metas.get("robots") != ["index,follow,max-image-preview:large"]:
        errors.append(f"{relative}: wrong robots metadata")
    if len(parser.metas.get("description", [])) != 1:
        errors.append(f"{relative}: missing unique description")
    expected_script = locale is None and page == "index"
    if expected_script:
        if parser.scripts != [{"src": f"{ASSET_ROOT}locale-redirect.js", "defer": ""}]:
            errors.append(f"{relative}: root router script is not exact")
    elif parser.scripts:
        errors.append(f"{relative}: unexpected script")
    expected_csp_script = "'self'" if expected_script else "'none'"
    csp = parser.metas.get("Content-Security-Policy", [])
    if len(csp) != 1 or f"script-src {expected_csp_script}" not in csp[0]:
        errors.append(f"{relative}: CSP script policy is wrong")
    for href in parser.hrefs:
        if href.startswith("mailto:"):
            if href != f"mailto:{EMAIL}":
                errors.append(f"{relative}: unauthorized mail link")
        elif href.startswith(BASE_URL):
            continue
        elif href.startswith("#"):
            continue
        else:
            errors.append(f"{relative}: unexpected link {href}")
    found_emails = set(EMAIL_RE.findall(text))
    if found_emails != {EMAIL}:
        errors.append(f"{relative}: public email set is not exact")
    if PRICE_RE.search(text):
        errors.append(f"{relative}: hard-coded price")
    if SCHOOL_ONLY_RE.search(text):
        errors.append(f"{relative}: school-only terminology")
    if TRACKING_RE.search(text):
        errors.append(f"{relative}: tracking or unexpected network code")


def check_assets(errors: list[str]) -> None:
    required = {
        ROOT / "assets" / "site.css",
        ROOT / "assets" / "locale-redirect.js",
        ROOT / "assets" / "site-icon.svg",
        ROOT / "assets" / "site-icon.png",
        ROOT / "assets" / "social-card.png",
        ROOT / ".nojekyll",
    }
    for path in required:
        if not path.is_file():
            errors.append(f"missing asset {path.relative_to(ROOT)}")
    for path, expected in [
        (ROOT / "assets" / "site-icon.png", (256, 256)),
        (ROOT / "assets" / "social-card.png", (1200, 630)),
    ]:
        if path.is_file():
            try:
                if png_size(path) != expected:
                    errors.append(f"{path.name}: wrong dimensions")
            except (OSError, ValueError):
                errors.append(f"{path.name}: invalid PNG")
    router = ROOT / "assets" / "locale-redirect.js"
    if router.is_file():
        text = router.read_text(encoding="utf-8")
        if TRACKING_RE.search(text):
            errors.append("locale router contains storage, tracking, or network access")
        for locale in LOCALES:
            if f'"{locale}"' not in text:
                errors.append(f"locale router omits {locale}")


def check_sitemap(errors: list[str]) -> None:
    sitemap = ROOT / "sitemap.xml"
    robots = ROOT / "robots.txt"
    if not sitemap.is_file() or sitemap.read_text(encoding="utf-8") != render_sitemap():
        errors.append("sitemap.xml is missing or stale")
    if not robots.is_file() or f"Sitemap: {BASE_URL}sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt does not name the canonical sitemap")


def check_text_format(errors: list[str]) -> None:
    extensions = {".css", ".html", ".js", ".json", ".md", ".py", ".svg", ".txt", ".xml"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix not in extensions and path.name not in {".gitignore", ".nojekyll"}:
            continue
        text = path.read_text(encoding="utf-8")
        lines = [line.rstrip() for line in text.splitlines()]
        while lines and not lines[-1]:
            lines.pop()
        expected = "\n".join(lines) + ("\n" if lines else "")
        if text != expected:
            errors.append(f"{path.relative_to(ROOT)}: trailing whitespace or extra blank line at EOF")


def main() -> None:
    errors: list[str] = []
    try:
        translations = load_translations()
    except SystemExit as error:
        raise SystemExit(f"FAIL: {error}") from error
    check_sources(errors, translations)
    outputs = expected_outputs(translations)
    expected_html = {path for path in outputs if path.suffix == ".html"}
    actual_html = set(ROOT.rglob("*.html"))
    if len(expected_html) != EXPECTED_PAGES or actual_html != expected_html:
        errors.append(f"HTML page set must be exactly {EXPECTED_PAGES}")
    for locale in [None, *LOCALES]:
        for page in PAGES:
            path = ROOT / PAGE_FILES[page] if locale is None else ROOT / locale / PAGE_FILES[page]
            if path.is_file():
                check_page(path, locale, page, errors)
            else:
                errors.append(f"missing page {path.relative_to(ROOT)}")
    check_assets(errors)
    check_sitemap(errors)
    check_text_format(errors)
    for path, expected in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            errors.append(f"generated output is stale: {path.relative_to(ROOT)}")
    if errors:
        for error in dict.fromkeys(errors):
            print(f"FAIL: {error}")
        raise SystemExit(1)
    print(f"PASS: {EXPECTED_PAGES} pages, {len(LOCALES)} locales, exact canonical/hreflang/sitemap, privacy and product facts verified.")


if __name__ == "__main__":
    main()
