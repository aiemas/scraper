#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import re

PLATIN_URL = "https://www.platinsport.com/link/28sunxqrx/01.php"  # pagina diretta
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico la pagina...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")  # aspetta che JS finisca

        # Prendi tutto il contenuto della pagina
        content = await page.content()

        # Trova tutte le partite (es. "Livingston vs Rangers")
        matches = re.findall(r'\b[A-Z][A-Z\s]*\s+vs\s+[A-Z][A-Z\s]*\b', content, flags=re.IGNORECASE)
        if not matches:
            print("[WARN] Nessuna partita trovata")
            matches = []

        # Prendi tutti i link AceStream dalla pagina
        ace_links = re.findall(r'acestream://[a-f0-9]{40,}', content, flags=re.IGNORECASE)
        if not ace_links:
            print("[WARN] Nessun link AceStream trovato")

        # Scrivi la playlist M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            for i, link in enumerate(ace_links):
                # Primo canale di ogni partita ha il nome della partita
                if i < len(matches):
                    title = matches[i].title()
                else:
                    title = f"Channel {i+1}"

                content_id = link.replace("acestream://", "")
                http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                f.write(f'#EXTINF:-1,{title}\n{http_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE} con {len(ace_links)} canali")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
