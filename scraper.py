import asyncio
from playwright.async_api import async_playwright

ACE_LOCAL = "http://127.0.0.1:6878/ace/getstream?id="

async def main():
    m3u8_lines = ["#EXTM3U"]
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.platinsport.com/link/23dinqxz/01.php")

        # Prendo tutto il contenuto testuale della pagina
        content = await page.inner_text("body")
        lines = content.splitlines()

        current_match = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Rilevo le righe con orario + partita
            if len(line) > 5 and ":" in line and "vs" in line:
                current_match = line
                continue
            # Rilevo i link AceStream
            if "acestream://" in line and current_match:
                ace_id = line.split("acestream://")[1].strip()
                m3u8_lines.append(f'#EXTINF:-1 group-title="{current_match}",{line}')
                m3u8_lines.append(f'{ACE_LOCAL}{ace_id}')

        await browser.close()

    # Scrivo il file M3U
    with open("platinsport.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u8_lines))

    print("M3U playlist creata: platinsport.m3u")

asyncio.run(main())
