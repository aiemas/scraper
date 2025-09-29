#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import re

PLATIN_URL = "https://www.platinsport.com/link/29monorx/01.php"
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico la pagina...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        content = await page.content()

        # Trova tutte le partite
        matches = re.findall(r'\b[A-Z][A-Z\s]*\s+vs\s+[A-Z][A-Z\s]*\b', content, flags=re.IGNORECASE)
        matches = [m.title() for m in matches]
        if not matches:
            print("[WARN] Nessuna partita trovata")
            matches = []

        # Trova tutti i link AceStream
        ace_links = re.findall(r'acestream://[a-f0-9]{40,}', content, flags=re.IGNORECASE)
        if not ace_links:
            print("[WARN] Nessun link AceStream trovato")

        # Raggruppa i link per partita
        grouped_links = {}
        if matches:
            links_per_match = max(1, len(ace_links) // len(matches))
            for i, match in enumerate(matches):
                start = i * links_per_match
                end = (i + 1) * links_per_match
                grouped_links[match] = ace_links[start:end]
        else:
            grouped_links["Unknown Event"] = ace_links

        # Scrivi la playlist M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for match, links in grouped_links.items():
                for idx, link in enumerate(links):
                    title = f"{match} - Channel {idx+1}" if len(links) > 1 else match
                    content_id = link.replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    f.write(f'#EXTINF:-1 group-title="{match}",{title}\n{http_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE} con {len(ace_links)} canali")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
