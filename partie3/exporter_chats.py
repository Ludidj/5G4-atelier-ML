"""Exporte les sessions OpenCode du projet en Markdown dans chatsLogs/.

Les raisonnements et les appels d'outils sont omis : seuls les messages
utilisateur et assistant sont conservés, avec leur horodatage.
"""

import json
import re
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
DOSSIER_LOGS = RACINE / "chatsLogs"
RAISON = "traçabilité des échanges de la Partie 3 (les raisonnements et appels d'outils sont omis)."


def _iso(millisecondes):
    return datetime.fromtimestamp(millisecondes / 1000, timezone.utc).isoformat()


def _date(millisecondes):
    return datetime.fromtimestamp(millisecondes / 1000, timezone.utc).strftime("%Y-%m-%d")


def _slug(texte):
    ascii_texte = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", ascii_texte).strip("-")


def _exporter_session(identifiant):
    resultat = subprocess.run(
        ["opencode", "session", "export", identifiant],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(resultat.stdout)


def _contenu_markdown(donnees):
    info = donnees["info"]
    modele = info.get("model") or {}
    modele_complet = f"{modele.get('providerID', '?')}/{modele.get('id', '?')}"
    lignes = [
        f"# Conversation OpenCode — {info.get('title', '')}",
        "",
        f"- Session : `{info['id']}`",
        f"- Agent : `{info.get('agent', '')}`",
        f"- Modèle : `{modele_complet}`",
        f"- Créée le : {_iso(info['time']['created'])}",
        f"- Exportée le : {_iso(datetime.now(timezone.utc).timestamp() * 1000)}",
        f"- Raison : {RAISON}",
        "",
        "---",
        "",
    ]

    for message in donnees.get("messages", []):
        type_message = message.get("type")
        horodatage = _iso(message.get("time", {}).get("created", info["time"]["created"]))

        if type_message == "user":
            texte = message.get("text", "").strip()
            if texte:
                lignes += [f"## Utilisateur — {horodatage}", "", texte, ""]
            continue

        if type_message != "assistant":
            continue

        parties = message.get("content", [])
        textes = [partie["text"].strip() for partie in parties if partie.get("type") == "text"]
        textes = [texte for texte in textes if texte]
        if not textes:
            continue

        lignes += [f"## Assistant — {horodatage}", ""]
        nombre_outils = sum(1 for partie in parties if partie.get("type") == "tool")
        if nombre_outils:
            lignes += [f"_{nombre_outils} appel(s) d'outil omis._", ""]
        lignes += ["\n\n".join(textes), ""]

    return "\n".join(lignes).rstrip() + "\n"


def main():
    listing = subprocess.run(
        ["opencode", "session", "list", "--format", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    sessions = json.loads(listing.stdout)
    DOSSIER_LOGS.mkdir(parents=True, exist_ok=True)

    for session in sessions:
        donnees = _exporter_session(session["id"])
        date = _date(donnees["info"]["time"]["created"])
        titre = _slug(donnees["info"].get("title", "session"))
        identifiant_court = donnees["info"]["id"].removeprefix("ses_")
        nom_fichier = f"{date}_{titre}_ses_{identifiant_court}.md"
        chemin = DOSSIER_LOGS / nom_fichier
        chemin.write_text(_contenu_markdown(donnees), encoding="utf-8")
        print(f"Exporté {donnees['info']['id']} -> {chemin.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
