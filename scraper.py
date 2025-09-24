#!/usr/bin/env python3
"""
Platinsport HTML Structure Printer
- Estrae e stampa la struttura HTML della pagina specificata
"""

import asyncio
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com/link/24werdqrx/01.php"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Modalità headless
        page = await browser.new_page()
        print("[INFO] Carico la pagina...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")

        # Estrai il contenuto della pagina
        content = await page.content()
        
        # Stampa l'intero contenuto HTML
        print(content)  # Stampa l'intero contenuto HTML

        # Se vuoi esportare l'HTML in un file per l'analisi
        with open("pagina.html", "w", encoding="utf-8") as f:
            f.write(content)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
    
