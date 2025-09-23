#!/usr/bin/env python3
"""
platinsport_scraper.py
- Apre Platinsport
- Trova il link bcvc.ink (shortener)
- Lo risolve cliccando su "Get Link" con Playwright
- Recupera i link AceStream dalla pagina finale
- Salva tutto in platinsport.m3u nella root della repo
"""

import re
import asyncio
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"


async def resolve_bcvc(bcvc_url: str) -> str:
    """Usa Playwright per cliccare su 'Get Link' e ottenere l'URL finale"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(bcvc_url, timeout=60000)

        # Attende il bottone "Get Link"
        await page.wait_for_selector("a#getlink", timeout=60000)
        await page.click("a#getlink")

        # Aspetta il redirect finale
        await page.wait_for_load_state("networkidle")
        final_url = page.url

        await browser.close()
        return final_url


def extract_acestream_links(html: str):
    """Trova link acestream nella pagina"""
    links = re.findall(r"(acestream://[^\s\"']+)", html)
    return list(set(links))


async def main():
    print("[INFO] Scarico pagina Platinsport...")
    r = requests.get(PLATIN_URL, timeout=30)

    # cerca link bcvc in tutto l'HTML (non solo <a>)
    bcvc_links = re.findall(r"https?://bcvc\.[^\s\"']+", r.text)
    if not bcvc_links:
        print("[ERRORE] Nessun link bcvc trovato")
        return

    bcvc_url = bcvc_links[0]
    print(f"[INFO] Trovato link bcvc: {bcvc_url}")

    print("[INFO] Risolvo shortener con Playwright...")
    final_url = await resolve_bcvc(bcvc_url)
    print(f"[INFO] URL finale: {final_url}")

    print("[INFO] Scarico pagina finale...")
    r2 = requests.get(final_url, timeout=30)
    acestream_links = extract_acestream_links(r2.text)

    if not acestream_links:
        print("[ERRORE] Nessun link AceStream trovato")
        return

    print(f"[INFO] Trovati {len(acestream_links)} link AceStream")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for i, link in enumerate(acestream_links, 1):
            f.write(f"#EXTINF:-1,Evento {i}\n{link}\n")

    print(f"[OK] Playlist salvata in {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
