#!/usr/bin/env python3
"""
Platinsport AceStream Scraper Debug Version
- Estrae le partite e i relativi link AceStream con debug
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
        
        # Debug: Stampa il contenuto HTML per vedere cosa c'è
        print(content[:1000])  # Stampa solo i primi 1000 caratteri per non sovraccaricare l'output.

        # Trova gli eventi delle partite
        partite = re.findall(
            r'<p>(.*?)</p>\s*<time datetime=".*?">(.*?)</time>\s*(.+? vs .+?)\s*(<a href="acestream://.*?</a>)', 
            content, re.DOTALL
        )

        # Debug: Controlla quante partite sono state trovate
        print(f"[DEBUG] Partite trovate: {len(partite)}")
        
        # Scrivi il file M3U se ci sono partite trovate
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            
            for partita_info in partite:
                competizione, orario, partita, canali = partita_info
                competizione = competizione.strip()
                orario = orario.strip()
                partita = partita.strip()

                # Debug: mostra il dettaglio della partita
                print(f"[DEBUG] Competizione: {competizione}, Orario: {orario}, Partita: {partita}")

                # Trova tutti i link AceStream nei canali
                links = re.findall(r'href="(acestream://.*?)".*?>(.*?)</a>', canali)
                for ace_link, channel_title in links:
                    f.write(f'#EXTINF:-1 group-title="{competizione} - {partita} ({orario})", {channel_title.strip()}\n{ace_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
