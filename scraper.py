#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import re

PLATIN_URL = "https://www.platinsport.com/link/28sunxqrx/01.php"
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico la pagina...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        # Trova tutti i container principali
        containers = await page.query_selector_all("body *")  # possiamo restringere se serve

        playlist = []
        current_match = None

        for el in containers:
            text = (await el.inner_text()).strip()

            # Controlla se il testo è una partita
            match = re.match(r'([A-Z][A-Za-z\s]+)\s+vs\s+([A-Z][A-Za-z\s]+)', text, flags=re.IGNORECASE)
            if match:
                current_match = match.group(0).title()
                continue

            # Se abbiamo trovato una partita, cerchiamo link AceStream dentro questo elemento
            links = await el.query_selector_all("a[href^='acestream://']")
            for link_el in links:
                href = await link_el.get_attribute("href")
                if href:
                    content_id = href.replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    title = text if text else "Channel"
                    playlist.append((current_match if current_match else "Unknown Event", title, http_link))

        # Scrivi la playlist M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for group, title, link in playlist:
                f.write(f'#EXTINF:-1 group-title="{group}",{title}\n{link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE} con {len(playlist)} canali")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
