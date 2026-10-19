"""Client minimo per il server locale di LM Studio.

Scheletro da completare con Claude Code (slide 19-22):
configurazione, messaggi, payload e chiamata HTTP.
Import e gestione degli errori sono gia' presenti: conservarli.
"""

import json
import os

import requests
from dotenv import load_dotenv

# --- Configurazione -------------------------------------------------------
load_dotenv()
base_url = os.environ["LM_BASE_URL"]
model = os.environ["LM_MODEL"]

# --- Messaggi -------------------------------------------------------------
messages = [
    {"role": "system", "content": "Sei un assistente conciso. Rispondi sempre in italiano."},
]

# --- Payload --------------------------------------------------------------
payload = {
    "model": model,
    "messages": messages,
    "temperature": 0.2,
    "max_tokens": 300,
    "reasoning_effort": "none",
    "stream": True,
}

# --- Chiamata -------------------------------------------------------------
try:
    while True:
        domanda = input("Domanda (esci per terminare): ").strip()
        if domanda.lower() == "esci":
            break
        if not domanda:
            continue
        payload["messages"] = messages + [{"role": "user", "content": domanda}]
        try:
            response = requests.post(f"{base_url}/chat/completions", json=payload, timeout=120, stream=True)
            response.raise_for_status()
            frammenti = []
            for riga in response.iter_lines(decode_unicode=True):
                if not riga or not riga.startswith("data:"):
                    continue
                dati = riga[5:].strip()
                if dati == "[DONE]":
                    break
                scelte = json.loads(dati)["choices"]
                frammento = scelte[0]["delta"].get("content") if scelte else None
                if frammento:
                    print(frammento, end="", flush=True)
                    frammenti.append(frammento)
            print()
            risposta_completa = "".join(frammenti)
            messages.append({"role": "user", "content": domanda})
            messages.append({"role": "assistant", "content": risposta_completa})
        except requests.exceptions.Timeout:
            print("Attesa scaduta: controllare server, carico e tempi.")
        except requests.exceptions.ConnectionError:
            print("Connessione fallita: controllare server, URL e porta.")
        except requests.exceptions.HTTPError:
            print("Errore HTTP:", response.status_code, response.text)
except (KeyboardInterrupt, EOFError):
    print()
