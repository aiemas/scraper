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

        print("#EXTM3U")

        # Trova tutti i blocchi di partite
        match_blocks = await page.query_selector_all(".event-block")  # esempio di classe, da adattare al sito reale

        for block in match_blocks:
            # Prendi il titolo della partita
            title_el = await block.query_selector(".event-title")  # classe esempio
            if title_el:
                match_name = (await title_el.inner_text()).strip()
            else:
                # fallback regex dal contenuto del blocco
                block_content = await block.inner_html()
                match = re.search(r'\b[A-Z][A-Za-z\s]*\s+Vs\s+[A-Z][A-Za-z\s]*\b', block_content, flags=re.IGNORECASE)
                if match:
                    match_name = match.group(0)
                else:
                    continue

            # Prendi tutti i link AceStream dentro il blocco
            link_elements = await block.query_selector_all("a")
            ace_links = []
            for link_el in link_elements:
                href = await link_el.get_attribute("href")
                if href and "ace/getstream" in href:
                    ace_links.append(href)

            # Stampa partita e link associati
            for i, link in enumerate(ace_links):
                if i == 0:
                    print(f"#EXTINF:-1,{match_name}")
                else:
                    print(f"#EXTINF:-1,{match_name} (link {i+1})")
                print(link)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
