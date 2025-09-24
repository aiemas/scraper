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

        # Trova tutti i dettagli delle partite
        eventi = re.findall(
            r'<p>(.*?)</p>\s*<time datetime=".*?">(.*?)</time>\s*(.+?\svs\s.+?)\s*(.*?)<time', 
            content, re.DOTALL
        )

        print(f"[DEBUG] Eventi trovati: {len(eventi)}")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            for evento in eventi:
                competizione, orario, partita, canali = evento
                competizione = competizione.strip()
                orario = orario.strip()
                partita = partita.strip()

                # Debug: mostra i dettagli del evento
                print(f"[DEBUG] Competizione: {competizione}, Orario: {orario}, Partita: {partita}")

                # Trova tutti i link AceStream nei canali
                link_regex = r'<a href="(acestream://.*?)" rel="nofollow">(.*?)</a>'
                links = re.findall(link_regex, canali)

                if not links:  # Se non ci sono link, non scrivere
                    print(f"[WARNING] Nessun link AceStream trovato per {partita}")
                    continue

                # Scrivi ogni link AceStream nel file M3U
                for ace_link, channel_title in links:
                    f.write(f'#EXTINF:-1 group-title="{competizione} - {partita} ({orario})", {channel_title.strip()}\n{ace_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
