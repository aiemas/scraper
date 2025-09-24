#!/usr/bin/env python3
"""
Platinsport scraper definitivo con link AceStream
- Trova link bc.vc vicino agli eventi
- Estrae il link diretto alla pagina /link/... dei canali AceStream
- Recupera tutti i link AceStream dalle chiamate XHR
- Stampa a video partite e link senza creare file M3U
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

        final_url = get_direct_link(bcvc_url)
        print(f"[INFO] Link diretto alla pagina dei canali: {final_url}")

        await page.goto(final_url, timeout=60000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(5000)  # attendi 5 secondi per JS

        # seleziona tutti gli elementi principali
        container = await page.query_selector(".myDiv1")
        if not container:
            print("[ERRORE] Container principale non trovato")
            await browser.close()
            return

        children = await container.query_selector_all(":scope > *")
        print(f"[INFO] Trovati {len(children)} elementi nella pagina")

        # memorizza partite e link
        events = []

        current_event = None

        for i, el in enumerate(children):
            tag_name = await el.evaluate("e => e.tagName")
            text = (await el.evaluate("e => e.textContent")).strip()

            # cerca orario + partita
            match = re.match(r"(\d{1,2}:\d{2})\s+(.+vs.+)", text)
            if match:
                current_event = f"{match.group(1)} {match.group(2)}"
                events.append({"event": current_event, "links": []})
                continue

            # cerca link AceStream nei tag <a>
            if tag_name == "A":
                href = await el.get_attribute("href")
                if href and href.startswith("acestream://") and current_event:
                    content_id = href.replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    events[-1]["links"].append(http_link)

        # stampa risultati
        print("[OK] Partite e link trovati:")
        for ev in events:
            print(ev["event"])
            if ev["links"]:
                for l in ev["links"]:
                    print(" ", l)
            else:
                print("  Nessun link AceStream trovato")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
