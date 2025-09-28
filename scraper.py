#!/usr/bin/env python3
import asyncio
import re
from playwright.async_api import async_playwright

DIRECT_URL = "https://www.platinsport.com/link/28sunxqrx/01.php"
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_user_agent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        )
        print("[INFO] Carico pagina dei canali...")
        await page.goto(DIRECT_URL, timeout=120000)
        await page.wait_for_load_state("networkidle")

        # Seleziona container principale
        container = await page.query_selector(".myDiv1")
        if not container:
            print("[ERRORE] Container principale non trovato")
            await browser.close()
            return

        children = await container.query_selector_all(":scope > *")
        if not children:
            print("[ERRORE] Nessun elemento trovato")
            await browser.close()
            return

        print("[INFO] Analizzo gli elementi e genero playlist...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            current_match = None
            first_channel = True

            for el in children:
                tag_name = await el.evaluate("e => e.tagName")
                text = await el.evaluate("e => e.textContent.trim()")
                
                if tag_name in ["STRONG", "H5", "DIV", "P"]:
                    # Controlla se contiene "vs" -> è il nome della partita
                    if "vs" in text:
                        current_match = text
                        first_channel = True

                elif tag_name == "A":
                    href = await el.get_attribute("href")
                    if href and href.startswith("acestream://"):
                        channel_title = text if len(text) > 0 else "Channel"
                        content_id = href.replace("acestream://", "")
                        http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"

                        # Se è il primo canale della partita, scrivi il nome della partita
                        if first_channel and current_match:
                            f.write(f'#EXTINF:-1,{current_match}\n{http_link}\n')
                            first_channel = False
                        else:
                            f.write(f'#EXTINF:-1,{channel_title}\n{http_link}\n')

        print(f"[OK] Playlist generata in {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
