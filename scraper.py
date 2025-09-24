#!/usr/bin/env python3
"""
Platinsport scraper definitivo
- Trova link bc.vc vicino agli eventi
- Estrae il link diretto alla pagina /link/... dei canali AceStream
- Recupera tutti i link AceStream
- Genera playlist M3U gerarchica con link HTTP per VLC/AceStream
    - gruppo = partita/evento + orario + squadra vs squadra
    - canali = link AceStream via HTTP locale
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"

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

        # selezioniamo tutti gli elementi dentro il container principale (es. myDiv1)
        container = await page.query_selector(".myDiv1")
        if not container:
            print("[ERRORE] Container principale non trovato")
            await browser.close()
            return

        children = await container.query_selector_all(":scope > *")
        if not children:
            print("[ERRORE] Nessun elemento trovato nella pagina dei canali")
            await browser.close()
            return

        print("[INFO] Analizzo gli elementi per costruire playlist gerarchica...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            current_group = "Unknown Event"
            buffer_count = 0  # contatore per leggere il nome della partita 3 righe dopo competizione

            for el in children:
                tag_name = await el.evaluate("e => e.tagName")
                text = (await el.evaluate("e => e.textContent")).strip()

                # logica per prendere il nome della partita 3 righe dopo competizione
                if buffer_count > 0:
                    buffer_count -= 1
                    if buffer_count == 0:
                        current_group = text
                        print(f"[GROUP] Nuovo gruppo: {current_group}")
                        continue

                # se trovi competizione, prepara a leggere 3 righe dopo
                if tag_name == "P" and "League" in text:
                    buffer_count = 3
                    continue

                # se è un link AceStream, aggiungi alla playlist
                if tag_name == "A":
                    href = await el.get_attribute("href")
                    if href and href.startswith("acestream://"):
                        channel_title = text if len(text) > 0 else "Channel"
                        content_id = href.replace("acestream://", "")
                        http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                        f.write(f'#EXTINF:-1 group-title="{current_group}",{channel_title}\n{http_link}\n')

        print(f"[OK] Playlist gerarchica salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
