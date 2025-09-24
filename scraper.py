#!/usr/bin/env python3
"""
Platinsport scraper - stampa solo partite con orario + squadre
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
        await page.wait_for_load_state("domcontentloaded")

        # prendiamo tutto il contenuto del container principale
        container = await page.query_selector(".myDiv1")
        if not container:
            print("[ERRORE] Container principale non trovato")
            await browser.close()
            return

        children = await container.query_selector_all(":scope > *")
        print(f"[INFO] Trovati {len(children)} elementi nella pagina")

        partite_trovate = 0

        for i, el in enumerate(children):
            tag_name = await el.evaluate("e => e.tagName")
            text = (await el.evaluate("e => e.textContent")).strip()

            # se è un nodo <time>, prendiamo il testo successivo come partita
            if tag_name == "TIME":
                orario = text
                # proviamo a prendere il testo del nodo successivo
                if i + 1 < len(children):
                    next_text = (await children[i + 1].evaluate("e => e.textContent")).strip()
                    if "vs" in next_text:
                        print(f"{orario} - {next_text}")
                        partite_trovate += 1

        print(f"[OK] Analisi completata. Partite trovate: {partite_trovate}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
