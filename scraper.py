#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import re

PLATIN_URL = "https://www.platinsport.com/link/28sunxqrx/01.php"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        content = await page.content()

        # Trova tutte le partite principali (Livingston vs Rangers ...)
        matches = re.findall(r'\b[A-Z][A-Z\s]*\s+vs\s+[A-Z][A-Z\s]*\b', content, flags=re.IGNORECASE)
        # Trova tutti i link AceStream
        links = re.findall(r'http://127\.0\.0\.1:6878/ace/getstream\?id=[a-f0-9]+', content)

        if not matches or not links:
            print("Nessuna partita o link trovati")
            await browser.close()
            return

        # Iniziamo la playlist M3U
        m3u = ["#EXTM3U"]

        link_index = 0
        for match in matches:
            match_name = match.title().strip()
            # Primo link della partita
            if link_index < len(links):
                m3u.append(f"#EXTINF:-1,{match_name}")
                m3u.append(links[link_index])
                link_index += 1
            # Link extra (associamo due per partita se presenti, si può cambiare)
            extra_count = 2  # quanti Channel extra per partita vuoi aggiungere
            for i in range(extra_count):
                if link_index < len(links):
                    m3u.append(f"#EXTINF:-1,{match_name} (Channel {i+2})")
                    m3u.append(links[link_index])
                    link_index += 1

        # Stampa la playlist finale
        print("\n".join(m3u))

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
