#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # Prendi tutti i paragrafi e div principali
        elements = await page.query_selector_all(".myDiv1 > *")

        for el in elements:
            text = await el.evaluate("e => e.innerText")
            if text and "vs" in text.lower():
                print(text.strip())

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
