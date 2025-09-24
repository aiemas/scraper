#!/usr/bin/env python3
"""
Platinsport scraper definitivo
- Estrae tutte le partite e i relativi link AceStream
- Genera playlist M3U con eventi e canali
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # Prendi tutti gli elementi della pagina
        children = await page.query_selector_all(".myDiv1 *")
        print(f"[INFO] Trovati {len(children)} elementi nella pagina")

        partite_trovate = []
        link_ace_dict = {}  # Dizionario per conservare le partite e i loro link

        # Itera sugli elementi e cerca pattern "orario" seguito da "Squadra vs Squadra"
        for i, el in enumerate(children):
            text = await el.evaluate("e => e.textContent").strip()
            
            # Cerca righe con orario
            match_time = re.match(r"(\d{1,2}:\d{2})\s*(.+)", text)
            if match_time:
                # Prova a leggere la riga successiva
                if i + 1 < len(children):
                    next_text = await children[i + 1].evaluate("e => e.textContent").strip()
                    if "vs" in next_text:
                        partita = f"{match_time.group(1)} {next_text}"
                        partite_trovate.append(partita)
                        link_ace_dict[partita] = []  # Inizializza una lista per gli ace links

            # Estrai i link AceStream 
            if text.startswith("acestream://"):
                # Aggiungi il link AceStream alla partita corretta
                for partita in partite_trovate:
                    if match_time:
                        link_ace_dict[partita].append(text)

        # Scrivi il file M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for partita, links in link_ace_dict.items():
                if links:
                    for link in links:
                        f.write(f'#EXTINF:-1 group-title="{partita}",{link}\nhttp://127.0.0.1:6878/ace/getstream?id={link.split("://")[1]}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
