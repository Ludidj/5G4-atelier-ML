"""Étape D : vérifier la connexion Python/C++ par comparaison avec le CLI d'origine.

Le test compile le CLI original (main.cpp) dans un répertoire temporaire, puis
exécute les mêmes opérations :
  1. via le module pybind11 ;
  2. via le menu en ligne de commande original.
Les données de agent/data/ sont copiées : les fichiers suivis ne sont jamais modifiés.

    cd partie3
    python3.12 test_connexion.py
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bibliotheque_binding as cpp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AGENT_DIR = ROOT / "agent"
DATA_DIR = AGENT_DIR / "data"


def compile_cli(destination: Path) -> Path:
    """Compile le CLI original sans modifier ses sources."""
    binary = destination / "bibliotheque"
    sources = sorted(AGENT_DIR.glob("*.cpp"))
    subprocess.run(
        ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic",
         *(str(source) for source in sources), "-o", str(binary)],
        check=True,
        capture_output=True,
        text=True,
    )
    return binary


def cli_input(actions) -> str:
    """Construit l'entrée du menu CLI original.

    Chaque action se termine par pauseForInput() (cin.ignore(); cin.get()),
    soit deux caractères à consommer avant le choix suivant ; la commande 0
    quitte sans pause.
    """
    parts = []
    for choice, answers in [*actions, (0, [])]:
        parts.append(f"{choice}\n")
        parts.extend(f"{answer}\n" for answer in answers)
        if choice != 0:
            parts.append("\n\n")
    return "".join(parts)


def run_cli(binary: Path, data_dir: Path, actions) -> str:
    result = subprocess.run(
        [str(binary), "-d", str(data_dir)],
        input=cli_input(actions),
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    return result.stdout


def stats_from_cli(output: str):
    labels = ["Total des Livres", "Livres Disponibles", "Livres Empruntés", "Total des Utilisateurs"]
    values = []
    for label in labels:
        match = re.search(rf"{re.escape(label)} : (\d+)", output)
        assert match, f"Statistique introuvable dans la sortie CLI : {label}"
        values.append(int(match.group(1)))
    return tuple(values)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="partie3-etape-d-") as tmp:
        tmp = Path(tmp)
        cli_data = tmp / "cli-data"
        py_data = tmp / "py-data"
        shutil.copytree(DATA_DIR, cli_data)
        shutil.copytree(DATA_DIR, py_data)

        cli = compile_cli(tmp)

        # --- Même chargement, mêmes statistiques des deux côtés ---
        library = cpp.Library()
        files = cpp.FileManager(str(py_data / "books.txt"), str(py_data / "users.txt"))
        assert files.loadLibraryData(library) is True
        stats = (
            library.getTotalBooks(),
            library.getAvailableBookCount(),
            library.getCheckedOutBookCount(),
            len(library.getAllUsers()),
        )

        cli_output = run_cli(cli, cli_data, [(11, [])])
        assert stats_from_cli(cli_output) == stats, (stats_from_cli(cli_output), stats)
        print("Statistiques identiques CLI / Python :", stats)

        # --- Même recherche par titre, même chaîne toString() ---
        cli_output = run_cli(cli, cli_data, [(3, ["Petit Prince"])])
        results = library.searchBooksByTitle("Petit Prince")
        assert len(results) == 1
        assert results[0].toString() in cli_output
        assert "Titre: Le Petit Prince" in results[0].toString()
        print("Recherche par titre identique CLI / Python")

        # --- Même affichage de tous les livres ---
        cli_output = run_cli(cli, cli_data, [(5, [])])
        for book in library.getAllBooks():
            assert book.toString() in cli_output
        print("Affichage des livres identique CLI / Python")

        # --- Opérations disponibles via le binding ---
        book = library.findBookByISBN("9782070612758")
        user = library.findUserById("USR004")
        assert book is not None and user is not None
        initial_borrowed = user.getBorrowedBooks()
        assert book.getAvailability() is True
        assert library.checkOutBook(book.getISBN(), user.getUserId()) is True
        assert book.getBorrowerId() == user.getUserId()
        assert user.hasBorrowedBook(book.getISBN()) is True
        assert library.returnBook(book.getISBN()) is True
        # USR004 avait déjà un autre livre emprunté dans les données d'origine :
        # seul l'ISBN emprunté ici doit disparaître de sa liste.
        assert book.getBorrowerId() == ""
        assert user.getBorrowedBooks() == initial_borrowed
        assert user.hasBorrowedBook(book.getISBN()) is False
        assert library.checkOutBook("ISBN-INCONNU", user.getUserId()) is False
        print("Emprunt / retour cohérents avec la logique C++ d'origine")

        new_book = cpp.Book("Livre de test", "Auteur de test", "TEST-001")
        library.addBook(new_book)
        assert library.findBookByISBN("TEST-001").getTitle() == "Livre de test"
        assert library.removeBook("TEST-001") is True
        assert library.removeBook("TEST-001") is False
        library.addUser(cpp.User("Utilisateur de test", "USR-TEST"))
        assert library.findUserById("USR-TEST").getName() == "Utilisateur de test"
        assert len(library.searchBooksByAuthor("Hugo")) == len(
            [b for b in library.getAllBooks() if "hugo" in b.getAuthor().lower()]
        )
        print("Ajout / suppression / recherche disponibles depuis Python")

        # --- Sauvegarde, rechargement et sauvegarde de secours ---
        assert files.saveLibraryData(library) is True
        assert files.fileExists(str(py_data / "books.txt"))
        reloaded = cpp.Library()
        assert files.loadLibraryData(reloaded) is True
        assert reloaded.getTotalBooks() == library.getTotalBooks()
        assert reloaded.getAvailableBookCount() == library.getAvailableBookCount()
        files.createBackup()
        assert (py_data / "books.txt.backup").is_file()
        assert (py_data / "users.txt.backup").is_file()
        print("Sauvegarde / chargement / sauvegarde de secours OK")

        # --- Format de fichier identique après aller-retour ---
        original_line = (cli_data / "books.txt").read_text(encoding="utf-8").splitlines()[0]
        parsed = cpp.Book()
        parsed.fromFileFormat(original_line)
        assert parsed.toFileFormat() == original_line
        print("Format de fichier Book préservé")

    print("ÉTAPE D OK")


if __name__ == "__main__":
    main()
