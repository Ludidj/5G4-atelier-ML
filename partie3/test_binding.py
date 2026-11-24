"""Tests directs du module pybind11 (aucune réécriture de la logique C++)."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import bibliotheque_binding as liaison

RACINE = Path(__file__).resolve().parents[1]
DONNEES_ORIGINALES = RACINE / "agent" / "data"


class TestBinding(unittest.TestCase):
    def test_book_getters_setters(self):
        livre = liaison.Book("Titre", "Auteur", "ISBN-1")
        self.assertEqual(livre.getTitle(), "Titre")
        self.assertEqual(livre.getAuthor(), "Auteur")
        self.assertEqual(livre.getISBN(), "ISBN-1")
        self.assertTrue(livre.getAvailability())
        self.assertEqual(livre.getBorrowerId(), "")

        livre.setTitle("Autre")
        livre.setAuthor("Écrivain")
        livre.setISBN("ISBN-2")
        livre.setBorrowerId("U1")
        livre.setAvailability(False)
        self.assertEqual(livre.getTitle(), "Autre")
        self.assertEqual(livre.getAuthor(), "Écrivain")
        self.assertEqual(livre.getISBN(), "ISBN-2")
        self.assertEqual(livre.getBorrowerId(), "U1")
        self.assertFalse(livre.getAvailability())

    def test_book_checkout_return(self):
        livre = liaison.Book("Titre", "Auteur", "ISBN-1")
        livre.checkOut("U1")
        self.assertFalse(livre.getAvailability())
        self.assertEqual(livre.getBorrowerId(), "U1")
        livre.returnBook()
        self.assertTrue(livre.getAvailability())
        self.assertEqual(livre.getBorrowerId(), "")

    def test_user_operations(self):
        utilisateur = liaison.User("Marie", "U1")
        utilisateur.borrowBook("ISBN-1")
        utilisateur.borrowBook("ISBN-1")
        self.assertEqual(utilisateur.getBorrowedBooks(), ["ISBN-1"])
        self.assertTrue(utilisateur.hasBorrowedBook("ISBN-1"))
        self.assertEqual(utilisateur.getNumberOfBorrowedBooks(), 1)
        utilisateur.returnBook("ISBN-1")
        self.assertFalse(utilisateur.hasBorrowedBook("ISBN-1"))

    def test_library_operations(self):
        bibliotheque = liaison.Library()
        bibliotheque.addBook(liaison.Book("Titre", "Auteur", "ISBN-1"))
        bibliotheque.addUser(liaison.User("Marie", "U1"))

        self.assertEqual(bibliotheque.getTotalBooks(), 1)
        self.assertEqual(bibliotheque.getAvailableBookCount(), 1)
        self.assertEqual(bibliotheque.getCheckedOutBookCount(), 0)
        self.assertEqual(len(bibliotheque.getAllUsers()), 1)

        self.assertTrue(bibliotheque.checkOutBook("ISBN-1", "U1"))
        self.assertEqual(bibliotheque.getCheckedOutBookCount(), 1)
        self.assertFalse(bibliotheque.checkOutBook("ISBN-1", "U1"))
        self.assertTrue(bibliotheque.returnBook("ISBN-1"))
        self.assertEqual(bibliotheque.getAvailableBookCount(), 1)

        self.assertEqual(len(bibliotheque.searchBooksByTitle("titre")), 1)
        self.assertEqual(len(bibliotheque.searchBooksByAuthor("AUTEUR")), 1)
        self.assertEqual(len(bibliotheque.getAvailableBooks()), 1)
        self.assertTrue(bibliotheque.removeBook("ISBN-1"))
        self.assertEqual(bibliotheque.getTotalBooks(), 0)

    def test_duree_de_vie_des_pointeurs(self):
        bibliotheque = liaison.Library()
        bibliotheque.addBook(liaison.Book("Titre", "Auteur", "ISBN-1"))
        livre = bibliotheque.findBookByISBN("ISBN-1")
        del bibliotheque
        self.assertEqual(livre.getTitle(), "Titre")

    def test_filemanager_lecture_ecriture(self):
        dossier = tempfile.mkdtemp(prefix="binding-")
        self.addCleanup(shutil.rmtree, dossier)
        livres = os.path.join(dossier, "books.txt")
        utilisateurs = os.path.join(dossier, "users.txt")
        shutil.copy2(DONNEES_ORIGINALES / "books.txt", livres)
        shutil.copy2(DONNEES_ORIGINALES / "users.txt", utilisateurs)

        gestionnaire = liaison.FileManager(livres, utilisateurs)
        bibliotheque = liaison.Library()
        self.assertTrue(gestionnaire.loadLibraryData(bibliotheque))
        self.assertEqual(bibliotheque.getTotalBooks(), 41)
        self.assertEqual(len(bibliotheque.getAllUsers()), 25)
        self.assertTrue(gestionnaire.saveLibraryData(bibliotheque))
        self.assertTrue(gestionnaire.fileExists(livres))


if __name__ == "__main__":
    unittest.main()
