#!/usr/bin/env python3
"""
Platinsport scraper corretto
- Gruppo = nome della partita (es: "Midtjylland vs Sturm Graz")
- Aggiunge tutti i link AceStream a quel gruppo
- Genera file M3U funzionante
"""

import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        # Aspetto che compaiano i link AceStream
        await page.wait_for_selector("a[href^='acestream://']", timeout=30000)

        # Prendo tutti i link AceStream
        ace_links = await page.query_selector_all("a[href^='acestream://']")
        if not ace_links:
            print("[ERRORE] Nessun link AceStream trovato")
            await browser.close()
            return

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")

            for link in ace_links:
                href = await link.get_attribute("href")
                text = (await link.evaluate("e => e.textContent")).strip()

                # Cerco il testo della partita più vicino al link
                parent_text = await link.evaluate("""
                    e => {
                        let el = e.parentElement;
                        while(el){
                            if(el.textContent && el.textContent.includes("vs")){
                                return el.textContent.trim();
                            }
                            el = el.parentElement;
                        }
                        return "Unknown Match";
                    }
                """)
                group_name = parent_text
                channel_title = text if text else "Channel"

                content_id = href.replace("acestream://", "")
                http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                f.write(f'#EXTINF:-1 group-title="{group_name}",{channel_title}\n{http_link}\n')

        print(f"[OK] Playlist salvata in {OUTPUT_FILE}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
