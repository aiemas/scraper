#!/usr/bin/env python3
import asyncio
import re
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com/link/23dinqxz/01.php"
OUTPUT_FILE = "platinsport.m3u"
ACE_LOCAL = "http://127.0.0.1:6878/ace/getstream?id="

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("[INFO] Carico pagina dei canali Platinsport...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")

        content = await page.inner_text("body")
        lines = content.splitlines()

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            current_group = "Unknown Event"
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # match orario + vs
                if re.match(r"\d{2}:\d{2} .+ vs .+", line):
                    current_group = line
                    continue
                # match AceStream
                if "acestream://" in line:
                    content_id = line.split("acestream://")[1].strip()
                    http_link = f"{ACE_LOCAL}{content_id}"
                    f.write(f'#EXTINF:-1 group-title="{current_group}",{line}\n{http_link}\n')

        print(f"[OK] Playlist M3U salvata: {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
