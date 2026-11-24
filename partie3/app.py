"""Partie 3 : interface graphique remplaçant le menu en ligne de commande.

Toutes les actions et tous les textes affichés proviennent du programme C++
original (agent/main.cpp, agent/library.cpp, agent/filemanager.cpp). Les
données sont manipulées par les classes C++ via le module pybind11 : aucune
logique métier n'est réécrite ici.

    cd partie3
    python3.12 app.py [-d <répertoire>]
"""

import ctypes
import os
import sys
import tempfile
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

import bibliotheque_binding as cpp

# Libellés du menu de agent/main.cpp (displayMenu), repris à l'identique.
MENU_LABELS = [
    "1.  Ajouter un Livre",
    "2.  Supprimer un Livre",
    "3.  Rechercher des Livres par Titre",
    "4.  Rechercher des Livres par Auteur",
    "5.  Afficher Tous les Livres",
    "6.  Afficher les Livres Disponibles",
    "7.  Ajouter un Utilisateur",
    "8.  Afficher Tous les Utilisateurs",
    "9.  Emprunter un Livre",
    "10. Retourner un Livre",
    "11. Statistiques de la Bibliothèque",
    "12. Sauvegarder les Données",
    "13. Créer une Sauvegarde",
    "0.  Quitter",
]

TITRE = "SYSTÈME DE GESTION DE BIBLIOTHÈQUE PERSONNELLE"
CHARGEMENT = "Chargement des données de la bibliothèque..."
PAUSE = "Appuyez sur Entrée pour continuer..."

# Invitations de saisie de agent/main.cpp (getInput), reprises à l'identique.
PROMPTS = {
    1: ["Entrez le titre du livre : ", "Entrez l'auteur du livre : ", "Entrez l'ISBN du livre : "],
    2: ["Entrez l'ISBN du livre à supprimer : "],
    3: ["Entrez le titre à rechercher : "],
    4: ["Entrez l'auteur à rechercher : "],
    7: ["Entrez le nom de l'utilisateur : ", "Entrez l'ID de l'utilisateur : "],
    9: ["Entrez l'ISBN du livre à emprunter : ", "Entrez l'ID de l'utilisateur : "],
    10: ["Entrez l'ISBN du livre à retourner : "],
}


def capture_sortie_cpp(appel):
    """Récupère le texte écrit par std::cout par une méthode C++ d'origine.

    Les méthodes displayAllBooks/displayAvailableBooks/displayAllUsers et
    loadLibraryData écrivent déjà les bons libellés : on se contente de
    rediriger le descripteur 1 le temps de l'appel, sans rien réécrire.
    """
    libc = ctypes.CDLL(None)
    libc.fflush(None)
    with tempfile.TemporaryFile(mode="w+b") as tmp:
        sortie_initial = os.dup(1)
        os.dup2(tmp.fileno(), 1)
        try:
            appel()
            libc.fflush(None)  # std::cout est synchronisé avec stdio ici
        finally:
            os.dup2(sortie_initial, 1)
            os.close(sortie_initial)
        tmp.seek(0)
        return tmp.read().decode("utf-8").strip("\n")


class ModeleBibliotheque:
    """Actions du menu, exécutées par les objets C++ du module pybind11."""

    def __init__(self, books_file: str, users_file: str):
        self.library = cpp.Library()
        self.files = cpp.FileManager(books_file, users_file)
        self.chargement = capture_sortie_cpp(lambda: self.files.loadLibraryData(self.library))

    def ajouter_livre(self, titre, auteur, isbn):
        if self.library.findBookByISBN(isbn):
            return f"Erreur : Un livre avec l'ISBN {isbn} existe déjà."
        self.library.addBook(cpp.Book(titre, auteur, isbn))
        return "Livre ajouté avec succès !"

    def supprimer_livre(self, isbn):
        if self.library.removeBook(isbn):
            return "Livre supprimé avec succès !"
        return "Livre non trouvé."

    def _resultats_recherche(self, resultats, message_vide):
        if not resultats:
            return message_vide
        lignes = ["=== RÉSULTATS DE RECHERCHE ==="]
        for i, livre in enumerate(resultats, 1):
            lignes.extend(["", f"Résultat {i} :", livre.toString(), "-----------------------------"])
        return "\n".join(lignes)

    def rechercher_titre(self, titre):
        return self._resultats_recherche(
            self.library.searchBooksByTitle(titre), "Aucun livre trouvé avec ce titre."
        )

    def rechercher_auteur(self, auteur):
        return self._resultats_recherche(
            self.library.searchBooksByAuthor(auteur), "Aucun livre trouvé de cet auteur."
        )

    def afficher_tous_les_livres(self):
        return capture_sortie_cpp(self.library.displayAllBooks)

    def afficher_livres_disponibles(self):
        return capture_sortie_cpp(self.library.displayAvailableBooks)

    def afficher_tous_les_utilisateurs(self):
        return capture_sortie_cpp(self.library.displayAllUsers)

    def ajouter_utilisateur(self, nom, identifiant):
        if self.library.findUserById(identifiant):
            return f"Erreur : Un utilisateur avec l'ID {identifiant} existe déjà."
        self.library.addUser(cpp.User(nom, identifiant))
        return "Utilisateur ajouté avec succès !"

    def emprunter_livre(self, isbn, identifiant):
        if self.library.checkOutBook(isbn, identifiant):
            return "Livre emprunté avec succès !"
        return ("Erreur : Impossible d'emprunter le livre. Vérifiez l'ISBN, "
                "l'ID utilisateur et la disponibilité du livre.")

    def retourner_livre(self, isbn):
        if self.library.returnBook(isbn):
            return "Livre retourné avec succès !"
        return ("Erreur : Impossible de retourner le livre. Vérifiez l'ISBN "
                "et que le livre est bien emprunté.")

    def statistiques(self):
        return "\n".join([
            "=== STATISTIQUES DE LA BIBLIOTHÈQUE ===",
            f"Total des Livres : {self.library.getTotalBooks()}",
            f"Livres Disponibles : {self.library.getAvailableBookCount()}",
            f"Livres Empruntés : {self.library.getCheckedOutBookCount()}",
            f"Total des Utilisateurs : {len(self.library.getAllUsers())}",
        ])

    def sauvegarder(self):
        if self.files.saveLibraryData(self.library):
            return "Données de la bibliothèque sauvegardées avec succès !"
        return "Erreur lors de la sauvegarde des données de la bibliothèque."

    def creer_sauvegarde(self):
        self.files.createBackup()
        return "Fichiers de sauvegarde créés."

    def quitter(self):
        self.files.saveLibraryData(self.library)
        return ("Sauvegarde des données avant la fermeture...\n"
                "Merci d'avoir utilisé le Système de Gestion de Bibliothèque Personnelle !")


class BibliothequeApp(ctk.CTk):
    def __init__(self, modele):
        super().__init__()
        self.modele = modele
        self.title(TITRE)
        self.geometry("1100x720")

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.menu = ctk.CTkFrame(self)
        self.menu.grid(row=0, column=0, sticky="ns", padx=8, pady=8)
        ctk.CTkLabel(self.menu, text=TITRE, wraplength=250).pack(padx=10, pady=12)

        for choix, libelle in enumerate(MENU_LABELS):
            numero = 0 if choix == len(MENU_LABELS) - 1 else choix + 1
            ctk.CTkButton(
                self.menu,
                text=libelle,
                anchor="w",
                command=lambda n=numero: self.executer(n),
            ).pack(fill="x", padx=8, pady=2)

        self.sortie = ctk.CTkTextbox(self, wrap="word")
        self.sortie.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=8)
        self.sortie.configure(state="disabled")
        self.afficher(f"{CHARGEMENT}\n{self.modele.chargement}")

    def afficher(self, texte):
        self.sortie.configure(state="normal")
        self.sortie.insert("end", texte + "\n")
        self.sortie.see("end")
        self.sortie.configure(state="disabled")

    def executer(self, choix):
        if choix in PROMPTS:
            self.ouvrir_saisie(choix)
            return
        actions = {
            5: self.modele.afficher_tous_les_livres,
            6: self.modele.afficher_livres_disponibles,
            8: self.modele.afficher_tous_les_utilisateurs,
            11: self.modele.statistiques,
            12: self.modele.sauvegarder,
            13: self.modele.creer_sauvegarde,
        }
        if choix == 0:
            message = self.modele.quitter()
            self.afficher(message)
            messagebox.showinfo(TITRE, message)
            self.destroy()
            return
        self.afficher(actions[choix]())

    def ouvrir_saisie(self, choix):
        dialogue = ctk.CTkToplevel(self)
        dialogue.title(MENU_LABELS[choix - 1])
        dialogue.transient(self)
        dialogue.grab_set()
        entrees = []
        for prompt in PROMPTS[choix]:
            ctk.CTkLabel(dialogue, text=prompt).pack(padx=12, pady=(12, 0), anchor="w")
            entree = ctk.CTkEntry(dialogue, width=320)
            entree.pack(padx=12, pady=4)
            entrees.append(entree)

        def valider():
            valeurs = [entree.get() for entree in entrees]
            resultats = {
                1: self.modele.ajouter_livre,
                2: self.modele.supprimer_livre,
                3: self.modele.rechercher_titre,
                4: self.modele.rechercher_auteur,
                7: self.modele.ajouter_utilisateur,
                9: self.modele.emprunter_livre,
                10: self.modele.retourner_livre,
            }
            self.afficher(resultats[choix](*valeurs))
            dialogue.destroy()

        ctk.CTkButton(dialogue, text=PAUSE, command=valider).pack(padx=12, pady=12)
        dialogue.bind("<Return>", lambda _evenement: valider())
        entrees[0].focus_set()


def analyser_arguments(argv):
    """Reprend l'analyse de main.cpp : --data-dir|-d <répertoire>."""
    data_dir = ""
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--data-dir" or arg == "-d":
            if i + 1 >= len(argv):
                erreur(f"Erreur : {arg} nécessite un répertoire.")
            data_dir = argv[i + 1]
            i += 1
        else:
            erreur(f"Erreur : argument inconnu '{arg}'.")
        i += 1

    if data_dir and not Path(data_dir).is_dir():
        erreur(f"Erreur : le répertoire {data_dir} n'existe pas.")
    if not data_dir:
        return "", ""
    return str(Path(data_dir) / "books.txt"), str(Path(data_dir) / "users.txt")


def erreur(message):
    print(message, file=sys.stderr)
    print(f"Usage: {sys.argv[0]} [--data-dir|-d <répertoire>]", file=sys.stderr)
    raise SystemExit(1)


def main():
    books_file, users_file = analyser_arguments(sys.argv[1:])
    modele = ModeleBibliotheque(books_file, users_file)
    BibliothequeApp(modele).mainloop()


if __name__ == "__main__":
    main()
