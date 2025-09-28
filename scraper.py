#!/usr/bin/env python3
import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # Prendi tutto il testo del container principale
        container = await page.query_selector(".myDiv1")
        if not container:
            print("Container principale non trovato")
            await browser.close()
            return

        content_text = await container.evaluate("e => e.innerText")

        # Trova tutte le partite tipo "TeamA VS TeamB"
        matches = re.findall(r"\b([A-Z0-9 ]+)\s+VS\s+([A-Z0-9 ]+)\b", content_text, flags=re.IGNORECASE)

        for match in matches:
            print(f"{match[0].strip()} VS {match[1].strip()}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
