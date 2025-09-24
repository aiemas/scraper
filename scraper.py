#!/usr/bin/env python3
"""
Platinsport scraper debug con link AceStream
- Stampa a video tutte le partite trovate nella pagina
- Stampa anche i link AceStream per ciascuna partita
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

        i = 0
        while i < len(children):
            el = children[i]
            text = (await el.evaluate("e => e.textContent")).strip()
            # cerca righe con orario
            match_time = re.match(r"(\d{1,2}:\d{2})\s*(.*)", text)
            if match_time:
                # prova a leggere la riga successiva
                if i + 1 < len(children):
                    next_text = (await children[i + 1].evaluate("e => e.textContent")).strip()
                    if "vs" in next_text:
                        partita = f"{match_time.group(1)} {next_text}"
                        links = []
                        # scorri avanti per trovare tutti i link AceStream relativi a questa partita
                        j = i + 2
                        while j < len(children):
                            next_el = children[j]
                            next_tag = await next_el.evaluate("e => e.tagName")
                            next_href = await next_el.get_attribute("href") if next_tag == "A" else None
                            next_text2 = (await next_el.evaluate("e => e.textContent")).strip()
                            # se trovi un'altra partita, fermati
                            if re.match(r"\d{1,2}:\d{2}", next_text2) and "vs" in next_text2:
                                break
                            if next_href and next_href.startswith("acestream://"):
                                content_id = next_href.replace("acestream://", "")
                                http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                                links.append(http_link)
                            j += 1
                        partite_trovate.append((partita, links))
                        i = j - 1  # salta al prossimo elemento dopo i link
            i += 1

        if partite_trovate:
            print("[OK] Partite e link trovati:")
            for p, lks in partite_trovate:
                print(f"\n{p}")
                if lks:
                    for lk in lks:
                        print(f"  {lk}")
                else:
                    print("  Nessun link AceStream trovato")
        else:
            print("[INFO] Nessuna partita trovata")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
