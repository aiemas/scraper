#!/usr/bin/env python3
"""
Platinsport scraper aggiornato
- Trova link AceStream vicino agli eventi
- Recupera orario e nome partita
- Genera playlist M3U con group-title = "HH:MM Team1 vs Team2"
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

        # trova il contenitore principale
        container = await page.query_selector("div.content")

        # recupera tutti i figli
        children = await container.query_selector_all(":scope > *")

        with open(OUTPUT, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            current_time = None
            current_match = None
            current_group = None

            for el in children:
                tag_name = await el.evaluate("e => e.tagName")
                text = await el.evaluate("e => e.textContent.trim()")

                # cattura l'orario
                if tag_name == "TIME":
                    dt = await el.get_attribute("datetime")
                    if dt and len(dt) >= 16:
                        current_time = dt[11:16]  # estrae HH:MM

                # cattura la partita (Team1 vs Team2)
                elif tag_name in ["DIV", "P", "SPAN"]:
                    if "vs" in text:
                        current_match = text
                        if current_time and current_match:
                            current_group = f"{current_time} {current_match}"

                # cattura i link acestream
                elif tag_name == "A":
                    href = await el.get_attribute("href")
                    if href and href.startswith("acestream://") and current_group:
                        channel_title = text if text else "Channel"
                        content_id = href.replace("acestream://", "")
                        http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                        f.write(f'#EXTINF:-1 group-title="{current_group}",{channel_title}\n{http_link}\n')

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
