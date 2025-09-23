#!/usr/bin/env python3
"""
Platinsport scraper aggiornato
- Trova link bc.vc vicino agli eventi
- Risolve lo shortener cliccando su "Get Link"
- Recupera link AceStream
- Salva playlist platinsport.m3u nella root
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"


async def resolve_bcvc(bcvc_url: str) -> str:
    """Usa Playwright per cliccare su 'Get Link' e ottenere l'URL finale"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(bcvc_url, timeout=60000)

        # Attende il bottone "Get Link" e clicca
        await page.wait_for_selector("a#getlink", timeout=60000)
        await page.click("a#getlink")

        # Aspetta redirect finale
        await page.wait_for_load_state("networkidle")
        final_url = page.url
        await browser.close()
        return final_url


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)

        # aspetta il caricamento del DOM
        await page.wait_for_load_state("domcontentloaded")
        content = await page.content()

        # estrai TUTTI i link bc.vc dal DOM
        bcvc_links = re.findall(r"https?://bc\.vc/[^\s\"'>]+", content)

        if not bcvc_links:
            print("[ERRORE] Nessun link bc.vc trovato")
            await browser.close()
            return

        bcvc_url = bcvc_links[0]
        print(f"[INFO] Trovato link bc.vc: {bcvc_url}")

        print("[INFO] Risolvo shortener...")
        final_url = await resolve_bcvc(bcvc_url)
        print(f"[INFO] URL finale: {final_url}")

        print("[INFO] Carico pagina finale e cerco link AceStream...")
        await page.goto(final_url, timeout=60000)
        await page.wait_for_load_state("networkidle")

        # estrai link AceStream dalla pagina finale
        page_content = await page.content()
        acestream_links = list(set(re.findall(r"acestream://[a-f0-9]{40}", page_content)))

        if not acestream_links:
            print("[ERRORE] Nessun link AceStream trovato")
            await browser.close()
            return

        print(f"[INFO] Trovati {len(acestream_links)} link AceStream")

        # salva playlist m3u
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for i, link in enumerate(acestream_links, 1):
                f.write(f"#EXTINF:-1,Evento {i}\n{link}\n")

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
