#!/usr/bin/env python3
"""
Platinsport scraper definitivo (solo stampa a video)
- Trova link bc.vc vicino agli eventi
- Estrae il link diretto alla pagina /link/... dei canali AceStream
- Recupera tutti i link AceStream
- Stampa a video partita + link AceStream
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"

def get_direct_link(bcvc_url: str) -> str:
    """Estrae il link diretto alla pagina /link/... dalla URL bc.vc"""
    match = re.search(r"https?://www\.platinsport\.com/link/[^\s\"'>]+", bcvc_url)
    if match:
        return match.group(0)
    return bcvc_url  # fallback

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # estrai tutti i link bc.vc dal DOM
        content = await page.content()
        bcvc_links = re.findall(r"https?://bc\.vc/[^\s\"'>]+", content)

        if not bcvc_links:
            print("[ERRORE] Nessun link bc.vc trovato")
            await browser.close()
            return

        bcvc_url = bcvc_links[0]
        print(f"[INFO] Trovato link bc.vc: {bcvc_url}")

        # estrai link diretto alla pagina dei canali AceStream
        final_url = get_direct_link(bcvc_url)
        print(f"[INFO] Link diretto alla pagina dei canali: {final_url}")

        # apri la pagina /link/... e cerca AceStream
        print("[INFO] Carico pagina finale e cerco link AceStream...")
        await page.goto(final_url, timeout=60000)
        await page.wait_for_load_state("networkidle")

        # selezioniamo tutti gli elementi dentro il container principale
        container = await page.query_selector(".myDiv1")
        if not container:
            print("[ERRORE] Container principale non trovato")
            await browser.close()
            return

        children = await container.query_selector_all(":scope > *")
        print(f"[INFO] Trovati {len(children)} elementi nella pagina")

        current_match = None
        matches_found = []

        for el in children:
            text = await el.evaluate("e => e.textContent.trim()")
            tag_name = await el.evaluate("e => e.tagName")

            # Controlla se il testo è una partita (orario + squadra vs squadra)
            match = re.match(r"(\d{1,2}:\d{2})\s+(.+vs.+)", text)
            if match:
                current_match = f"{match.group(1)} {match.group(2)}"
                matches_found.append((current_match, []))
                continue

            # Se è un link AceStream e c'è già una partita corrente
            if tag_name == "A" and current_match:
                href = await el.get_attribute("href")
                if href and href.startswith("acestream://"):
                    content_id = href.replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    matches_found[-1][1].append(http_link)

        # Stampa a video tutte le partite con i link AceStream
        print("[OK] Partite e link trovati:")
        for match, links in matches_found:
            print(match)
            if links:
                for link in links:
                    print(f"  {link}")
            else:
                print("  Nessun link AceStream trovato")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
