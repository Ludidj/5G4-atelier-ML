"""Tests de l'interface CustomTkinter et de sa parité avec le CLI.

Nécessite un DISPLAY fonctionne (par exemple DISPLAY=:3 ici).
Aucun test n'est ignoré : chaque action du menu est vérifiée.
Une seule fenêtre CTk est créée pour toute la classe : c'est plus rapide et
cela évite les avertissements Tk sur les callbacks 'after' des fenêtres fermées.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from app import BibliothequeApp
from bibliotheque import LIBELLES_MENU, ModeleBibliotheque

RACINE = Path(__file__).resolve().parents[1]
SOURCE_CLI = RACINE / "agent"
DONNEES_ORIGINALES = SOURCE_CLI / "data"

SCENARIOS = [
    (1, ["Titre Test", "Auteur Test", "999"], ("Titre Test", "Auteur Test", "999")),
    (2, ["9782070612758"], ("9782070612758",)),
    (3, ["Petit"], ("Petit",)),
    (4, ["Hugo"], ("Hugo",)),
    (5, [], ()),
    (6, [], ()),
    (7, ["Test User", "U999"], ("Test User", "U999")),
    (8, [], ()),
    (9, ["9782070612758", "USR001"], ("9782070612758", "USR001")),
    (10, ["9782253096337"], ("9782253096337",)),
    (11, [], ()),
    (12, [], ()),
    (13, [], ()),
]


class TestInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier_tmp = tempfile.mkdtemp(prefix="interface-cli-")
        cls.cli = os.path.join(cls.dossier_tmp, "bibliotheque")
        sources = sorted(str(f) for f in SOURCE_CLI.glob("*.cpp"))
        subprocess.run(
            [
                "g++",
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                *sources,
                "-o",
                cls.cli,
            ],
            check=True,
        )
        cls.application = BibliothequeApp()
        cls.application.update()

    @classmethod
    def tearDownClass(cls):
        if cls.application.winfo_exists():
            cls.application.destroy()
        shutil.rmtree(cls.dossier_tmp)

    def _copies(self, identifiant):
        dossier_cli = os.path.join(self.dossier_tmp, identifiant + "-cli")
        dossier_gui = os.path.join(self.dossier_tmp, identifiant + "-gui")
        shutil.rmtree(dossier_cli, ignore_errors=True)
        shutil.rmtree(dossier_gui, ignore_errors=True)
        shutil.copytree(DONNEES_ORIGINALES, dossier_cli)
        shutil.copytree(DONNEES_ORIGINALES, dossier_gui)
        return dossier_cli, dossier_gui

    def _sortie_cli(self, dossier, choix, lignes):
        script = f"{choix}\n" + "".join(ligne + "\n" for ligne in lignes) + "\n\n0\n"
        resultat = subprocess.run(
            [self.cli, "-d", dossier],
            input=script,
            text=True,
            capture_output=True,
            timeout=15,
        )
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        return resultat.stdout

    def _reinitialiser(self, identifiant):
        dossier_cli, dossier_gui = self._copies(identifiant)
        self.application.modele = ModeleBibliotheque(dossier_gui)
        self.application.modele.demarrer()
        self.application.formulaire_courant = None
        self.application.en_quittement = False
        self.application.zone_sortie.configure(state="normal")
        self.application.zone_sortie.delete("1.0", "end")
        self.application.zone_sortie.configure(state="disabled")
        self.application.update()
        return dossier_cli, dossier_gui

    def test_libelles_des_boutons(self):
        boutons = [
            widget.cget("text")
            for widget in self.application.cadre_boutons.winfo_children()
        ]
        self.assertEqual(len(boutons), 14)
        self.assertEqual(boutons, LIBELLES_MENU)

    def test_chaque_action_egale_au_cli(self):
        for numero, lignes, valeurs in SCENARIOS:
            with self.subTest(action=numero):
                dossier_cli, _ = self._reinitialiser("action-" + str(numero))
                sortie_cli = self._sortie_cli(dossier_cli, numero, lignes)
                texte_gui = self.application.executer_action(numero, valeurs)
                self.assertIn(texte_gui, sortie_cli)
                self.assertIn(
                    texte_gui, self.application.zone_sortie.get("1.0", "end")
                )

    def test_dialogue_valide_avec_entree(self):
        self._reinitialiser("dialogue")
        self.assertIsNone(self.application.executer_action(1))
        self.application.update()
        formulaire = self.application.formulaire_courant
        self.assertIsNotNone(formulaire)
        self.assertEqual([entree.get() for entree in formulaire.entrees], ["", "", ""])
        for entree, valeur in zip(formulaire.entrees, ("Titre", "Auteur", "123")):
            entree.insert(0, valeur)
        formulaire.entrees[-1].event_generate("<Return>")
        self.application.update()
        self.assertIn(
            "Livre ajouté avec succès !",
            self.application.zone_sortie.get("1.0", "end"),
        )

    def test_donnees_ecrites_par_gui_relues_par_cli(self):
        _, dossier_gui = self._reinitialiser("aller-retour")
        self.application.executer_action(1, ("Livre GUI", "Auteur GUI", "GUI-999"))
        self.application.executer_action(7, ("Utilisateur GUI", "GUI-U1"))
        self.application.executer_action(12)

        sortie_cli = self._sortie_cli(dossier_gui, 3, ["Livre GUI"])
        self.assertIn("Titre: Livre GUI", sortie_cli)
        self.assertIn("Auteur: Auteur GUI", sortie_cli)
        self.assertIn("ISBN: GUI-999", sortie_cli)

    def test_z_action_quitter(self):
        dossier_cli, _ = self._reinitialiser("quitter")
        sortie_cli = self._sortie_cli(dossier_cli, 0, [])
        texte_gui = self.application.executer_action(0)
        self.assertIn(texte_gui, sortie_cli)
        self.assertIn(
            "Merci d'avoir utilisé", self.application.zone_sortie.get("1.0", "end")
        )


if __name__ == "__main__":
    unittest.main()
