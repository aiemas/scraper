#!/usr/bin/env python3
"""
Platinsport scraper definitivo corretto
- Trova link bc.vc vicino agli eventi
- Estrae correttamente il link diretto alla pagina /link/... dei canali AceStream
- Recupera tutti i link AceStream
- Salva playlist platinsport.m3u nella root
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"


def get_direct_link(bcvc_url: str) -> str:
    """
    Estrae il link diretto alla pagina /link/... dalla URL bc.vc
    Es: http://bc.vc/179424/https://www.platinsport.com/link/23dinqxz/01.php
         -> https://www.platinsport.com/link/23dinqxz/01.php
    """
    match = re.search(r"https?://www\.platinsport\.com/link/[^\s\"'>]+", bcvc_url)
    if match:
        return match.group(0)
    return bcvc_url  # fallback


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # estrai tutti i link bc.vc dal DOM
        content = await page.content()
        bcvc_links = re.findall(r"https?://bc\.vc/[^\s\"'>]+", content)

        if not bcvc_links:
            print("[ERRORE] Nessun link bc.vc trovato")
            await browser.close()
            return

        bcvc_url = bcvc_links[0]
        print(f"[INFO] Trovato link bc.vc: {bcvc_url}")

        # estrai link diretto alla pagina dei canali AceStream
        final_url = get_direct_link(bcvc_url)
        print(f"[INFO] Link diretto alla pagina dei canali: {final_url}")

        # apri la pagina /link/... e cerca AceStream
        print("[INFO] Carico pagina finale e cerco link AceStream...")
        await page.goto(final_url, timeout=60000)
        await page.wait_for_load_state("networkidle")

        page_content = await page.content()
        acestream_links = list(set(re.findall(r"acestream://[a-f0-9]{40}", page_content)))

        if not acestream_links:
            print("[ERRORE] Nessun link AceStream trovato")
            await browser.close()
            return

        print(f"[INFO] Trovati {len(acestream_links)} link AceStream")

        # salva playlist M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for i, link in enumerate(acestream_links, 1):
                f.write(f"#EXTINF:-1,Evento {i}\n{link}\n")

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
