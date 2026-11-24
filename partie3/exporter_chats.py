"""Exporte les conversations OpenCode du projet en Markdown dans chatsLogs/.

    /usr/local/bin/python3.12 partie3/exporter_chats.py

L'export officiel d'OpenCode (`opencode session export`) produit du JSON :
ce script le convertit en Markdown lisible. Seuls les échanges utilisateur et
assistant sont conservés ; les raisonnements internes et les appels d'outils
sont omis pour garder des fichiers consultables.
"""

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHATS = ROOT / "chatsLogs"
OPENCODE = "opencode"


def date_iso(timestamp_ms):
    return datetime.fromtimestamp(timestamp_ms / 1000).astimezone().isoformat(timespec="seconds")


def sessions():
    result = subprocess.run(
        [OPENCODE, "session", "list"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        champs = line.split("\t")
        if len(champs) >= 2 and champs[0].startswith("ses_"):
            yield champs[0], champs[1]


def exporter(session_id):
    result = subprocess.run(
        [OPENCODE, "session", "export", session_id],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def en_markdown(donnees):
    info = donnees["info"]
    model = info.get("model") or {}
    lignes = [
        f"# Conversation OpenCode — {info.get('title', 'Sans titre')}",
        "",
        f"- Session : `{info['id']}`",
        f"- Agent : `{info.get('agent', '')}`",
        f"- Modèle : `{model.get('providerID', '')}/{model.get('id', '')}`",
        f"- Créée le : {date_iso(info['time']['created'])}",
        f"- Exportée le : {date_iso(int(datetime.now().timestamp() * 1000))}",
        "- Raison : traçabilité des échanges de la Partie 3 (les raisonnements et appels d'outils sont omis).",
        "",
        "---",
        "",
    ]

    for message in donnees["messages"]:
        type_message = message.get("type")
        if type_message not in ("user", "assistant"):
            continue
        if type_message == "user":
            texte = (message.get("text") or "").strip()
            role = "Utilisateur"
        else:
            parties = message.get("content") or []
            texte = "\n\n".join(
                partie["text"].strip()
                for partie in parties
                if partie.get("type") == "text" and partie.get("text", "").strip()
            )
            outils = sum(1 for partie in parties if partie.get("type") == "tool")
            if outils:
                texte += f"\n\n_{outils} appel(s) d'outil omis._"
            role = "Assistant"
        if not texte:
            continue
        lignes.extend([
            f"## {role} — {date_iso(message['time']['created'])}",
            "",
            texte,
            "",
        ])
    return "\n".join(lignes).rstrip() + "\n"


def main():
    CHATS.mkdir(exist_ok=True)
    exports = []
    for session_id, titre in sessions():
        donnees = exporter(session_id)
        contenu = en_markdown(donnees)
        date = date_iso(donnees["info"]["time"]["created"])[:10]
        slug = re.sub(r"[^A-Za-z0-9]+", "-", titre).strip("-")[:70]
        chemin = CHATS / f"{date}_{slug}_{session_id}.md"
        chemin.write_text(contenu, encoding="utf-8")
        exports.append(chemin)
        print(f"{chemin.name} : {len(donnees['messages'])} messages exportés")
    print(f"{len(exports)} conversation(s) exportée(s) dans {CHATS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
