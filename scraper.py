#!/usr/bin/env python3
"""
Platinsport scraper definitivo - DEBUG
- Cerca nella pagina solo gli eventi in formato "Squadra vs Squadra"
- Stampa a video ciò che trova senza creare alcun file M3U
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

        # selezioniamo tutti gli elementi dentro il container principale (es. myDiv1)
        container = await page.query_selector(".myDiv1")
        if not container:
            print("[ERRORE] Container principale non trovato")
            await browser.close()
            return

        children = await container.query_selector_all(":scope > *")
        if not children:
            print("[ERRORE] Nessun elemento trovato nella pagina")
            await browser.close()
            return

        print("[INFO] Cerco eventi in formato partita (Team1 vs Team2)...")

        next_is_match = False

        for el in children:
            text = (await el.evaluate("e => e.textContent")).strip()
            tag_name = await el.evaluate("e => e.tagName")

            # se trovi orario, la prossima riga potrebbe essere la partita
            if tag_name == "TIME" and re.match(r"\d{1,2}:\d{2}", text):
                next_is_match = True
                continue

            # se flag attivo e testo contiene "vs", allora è la partita
            if next_is_match and "vs" in text:
                print(f"[EVENTO TROVATO] {text}")
                next_is_match = False

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
