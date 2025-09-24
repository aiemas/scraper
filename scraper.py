#!/usr/bin/env python3
"""
Platinsport scraper debug
- Cerca tutti gli eventi in formato partita
- Non crea file M3U, stampa solo ciò che trova
- Scopo: capire se il selettore funziona
"""

import asyncio
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        # Prendi tutto il body invece di un container specifico
        container = await page.query_selector("body")
        if not container:
            print("[ERRORE] Body non trovato")
            await browser.close()
            return

        children = await container.query_selector_all("*")
        print(f"[INFO] Trovati {len(children)} elementi nella pagina")

        # Scansione elementi alla ricerca di testo in formato "orario Team1 vs Team2"
        for el in children:
            text = await el.evaluate("e => e.textContent.trim()")
            # regex per catturare orario + partita tipo "20:45 Team1 vs Team2"
            if text:
                import re
                match = re.match(r"(\d{1,2}:\d{2})\s+(.+vs.+)", text)
                if match:
                    print(f"[MATCH] {match.group(1)} {match.group(2)}")

        await browser.close()
        print("[OK] Analisi completata")

if __name__ == "__main__":
    asyncio.run(main())
