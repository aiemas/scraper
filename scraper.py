#!/usr/bin/env python3
"""
Platinsport scraper con Playwright
- Estrae i link AceStream
- Usa come group-title il nome della partita (es: "Roma vs Hellas Verona")
"""

import asyncio
from playwright.async_api import async_playwright

URL = "https://platinsport.com/schedule.html"
OUTPUT = "playlist.m3u"

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL)

        container = await page.query_selector("div.content")
        children = await container.query_selector_all(":scope > *")

        with open(OUTPUT, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            current_match = None

            for el in children:
                tag_name = await el.evaluate("e => e.tagName") if await el.evaluate("e => e.tagName") else None
                text = await el.evaluate("e => e.textContent.trim()")

                # Se il testo contiene "vs", consideralo come nome partita
                if "vs" in text and len(text) < 80:  # filtro per non prendere stringhe troppo lunghe
                    current_match = text

                # Se è un link AceStream e abbiamo già il match
                if tag_name == "A":
                    href = await el.get_attribute("href")
                    if href and href.startswith("acestream://") and current_match:
                        channel_title = text if text else "Channel"
                        content_id = href.replace("acestream://", "")
                        http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                        f.write(f'#EXTINF:-1 group-title="{current_match}",{channel_title}\n{http_link}\n')

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
