#!/usr/bin/env python3
"""
Platinsport scraper definitivo
- Trova link bc.vc vicino agli eventi
- Estrae il link diretto alla pagina /link/... dei canali AceStream
- Recupera tutti i link AceStream
- Genera playlist M3U gerarchica con link HTTP per VLC/AceStream
    - gruppo = orario + squadra vs squadra
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
    return match.group(0) if match else bcvc_url  # fallback

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

        # Estrai informazioni
        matches = []
        children = await container.query_selector_all(":scope > *")
        
        if not children:
            print("[ERRORE] Nessun elemento trovato nella pagina dei canali")
            await browser.close()
            return

        print("[INFO] Estrae i link e le partite...")
        
        for el in children:
            tag_name = await el.evaluate("e => e.tagName")
            text = await el.evaluate("e => e.textContent.trim()")

            # Estrai le partite
            if tag_name == "P" and len(text) > 0:
                match = re.search(r"(.+?)\s+vs\s+(.+)", text)
                if match:
                    match_info = {
                        "team1": match.group(1).strip(),
                        "team2": match.group(2).strip(),
                        "time": await el.query_selector("time") or None
                    }
                    matches.append(match_info)

            # Estrai i link AceStream
            elif tag_name == "A":
                href = await el.get_attribute("href")
                if href and href.startswith("acestream://"):
                    channel_title = text if len(text) > 0 else "Channel"
                    content_id = href.replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    
                    # Aggiungi il link AceStream all'ultimo match trovato
                    if matches:
                        matches[-1].setdefault("channels", []).append((channel_title, http_link))

        # Scrivi il file M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for match in matches:
                if match["time"]:
                    datetime = await match["time"].evaluate("e => e.getAttribute('datetime')")
                    current_group = f"{datetime} - {match['team1']} vs {match['team2']}"
                    
                    if "channels" in match:
                        for channel in match["channels"]:
                            channel_title, http_link = channel
                            f.write(f'#EXTINF:-1 group-title="{current_group}",{channel_title}\n{http_link}\n')

        print(f"[OK] Playlist gerarchica salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
