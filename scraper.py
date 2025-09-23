#!/usr/bin/env python3
"""
Platinsport scraper - playlist M3U gerarchica
- Gruppo = orario + partita
- Canali = link AceStream
- Trasformazione AceStream in link HTTP locale per VLC/AcePlayer
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
    return bcvc_url

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # estrai link bc.vc
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

        print("[INFO] Carico pagina dei canali AceStream...")
        await page.goto(final_url, timeout=60000)
        await page.wait_for_load_state("networkidle")

        # seleziona tutti i figli del container principale
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

        print("[INFO] Analizzo gli elementi e creo playlist M3U...")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            current_group = None

            for el in children:
                tag_name = await el.evaluate("e => e.tagName")
                text = await el.evaluate("e => e.textContent.trim()")

                # riga partita: orario + vs + squadra
                if re.match(r"^\d{1,2}:\d{2} .+ vs .+", text):
                    current_group = text
                    continue

                # link AceStream
                elif tag_name == "A":
                    href = await el.get_attribute("href")
                    if href and href.startswith("acestream://") and current_group:
                        channel_title = text if len(text) > 0 else "Channel"
                        content_id = href.replace("acestream://", "")
                        http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                        f.write(f'#EXTINF:-1 group-title="{current_group}",{channel_title}\n{http_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
