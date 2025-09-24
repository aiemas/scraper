#!/usr/bin/env python3
"""
Platinsport AceStream Scraper
- Estrae le partite e i relativi link AceStream
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

        # Trova gli eventi delle partite
        partite = re.findall(
            r'<p>(.*?)</p>.*?<time datetime=".*?">(.*?)</time>\s*(.+?\svs.+?)</.*?>(.*?)</a>', 
            content, re.DOTALL
        )
        
        # Scrivi il file M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            for partita_info in partite:
                competizione, orario, partita, canali = partita_info
                # Cleanup del testo
                competizione = competizione.strip()
                orario = orario.strip()
                partita = partita.strip()
                
                # Trova tutti i link AceStream nei canali
                links = re.findall(r'<a href="(acestream://.*?)".*?>(.*?)</a>', canali)
                for link in links:
                    ace_link, channel_title = link
                    f.write(f'#EXTINF:-1 group-title="{competizione} - {partita} ({orario})", {channel_title.strip()}\n{ace_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
