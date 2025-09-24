#!/usr/bin/env python3
"""
Platinsport scraper
- Estrae i blocchi partite da /link/...
- Usa come gruppo SOLO la riga con 'vs' (es: "Midtjylland vs Sturm Graz")
- Aggiunge tutti i link AceStream a quel gruppo
- Genera un file M3U leggibile da VLC
"""

import re
import requests
from bs4 import BeautifulSoup

PLATIN_URL = "https://www.platinsport.com"
OUTPUT_FILE = "platinsport.m3u"


def get_direct_link(bcvc_url: str) -> str:
    """Estrae il link diretto alla pagina /link/... dalla URL bc.vc"""
    match = re.search(r"https?://www\.platinsport\.com/link/[^\s\"'>]+", bcvc_url)
    if match:
        return match.group(0)
    return bcvc_url


def main():
    print("[INFO] Scarico Platinsport...")
    r = requests.get(PLATIN_URL, timeout=30)
    if r.status_code != 200:
        print(f"[ERRORE] Pagina non disponibile: {r.status_code}")
        return

    bcvc_links = re.findall(r"https?://bc\.vc/[^\s\"'>]+", r.text)
    if not bcvc_links:
        print("[ERRORE] Nessun link bc.vc trovato")
        return

    bcvc_url = bcvc_links[0]
    final_url = get_direct_link(bcvc_url)
    print(f"[INFO] Pagina link diretta: {final_url}")

    r2 = requests.get(final_url, timeout=30)
    if r2.status_code != 200:
        print(f"[ERRORE] Pagina /link non disponibile: {r2.status_code}")
        return

    soup = BeautifulSoup(r2.text, "html.parser")
    container = soup.find(class_="myDiv1")
    if not container:
        print("[ERRORE] Container non trovato")
        return

    children = container.find_all(recursive=False)
    if not children:
        print("[ERRORE] Nessun elemento figlio trovato")
        return

    current_group = None
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for el in children:
            text = el.get_text(strip=True)
            href = el.get("href")

            # 👇 se contiene "vs" è la partita
            if "vs" in text:
                current_group = text
                print(f"[MATCH] Trovata partita: {current_group}")

            # 👇 se è un link acestream, lo aggiungo sotto l’ultimo gruppo trovato
            if href and href.startswith("acestream://") and current_group:
                content_id = href.replace("acestream://", "")
                channel_title = text if text else "Channel"
                http_link = f"http://127.0.0.1:6878/ace/getstream?id={content_id}"
                f.write(f'#EXTINF:-1 group-title="{current_group}",{channel_title}\n{http_link}\n')

    print(f"[OK] Playlist salvata in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
