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

        # Trova tutti i container principali della pagina
        containers = await page.query_selector_all("body *")

        grouped_links = {}
        current_match = None

        for el in containers:
            text = (await el.inner_text()).strip()

            # Controlla se è una partita
            match = re.match(r'([A-Z][A-Za-z\s]+)\s+vs\s+([A-Z][A-Za-z\s]+)', text, flags=re.IGNORECASE)
            if match:
                current_match = match.group(0).title()
                grouped_links[current_match] = []
                continue

            # Se abbiamo una partita corrente, cerca link AceStream dentro questo elemento
            if current_match:
                links = await el.query_selector_all("a[href^='acestream://']")
                for link_el in links:
                    href = await link_el.get_attribute("href")
                    if href:
                        grouped_links[current_match].append(href)

        # Scrivi la playlist M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for match, links in grouped_links.items():
                for idx, link in enumerate(links):
                    title = f"{match} - Channel {idx+1}" if len(links) > 1 else match
                    content_id = link.replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    f.write(f'#EXTINF:-1 group-title="{match}",{title}\n{http_link}\n')

        total_links = sum(len(v) for v in grouped_links.values())
        print(f"[OK] Playlist salvata in {OUTPUT_FILE} con {total_links} canali")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
