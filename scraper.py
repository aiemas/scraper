#!/usr/bin/env python3
import asyncio
import re
from collections import OrderedDict
from playwright.async_api import async_playwright

PLATIN_URL = "https://www.platinsport.com/link/29monorx/01.php"  # cambia se serve
OUTPUT_FILE = "platinsport.m3u"

async def main():
    async with async_playwright() as p:
        # usa un context con user-agent per ridurre il rischio di blocchi "headless"
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US"
        )
        page = await context.new_page()
        print("[INFO] Carico la pagina...")
        await page.goto(PLATIN_URL, timeout=60000)
        await page.wait_for_load_state("networkidle")
        # un piccolo delay extra perché alcuni script finiscono dopo networkidle
        await page.wait_for_timeout(1500)

        # Eseguo in pagina uno script che trova TUTTI i riferimenti a "acestream://" nelle ATTRIBUTI
        # e associa ogni link alla partita più vicina nel DOM (ricerca per previous siblings / parent)
        results = await page.evaluate(
            """() => {
                // regex per trovare "Team A vs Team B" (case-insensitive)
                const matchRe = /\\b([A-Za-zÀ-ÖØ-öø-ÿ0-9\\'\\.\\-\\s]+)\\s+vs\\s+([A-Za-zÀ-ÖØ-öø-ÿ0-9\\'\\.\\-\\s]+)\\b/i;
                function findNearestMatch(el) {
                    let node = el;
                    while (node) {
                        // controlla gli siblings precedenti
                        let prev = node.previousElementSibling;
                        while (prev) {
                            const t = prev.textContent.trim();
                            const m = t.match(matchRe);
                            if (m) return m[0].trim();
                            prev = prev.previousElementSibling;
                        }
                        // controlla il testo del nodo padre
                        node = node.parentElement;
                        if (!node) break;
                        const pt = node.textContent.trim();
                        const pm = pt.match(matchRe);
                        if (pm) return pm[0].trim();
                    }
                    return "";
                }

                const found = [];
                // scandisco ogni elemento e tutte le sue ATTRIBUZIONI
                const all = Array.from(document.querySelectorAll('*'));
                for (const el of all) {
                    for (const attr of el.attributes) {
                        const v = attr.value;
                        if (!v) continue;
                        const m = v.match(/acestream:\\/\\/([a-f0-9]{40,})/i);
                        if (m) {
                            const href = 'acestream://' + m[1];
                            const titleCandidate = (el.textContent || "").trim();
                            const match = findNearestMatch(el) || "";
                            found.push({ href, title: titleCandidate, match });
                            break; // se questa elemento contiene già un acestream non cerco altre attrib
                        }
                    }
                }
                // anche scansiona esplicitamente gli <a> (se hanno href)
                const anchors = Array.from(document.querySelectorAll('a'));
                for (const a of anchors) {
                    const hrefAttr = a.getAttribute('href') || '';
                    const m = hrefAttr.match(/acestream:\\/\\/([a-f0-9]{40,})/i);
                    if (m) {
                        const href = 'acestream://' + m[1];
                        const title = (a.textContent || "").trim();
                        const match = findNearestMatch(a) || "";
                        found.push({ href, title, match });
                    }
                }

                // deduplica mantenendo ordine
                const seen = new Set();
                const dedup = [];
                for (const o of found) {
                    if (!seen.has(o.href)) {
                        seen.add(o.href);
                        dedup.push(o);
                    }
                }
                return dedup;
            }"""
        )

        await context.close()
        await browser.close()

        if not results:
            print("[WARN] Nessun link AceStream trovato (results vuoto).")
            # per debug: salva l'HTML su file locale? (opzionale)
            return

        print(f"[INFO] Trovati {len(results)} riferimenti AceStream, ora raggruppo per partita...")

        # Raggruppa per match (la chiave "" => Unknown Event)
        grouped = OrderedDict()
        for item in results:
            key = item.get("match", "") or "Unknown Event"
            title = item.get("title") or ""
            href = item.get("href")
            grouped.setdefault(key, []).append({"href": href, "title": title})

        # Scrivi M3U (ogni link sotto il proprio evento)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for match, links in grouped.items():
                # se la match è lunga, puliscila
                match_clean = match.strip()
                if not match_clean:
                    match_clean = "Unknown Event"
                for idx, linkobj in enumerate(links, start=1):
                    channel_title = linkobj["title"] if linkobj["title"] else f"Channel {idx}"
                    content_id = linkobj["href"].replace("acestream://", "")
                    http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                    f.write(f'#EXTINF:-1 group-title="{match_clean}",{channel_title}\n{http_link}\n')

        total_links = sum(len(v) for v in grouped.values())
        print(f"[OK] Playlist salvata in {OUTPUT_FILE} con {total_links} canali in {len(grouped)} eventi.")

if __name__ == "__main__":
    asyncio.run(main())
