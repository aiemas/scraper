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

        # Trova tutte le partite tipo "Team A Vs Team B"
        matches = re.findall(r'\b[A-Z][A-Za-z\s]*\s+Vs\s+[A-Z][A-Za-z\s]*\b', content, flags=re.IGNORECASE)

        print("#EXTM3U")

        # Trova tutti i link AceStream
        link_elements = await page.query_selector_all("a")
        ace_links = []
        for link_el in link_elements:
            href = await link_el.get_attribute("href")
            if href and "ace/getstream" in href:
                ace_links.append(href)

        # Associa i link alle partite (uno o più link per partita)
        # Se i link sono multipli per partita, qui li distribuiamo in sequenza
        idx = 0
        for match_name in matches:
            match_name = match_name.strip()
            if idx >= len(ace_links):
                break
            # Prendi almeno un link per ogni match, se ce ne sono di più li aggiungi sotto
            links_for_match = ace_links[idx:idx+3]  # esempio: max 3 link per partita
            for i, link in enumerate(links_for_match):
                if i == 0:
                    print(f"#EXTINF:-1,{match_name}")
                else:
                    print(f"#EXTINF:-1,{match_name} (link {i+1})")
                print(link)
            idx += len(links_for_match)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
