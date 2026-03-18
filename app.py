#!/usr/bin/env python3
"""
📰 글로벌 경제 뉴스 요약기
- API 키 불필요 / 외부 라이브러리 설치 불필요
- 주요 매체 RSS 피드를 직접 파싱
"""

import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
import html
import sys
import os
import re
import json
import textwrap
from datetime import datetime

# ── RSS 피드 목록 ─────────────────────────────────────────────────────────────

FEEDS = {
    "1": {
        "label": "🌍 전체 글로벌 경제",
        "sources": [
            ("Reuters Business",   "https://feeds.reuters.com/reuters/businessNews"),
            ("BBC Business",       "https://feeds.bbci.co.uk/news/business/rss.xml"),
            ("CNBC Economy",       "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
        ],
    },
    "2": {
        "label": "🇺🇸 미국 경제",
        "sources": [
            ("Reuters US",         "https://feeds.reuters.com/reuters/USdomesticNews"),
            ("CNBC US",            "https://www.cnbc.com/id/15837362/device/rss/rss.html"),
            ("MarketWatch",        "https://feeds.marketwatch.com/marketwatch/topstories/"),
        ],
    },
    "3": {
        "label": "📈 주식·증시",
        "sources": [
            ("CNBC Markets",       "https://www.cnbc.com/id/15839069/device/rss/rss.html"),
            ("Reuters Markets",    "https://feeds.reuters.com/reuters/companyNews"),
            ("Investing.com",      "https://www.investing.com/rss/news_14.rss"),
        ],
    },
    "4": {
        "label": "🏦 중앙은행·금리",
        "sources": [
            ("Reuters Finance",    "https://feeds.reuters.com/reuters/financialwireNews"),
            ("CNBC Finance",       "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
            ("FT Markets",         "https://www.ft.com/markets?format=rss"),
        ],
    },
    "5": {
        "label": "🛢️  원자재·에너지",
        "sources": [
            ("Reuters Commodities","https://feeds.reuters.com/reuters/commoditiesNews"),
            ("OilPrice.com",       "https://oilprice.com/rss/main"),
            ("CNBC Energy",        "https://www.cnbc.com/id/10000088/device/rss/rss.html"),
        ],
    },
    "6": {
        "label": "🤖 AI·테크 산업",
        "sources": [
            ("Reuters Tech",       "https://feeds.reuters.com/reuters/technologyNews"),
            ("CNBC Tech",          "https://www.cnbc.com/id/19854910/device/rss/rss.html"),
            ("TechCrunch",         "https://techcrunch.com/feed/"),
        ],
    },
    "7": {
        "label": "🌏 아시아 경제",
        "sources": [
            ("Reuters Asia",       "https://feeds.reuters.com/reuters/AsiaNews"),
            ("CNBC Asia",          "https://www.cnbc.com/id/19832390/device/rss/rss.html"),
            ("Nikkei Asia",        "https://asia.nikkei.com/rss/feed/nar"),
        ],
    },
}

# ── 유틸리티 ──────────────────────────────────────────────────────────────────

WIDTH = 62

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def c(code, text):
    return f"\033[{code}m{text}\033[0m"

def print_header():
    print(c("1;36", "╔" + "═" * WIDTH + "╗"))
    print(c("1;36", "║") + c("1;33", "   📰  글로벌 경제 뉴스 요약기".center(WIDTH)) + c("1;36", "║"))
    print(c("1;36", "║") + c("2",    "   API 없음 · 설치 없음 · RSS 실시간".center(WIDTH + 1)) + c("1;36", "║"))
    print(c("1;36", "╚" + "═" * WIDTH + "╝"))
    print()

def print_menu():
    print(c("1;33", "📂 카테고리를 선택하세요:\n"))
    for key, info in FEEDS.items():
        print(f"  {c('1', key)}. {info['label']}")
    print(f"\n  {c('1', '0')}. 종료\n")

def clean(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())

def wrap_text(text: str, indent: int = 5) -> str:
    prefix = " " * indent
    return textwrap.fill(text, width=WIDTH + indent,
                         initial_indent=prefix,
                         subsequent_indent=prefix)

# ── 번역 ─────────────────────────────────────────────────────────────────────

def translate_ko(text: str) -> str:
    """Google 번역 비공식 엔드포인트로 한국어 번역 (API 키 불필요)"""
    if not text:
        return text
    try:
        params = urllib.parse.urlencode({
            "client": "gtx",
            "sl":     "auto",
            "tl":     "ko",
            "dt":     "t",
            "q":      text,
        })
        url = f"https://translate.googleapis.com/translate_a/single?{params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0"
        })
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        # 응답 구조: [[[번역문, 원문, ...], ...], ...]
        translated = "".join(
            seg[0] for seg in data[0] if seg[0]
        )
        return translated.strip() or text
    except Exception:
        return text  # 번역 실패 시 원문 반환




def fetch_rss(url: str, timeout: int = 8):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        )
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()

    root = ET.fromstring(raw)
    items = []

    # RSS 2.0
    for item in root.iter("item"):
        title = clean(item.findtext("title", ""))
        desc  = clean(item.findtext("description", ""))
        link  = item.findtext("link", "")
        pub   = item.findtext("pubDate", "")
        if title:
            items.append({"title": title, "desc": desc,
                          "link": link, "pub": pub})

    # Atom
    atom_ns = "{http://www.w3.org/2005/Atom}"
    for entry in root.iter(f"{atom_ns}entry"):
        title   = clean(entry.findtext(f"{atom_ns}title", ""))
        desc    = clean(entry.findtext(f"{atom_ns}summary", ""))
        link_el = entry.find(f"{atom_ns}link")
        link    = link_el.get("href", "") if link_el is not None else ""
        pub     = entry.findtext(f"{atom_ns}updated", "")
        if title:
            items.append({"title": title, "desc": desc,
                          "link": link, "pub": pub})

    return items[:10]

def collect_news(sources: list) -> list:
    all_items = []
    for name, url in sources:
        sys.stdout.write(f"\r  ⏳ {name} 수집 중...{' ' * 20}")
        sys.stdout.flush()
        try:
            items = fetch_rss(url)
            for it in items:
                it["source"] = name
                sys.stdout.write(f"\r  🌐 {name} 번역 중...{' ' * 20}")
                sys.stdout.flush()
                it["title"] = translate_ko(it["title"])
                it["desc"]  = translate_ko(it["desc"][:300]) if it["desc"] else ""
            all_items.extend(items)
            sys.stdout.write(f"\r  ✅ {name} — {len(items)}건{' ' * 20}\n")
        except Exception as e:
            sys.stdout.write(f"\r  ⚠️  {name} 실패 ({str(e)[:35]}){' ' * 10}\n")
        sys.stdout.flush()
    return all_items

# ── 출력 ──────────────────────────────────────────────────────────────────────

def print_news(items: list, label: str):
    if not items:
        print(c("1;31", "\n❌ 뉴스를 가져오지 못했습니다. 인터넷 연결을 확인하세요."))
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print()
    print(c("1;36", "═" * (WIDTH + 5)))
    print(c("1;33", f"  {label}  ({now})"))
    print(c("1;36", "═" * (WIDTH + 5)))

    shown = items[:15]
    for i, it in enumerate(shown, 1):
        print()
        print(c("1;32", f"  [{i:02d}] ") + c("1", it["title"]))
        print(c("2", f"       출처: {it['source']}"))
        if it["desc"]:
            short = it["desc"][:220] + ("..." if len(it["desc"]) > 220 else "")
            print(wrap_text(short))

    print()
    print(c("1;36", "═" * (WIDTH + 5)))
    print(c("2", f"  총 {len(shown)}건 표시됨 / 수집된 뉴스 {len(items)}건"))

# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    clear()
    print_header()

    while True:
        print_menu()
        try:
            choice = input(c("1", "선택 (0-7): ")).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 종료합니다.")
            break

        if choice == "0":
            print("\n👋 종료합니다.\n")
            break

        if choice not in FEEDS:
            print(c("1;31", "⚠️  0~7 중에서 선택하세요.\n"))
            continue

        info = FEEDS[choice]
        print(f"\n{c('1;35', info['label'])} 뉴스 수집 시작...\n")

        items = collect_news(info["sources"])
        print_news(items, info["label"])

        try:
            input(f"\n{c('2', '[Enter]를 누르면 메뉴로 돌아갑니다...')}")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 종료합니다.")
            break

        clear()
        print_header()

if __name__ == "__main__":
    main()
