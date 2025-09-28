#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import re

PLATIN_URL = "https://www.platinsport.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")  # aspetta che JS finisca

        # Prendi tutto il contenuto della pagina
        content = await page.content()

        # Trova pattern tipo "LIVINGSTON VS RANGERS" (case insensitive)
        matches = re.findall(r'\b[A-Z][A-Z\s]*\s+vs\s+[A-Z][A-Z\s]*\b', content, flags=re.IGNORECASE)

        if matches:
            for match in matches:
                print(match.strip())
        else:
            print("Nessuna partita trovata")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
