#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://www.platinsport.com/link/28sunxqrx/01.php"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        # Attendi che la pagina sia completamente caricata
        await page.wait_for_selector("body")

        # Trova tutte le righe di testo
        lines = await page.locator("body").all_text_contents()

        print("=== NOMI PARTITE ===")
        for line in lines:
            if "vs" in line:
                print(line.strip())

        # Prendi tutti i link AceStream
        print("\n=== LINK ACESTREAM ===")
        links = await page.locator("a[href^='acestream://']").all()
        for l in links:
            href = await l.get_attribute("href")
            text = await l.inner_text()
            print(text.strip(), href)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
