import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.platinsport.com"

async def get_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL, timeout=60000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        eventi = [a["href"] for a in soup.select("a[href*='/link/']")]
        results = []

        for evento in eventi:
            print(f"[index] {evento}")
            await page.goto(evento, timeout=60000)

            try:
                # aspetta il bottone "Get Link" e clicca
                await page.wait_for_selector("a#getlink", timeout=15000)
                await page.click("a#getlink")
                await page.wait_for_load_state("networkidle")

                final_url = page.url
                print(f"[final] {final_url}")
                results.append(final_url)
            except Exception as e:
                print("Errore evento:", e)

        await browser.close()
        return results

def save_m3u(links):
    with open("platinsport.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for i, url in enumerate(links, 1):
            f.write(f"#EXTINF:-1,Evento {i}\n{url}\n")

if __name__ == "__main__":
    links = asyncio.run(get_links())
    save_m3u(links)
