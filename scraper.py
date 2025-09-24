#!/usr/bin/env python3
"""
Platinsport AceStream Scraper
- Estrae tutte le partite e relativi link AceStream
- Genera una playlist M3U
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com/link/24werdqrx/01.php"
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico la pagina...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # Estrai il contenuto della pagina
        content = await page.content()

        # Troviamo ogni blocco di eventi che inizia con <p> e contiene le informazioni delle partite.
        partite_block = re.findall(r'<p>(.*?)</p>\s*<time datetime=".*?">(.*?)</time>.*?<time', content, re.DOTALL)

        print(f"[DEBUG] Partite trovate: {len(partite_block)}")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            for partita_info in partite_block:
                competizione = partita_info[0].strip()
                orario = partita_info[1].strip()

                # Trova la partita e i relativi canali
                partita_match = re.search(r'(.+?\svs\s.+?)\s*<a href=', competizione)
                if partita_match:
                    partita = partita_match.group(1)
                    
                    # Trova i canali
                    canali_match = re.findall(r'<a href="(acestream://.*?)" rel="nofollow">(.*?)</a>', content)
                    
                    if not canali_match:  # Se non ci sono canali, non scrivere
                        print(f"[WARNING] Nessun link AceStream trovato per {partita}")
                        continue
                    
                    # Scrivi ogni link AceStream nel file M3U
                    for ace_link, channel_title in canali_match:
                        f.write(f'#EXTINF:-1 group-title="{competizione} - {partita} ({orario})", {channel_title.strip()}\n{ace_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
