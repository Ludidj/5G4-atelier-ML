"""Étape F : tests fonctionnels de l'interface et comparaison avec le CLI.

Vérifie que les 14 entrées du menu graphique gardent les libellés du programme
original, que chaque action produit les mêmes textes que le CLI, et que les
données modifiées depuis la GUI sont relues correctement par le CLI.

    cd partie3
    python3.12 test_interface.py
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
from tkinter import TclError

import customtkinter as ctk

import app as gui
from test_connexion import ROOT, compile_cli, run_cli


def comparer_avec_cli(binary, cli_data, choix, answers, texte_graphique):
    sortie_cli = run_cli(binary, cli_data, [(choix, answers)])
    assert texte_graphique in sortie_cli, (
        f"Action {choix} : le texte de l'interface est absent de la sortie CLI\n"
        f"GUI : {texte_graphique!r}\nCLI : {sortie_cli[:500]!r}"
    )


def saisir_dans_dialogue(app, valeurs):
    """Remplit les champs du dialogue ouvert et valide avec Entrée."""
    app.update()
    dialogues = [w for w in app.winfo_children() if isinstance(w, ctk.CTkToplevel)]
    assert len(dialogues) == 1, "Un seul dialogue de saisie doit être ouvert"
    dialogue = dialogues[0]
    entrees = [w for w in dialogue.winfo_children() if hasattr(w, "get") and callable(w.get)]
    assert len(entrees) == len(valeurs)
    for entree, valeur in zip(entrees, valeurs):
        entree.insert(0, valeur)
    dialogue.event_generate("<Return>")
    app.update()
    assert dialogue.winfo_exists() == 0, "Le dialogue doit se fermer après validation"


def main():
    with tempfile.TemporaryDirectory(prefix="partie3-etape-f-") as tmp:
        tmp = Path(tmp)
        cli_data = tmp / "cli-data"
        py_data = tmp / "py-data"
        shutil.copytree(ROOT / "agent" / "data", cli_data)
        shutil.copytree(ROOT / "agent" / "data", py_data)
        cli = compile_cli(tmp)

        modele = gui.ModeleBibliotheque(
            str(py_data / "books.txt"), str(py_data / "users.txt")
        )

        # --- Chargement identique au CLI ---
        assert modele.chargement == (
            "Chargé 41 livre(s) depuis le fichier.\n"
            "Chargé 25 utilisateur(s) depuis le fichier."
        )
        print("Chargement des données OK")

        # --- Actions sans saisie : même sortie que le CLI ---
        for choix, action in [
            (5, modele.afficher_tous_les_livres),
            (6, modele.afficher_livres_disponibles),
            (8, modele.afficher_tous_les_utilisateurs),
            (11, modele.statistiques),
            (13, modele.creer_sauvegarde),
        ]:
            comparer_avec_cli(cli, cli_data, choix, [], action())
        print("Affichages, statistiques et sauvegarde identiques au CLI")

        # --- Actions avec saisie : mêmes résultats et mêmes messages ---
        for choix, answers, action in [
            (3, ["Petit Prince"], lambda: modele.rechercher_titre("Petit Prince")),
            (4, ["Hugo"], lambda: modele.rechercher_auteur("Hugo")),
            (3, ["titre introuvable"], lambda: modele.rechercher_titre("titre introuvable")),
            (4, ["auteur introuvable"], lambda: modele.rechercher_auteur("auteur introuvable")),
            (2, ["ISBN-INCONNU"], lambda: modele.supprimer_livre("ISBN-INCONNU")),
            (9, ["9782070612758", "USR-INCONNU"], lambda: modele.emprunter_livre("9782070612758", "USR-INCONNU")),
            (10, ["9782070612758"], lambda: modele.retourner_livre("9782070612758")),
        ]:
            comparer_avec_cli(cli, cli_data, choix, answers, action())
        print("Recherches et messages d'erreur identiques au CLI")

        # --- Fenêtre principale : libellés originaux et affichage ---
        app = gui.BibliothequeApp(modele)
        app.update()
        boutons = [w for w in app.menu.winfo_children() if isinstance(w, ctk.CTkButton)]
        assert [w.cget("text") for w in boutons] == gui.MENU_LABELS
        assert gui.CHARGEMENT in app.sortie.get("1.0", "end")
        app.executer(11)
        app.update()
        assert "Total des Livres : 41" in app.sortie.get("1.0", "end")
        print("Fenêtre CustomTkinter : 14 libellés d'origine et affichage OK")

        # --- Saisie via la GUI, puis lecture des données par le CLI ---
        app.executer(3)
        saisir_dans_dialogue(app, ["Petit Prince"])
        assert "Titre: Le Petit Prince" in app.sortie.get("1.0", "end")
        print("Dialogue de recherche validé avec Entrée")

        app.executer(1)
        saisir_dans_dialogue(app, ["Livre de test", "Auteur de test", "TEST-001"])
        assert "Livre ajouté avec succès !" in app.sortie.get("1.0", "end")
        app.executer(1)
        saisir_dans_dialogue(app, ["Livre de test", "Auteur de test", "TEST-001"])
        assert "Erreur : Un livre avec l'ISBN TEST-001 existe déjà." in app.sortie.get("1.0", "end")

        app.executer(7)
        saisir_dans_dialogue(app, ["Utilisateur de test", "USR-TEST"])
        assert "Utilisateur ajouté avec succès !" in app.sortie.get("1.0", "end")
        app.executer(9)
        saisir_dans_dialogue(app, ["TEST-001", "USR-TEST"])
        assert "Livre emprunté avec succès !" in app.sortie.get("1.0", "end")
        app.executer(10)
        saisir_dans_dialogue(app, ["TEST-001"])
        assert "Livre retourné avec succès !" in app.sortie.get("1.0", "end")
        app.executer(12)
        app.update()
        assert "Données de la bibliothèque sauvegardées avec succès !" in app.sortie.get("1.0", "end")
        print("Ajout, doublon, utilisateur, emprunt, retour et sauvegarde OK")

        sortie_cli = run_cli(cli, py_data, [(11, []), (5, [])])
        assert "Titre: Livre de test" in sortie_cli
        assert "Total des Livres : 42" in sortie_cli
        assert "Nom: Utilisateur de test" in run_cli(cli, py_data, [(8, [])])
        print("Données écrites par la GUI relues correctement par le CLI")

        # --- Quitter : même sauvegarde que le CLI, puis fermeture ---
        with patch.object(gui.messagebox, "showinfo"):
            app.executer(0)
        try:
            app.winfo_exists()
        except TclError:
            pass  # la fenêtre et l'interpréteur Tk ont été détruits
        else:
            raise AssertionError("La commande 0 doit fermer la fenêtre")
        print("Quitter sauvegarde et ferme la fenêtre")

    print("ÉTAPE F OK")


if __name__ == "__main__":
    main()
