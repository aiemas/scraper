import requests
from bs4 import BeautifulSoup

# URL della pagina da cui prendere le partite
url = "https://tuosito.com/schedule"  # sostituisci con il tuo URL reale

# Scarica la pagina
response = requests.get(url)
html = response.text

soup = BeautifulSoup(html, "html.parser")

# Lista per M3U
m3u_entries = []

# Cicla su tutti gli elementi testuali che potrebbero contenere il nome partita
for element in soup.find_all(string=True):
    text = element.strip()
    if text:
        # Filtra testi troppo corti o non rilevanti
        if len(text) > 3 and not text.lower().startswith(("scotland", "english", "time")):
            match_name = text
            # Qui devi decidere come ottenere lo stream URL corrispondente
            # Per esempio un ID AceStream o M3U8 trovato nello stesso blocco HTML
            # Temporaneamente mettiamo un placeholder
            stream_url = f"http://127.0.0.1:6878/ace/getstream?id=PLACEHOLDER_{len(m3u_entries)+1}"
            
            # Crea la riga M3U
            m3u_line = f'#EXTINF:-1 group-title="{match_name}",{match_name}\n{stream_url}'
            m3u_entries.append(m3u_line)

# Genera il file M3U
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for entry in m3u_entries:
        f.write(entry + "\n")

print(f"Playlist generata con {len(m3u_entries)} partite!")
