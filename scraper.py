#!/usr/bin/env python3
"""
Platinsport scraper per il primo evento
- Estrae il primo evento dalla pagina
- Genera playlist M3U con le informazioni dell'evento e i canali AceStream
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"  # Usa il nome originale

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

        # selezioniamo il primo evento dentro il container principale (es. myDiv1)
        container = await page.query_selector(".myDiv1")
        if not container:
            print("[ERRORE] Container principale non trovato")
            await browser.close()
            return

        # Variabili per il primo evento
        channels = []
        first_event = None

        children = await container.query_selector_all(":scope > *")

        if not children:
            print("[ERRORE] Nessun elemento trovato nella pagina dei canali")
            await browser.close()
            return

        print("[INFO] Estrae il primo evento...")
        
        # Itera sugli elementi e cattura il primo evento
        for el in children:
            tag_name = await el.evaluate("e => e.tagName")
            text = await el.evaluate("e => e.textContent.trim()")

            # Estrai titolo partita e orario
            if tag_name == "P":
                match = re.search(r"(.+?)\s+vs\s+(.+)", text)
                if match:
                    team1 = match.group(1).strip()
                    team2 = match.group(2).strip()

                    # Recupera l'orario dalla tag <time>
                    time_element = await el.query_selector("time")
                    datetime = await time_element.evaluate("e => e.getAttribute('datetime')") if time_element else None
                    first_event = f"{datetime} - {team1} vs {team2}" if datetime else f"{team1} vs {team2}"

                    # Chiudi il ciclo dopo aver trovato il primo evento
                    break

        # Estrai i canali AceStream associati a questo evento
        if first_event:
            for el in children:
                tag_name = await el.evaluate("e => e.tagName")
                if tag_name == "A":
                    href = await el.get_attribute("href")
                    if href and href.startswith("acestream://"):
                        channel_title = text if len(text) > 0 else "Channel"
                        content_id = href.replace("acestream://", "")
                        http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                        channels.append((channel_title, http_link))

        # Scrivi il file M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if first_event:
                for channel_title, http_link in channels:
                    f.write(f'#EXTINF:-1 group-title="{first_event}",{channel_title}\n{http_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
