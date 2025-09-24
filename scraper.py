#!/usr/bin/env python3
"""
Platinsport scraper
- Stampa a video tutte le partite trovate nella pagina e i relativi link AceStream.
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
                # Prova a leggere la riga successiva
                if i + 1 < len(children):
                    next_text = (await children[i + 1].evaluate("e => e.textContent")).strip()
                    if "vs" in next_text:
                        partita = f"{match_time.group(1)} {next_text}"
                        partite_trovate.append(partita)

                        # Estrai i link AceStream dalla stessa sezione
                        # Ora guardiamo anche i tag <a> nei prossimi due elementi
                        for j in range(i + 2, min(i + 4, len(children))):
                            link_elements = await children[j].query_selector_all("a[href^='acestream://']")
                            for link_el in link_elements:
                                link_text = await link_el.evaluate("e => e.textContent")
                                link_href = await link_el.get_attribute("href")
                                if link_href:
                                    print(f"[INFO] Partita: {partita}, Link AceStream: {link_href} ({link_text})")

        if partite_trovate:
            print("[OK] Partite trovate:")
            for p in partite_trovate:
                print(p)
        else:
            print("[INFO] Nessuna partita trovata")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
