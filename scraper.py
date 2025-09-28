#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import re

# URL della pagina diretta che ci hai fornito
PLATIN_URL = "https://www.platinsport.com/link/28sunxqrx/01.php"

# File M3U di output
OUTPUT_FILE = "playlist.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        # Contenuto della pagina
        content = await page.content()

        # Trova tutte le partite (pattern tipo "Team A Vs Team B")
        matches = re.findall(r'\b[A-Z][A-Za-z\s]*\s+Vs\s+[A-Z][A-Za-z\s]*\b', content, flags=re.IGNORECASE)

        # Trova tutti i link "Channel" (in ordine, così li assoceremo alle partite)
        links = re.findall(r'(http://127\.0\.0\.1:6878/ace/getstream\?id=[a-f0-9]+)', content)

        if not matches or not links:
            print("Nessuna partita o link trovati")
            await browser.close()
            return

        # Scrittura M3U
        with open(OUTPUT_FILE, "w") as f:
            f.write("#EXTM3U\n")
            
            # Assumiamo che ci siano N link per partita in ordine
            links_per_match = len(links) // len(matches)
            extra_links = len(links) % len(matches)
            idx = 0

            for i, match in enumerate(matches):
                f.write(f"#EXTINF:-1,{match.strip()}\n")
                
                # Numero di link da associare a questa partita
                n_links = links_per_match + (1 if i < extra_links else 0)
                
                for _ in range(n_links):
                    f.write(links[idx] + "\n")
                    idx += 1

        print(f"Playlist generata: {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
