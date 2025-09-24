#!/usr/bin/env python3
"""
Platinsport scraper debug
- Stampa a video tutte le partite trovate nella pagina
- Non crea file M3U
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # Prendi tutti gli elementi della pagina
        children = await page.query_selector_all("body *")
        print(f"[INFO] Trovati {len(children)} elementi nella pagina")

        partite_trovate = []

        # Itera sugli elementi e cerca pattern "orario" seguito da "Squadra vs Squadra"
        for i, el in enumerate(children):
            text = (await el.evaluate("e => e.textContent")).strip()
            # cerca righe con orario
            match_time = re.match(r"(\d{1,2}:\d{2})\s*(.*)", text)
            if match_time:
                # prova a leggere la riga successiva
                if i + 1 < len(children):
                    next_text = (await children[i + 1].evaluate("e => e.textContent")).strip()
                    if "vs" in next_text:
                        partita = f"{match_time.group(1)} {next_text}"
                        partite_trovate.append(partita)

        if partite_trovate:
            print("[OK] Partite trovate:")
            for p in partite_trovate:
                print(p)
        else:
            print("[INFO] Nessuna partita trovata")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
