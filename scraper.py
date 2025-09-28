#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "file:///C:/Users/TUO_PC/Desktop/test.html"  # usa il tuo file HTML locale di test

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        # Trova i blocchi di testo con le partite
        eventi = await page.locator("body").all_text_contents()

        print("=== CONTENUTO PAGINA ===")
        for e in eventi:
            print(e)

        # Prova a catturare solo "Roma vs Hellas Verona"
        match = await page.locator("body").inner_text()
        print("\n=== MATCH TROVATI ===")
        for line in match.splitlines():
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
