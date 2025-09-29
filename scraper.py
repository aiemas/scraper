#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com/link/29monorx/01.php"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # visibile per debug
        page = await browser.new_page()
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(3000)  # aspetto ancora JS

        # 1. Cerca nel DOM principale
        content = await page.content()
        if "acestream://" in content:
            print("[DEBUG] trovato in DOM principale")

        # 2. Cerca negli iframe
        for frame in page.frames:
            try:
                html = await frame.content()
                if "acestream://" in html:
                    print("[DEBUG] trovato in iframe:", frame.url)
            except:
                pass

        # 3. Intercetta XHR responses
        async def handle_response(resp):
            try:
                txt = await resp.text()
                if "acestream://" in txt:
                    print("[DEBUG] trovato in response:", resp.url)
            except:
                pass

        page.on("response", handle_response)

        # tieni aperto un po’ per intercettare XHR
        await page.wait_for_timeout(10000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
