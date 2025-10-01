#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import re

PLATIN_URL = "https://www.platinsport.com/link/01wedxrq/01.php"
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico la pagina...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        content = await page.content()

        # Trova blocchi: partita + link vicini
        pattern = re.compile(
            r'([A-Z][A-Z\s]*\s+vs\s+[A-Z][A-Z\s]*)(.*?)((?=</div)|(?=<br)|$)',
            flags=re.IGNORECASE | re.DOTALL
        )

        grouped_links = {}
        for match in pattern.finditer(content):
            match_name = match.group(1).title().strip()
            block = match.group(2)

            # trova i link in questo blocco
            ace_links = re.findall(r'acestream://[a-f0-9]{40,}', block, flags=re.IGNORECASE)
            if ace_links:
                grouped_links[match_name] = ace_links

        if not grouped_links:
            print("[WARN] Nessuna partita con link trovata!")

        # Scrivi la playlist M3U
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for match, links in grouped_links.items():
                for idx, link in enumerate(links):
                    title = f"{match} - Channel {idx+1}" if len(links) > 1 else match
                    content_id = link.replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    f.write(f'#EXTINF:-1 group-title="{match}",{title}\n{http_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE} con {sum(len(v) for v in grouped_links.values())} canali")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
