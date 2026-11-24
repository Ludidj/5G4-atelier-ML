"""Parité entre le CLI C++ original et la façade Python (étape D)."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from bibliotheque import ModeleBibliotheque

RACINE = Path(__file__).resolve().parents[1]
SOURCE_CLI = RACINE / "agent"
DONNEES_ORIGINALES = SOURCE_CLI / "data"


class TestPariteCliFacade(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier_tmp = tempfile.mkdtemp(prefix="parite-cli-")
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

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dossier_tmp)

    def _comparer(self, choix, lignes, nom_action, args=()):
        identifiant = self.id().rsplit(".", 1)[-1]
        dossier_cli = os.path.join(self.dossier_tmp, identifiant + "-cli")
        dossier_python = os.path.join(self.dossier_tmp, identifiant + "-py")
        shutil.copytree(DONNEES_ORIGINALES, dossier_cli)
        shutil.copytree(DONNEES_ORIGINALES, dossier_python)

        script = f"{choix}\n" + "".join(ligne + "\n" for ligne in lignes) + "\n\n0\n"
        sortie_cli = subprocess.run(
            [self.cli, "-d", dossier_cli],
            input=script,
            text=True,
            capture_output=True,
            timeout=15,
        )
        self.assertEqual(sortie_cli.returncode, 0, sortie_cli.stderr)

        modele = ModeleBibliotheque(dossier_python)
        modele.demarrer()
        texte_facade = getattr(modele, nom_action)(*args)
        self.assertIn(texte_facade, sortie_cli.stdout)

    def test_01_ajouter_livre(self):
        self._comparer(
            1,
            ["Titre Test", "Auteur Test", "999"],
            "ajouter_livre",
            ("Titre Test", "Auteur Test", "999"),
        )

    def test_02_supprimer_livre(self):
        self._comparer(2, ["9782070612758"], "supprimer_livre", ("9782070612758",))

    def test_03_rechercher_titre(self):
        self._comparer(3, ["Petit"], "rechercher_par_titre", ("Petit",))

    def test_04_rechercher_auteur(self):
        self._comparer(4, ["Hugo"], "rechercher_par_auteur", ("Hugo",))

    def test_05_afficher_tous_les_livres(self):
        self._comparer(5, [], "afficher_tous_les_livres")

    def test_06_afficher_disponibles(self):
        self._comparer(6, [], "afficher_livres_disponibles")

    def test_07_ajouter_utilisateur(self):
        self._comparer(
            7, ["Test User", "U999"], "ajouter_utilisateur", ("Test User", "U999")
        )

    def test_08_afficher_utilisateurs(self):
        self._comparer(8, [], "afficher_tous_les_utilisateurs")

    def test_09_emprunter_livre(self):
        self._comparer(
            9,
            ["9782070612758", "USR001"],
            "emprunter_livre",
            ("9782070612758", "USR001"),
        )

    def test_10_retourner_livre(self):
        self._comparer(10, ["9782253096337"], "retourner_livre", ("9782253096337",))

    def test_11_statistiques(self):
        self._comparer(11, [], "statistiques")

    def test_12_sauvegarder(self):
        self._comparer(12, [], "sauvegarder")

    def test_13_creer_sauvegarde(self):
        self._comparer(13, [], "creer_sauvegarde")

    def test_14_quitter(self):
        self._comparer(0, [], "quitter")

    def test_doublon_isbn(self):
        self._comparer(
            1,
            ["Titre", "Auteur", "9782070612758"],
            "ajouter_livre",
            ("Titre", "Auteur", "9782070612758"),
        )


if __name__ == "__main__":
    unittest.main()
