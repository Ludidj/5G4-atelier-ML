"""Façade Python : elle pilote les classes C++ originales via pybind11.

Tous les textes ci-dessous sont ceux du programme original (agent/main.cpp,
agent/library.cpp et agent/filemanager.cpp). Aucun libellé n'est inventé.
"""

import ctypes
import os
import tempfile

import bibliotheque_binding as liaison


MENU_PRINCIPAL = (
    "\n=== SYSTÈME DE GESTION DE BIBLIOTHÈQUE PERSONNELLE ===\n"
    "1.  Ajouter un Livre\n"
    "2.  Supprimer un Livre\n"
    "3.  Rechercher des Livres par Titre\n"
    "4.  Rechercher des Livres par Auteur\n"
    "5.  Afficher Tous les Livres\n"
    "6.  Afficher les Livres Disponibles\n"
    "7.  Ajouter un Utilisateur\n"
    "8.  Afficher Tous les Utilisateurs\n"
    "9.  Emprunter un Livre\n"
    "10. Retourner un Livre\n"
    "11. Statistiques de la Bibliothèque\n"
    "12. Sauvegarder les Données\n"
    "13. Créer une Sauvegarde\n"
    "0.  Quitter\n"
    "======================================================\n"
    "Entrez votre choix : "
)

LIBELLES_MENU = [
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

PROMPT_TITRE_LIVRE = "Entrez le titre du livre : "
PROMPT_AUTEUR_LIVRE = "Entrez l'auteur du livre : "
PROMPT_ISBN_LIVRE = "Entrez l'ISBN du livre : "
PROMPT_ISBN_SUPPRESSION = "Entrez l'ISBN du livre à supprimer : "
PROMPT_TITRE_RECHERCHE = "Entrez le titre à rechercher : "
PROMPT_AUTEUR_RECHERCHE = "Entrez l'auteur à rechercher : "
PROMPT_NOM_UTILISATEUR = "Entrez le nom de l'utilisateur : "
PROMPT_ID_UTILISATEUR = "Entrez l'ID de l'utilisateur : "
PROMPT_ISBN_EMPRUNT = "Entrez l'ISBN du livre à emprunter : "
PROMPT_ID_EMPRUNT = "Entrez l'ID de l'utilisateur : "
PROMPT_ISBN_RETOUR = "Entrez l'ISBN du livre à retourner : "


def capture_sortie_cpp(action):
    """Exécute un appel C++ et récupère exactement ce qu'il écrit sur stdout.

    Les méthodes display* et FileManager écrivent avec cout. On redirige le
    descripteur 1 le temps de l'appel, puis on vide les flux stdio avec fflush.
    Retourne (valeur_de_retour_de_l_action, texte_capture).
    """
    bibliotheque_c = ctypes.CDLL(None)
    bibliotheque_c.fflush.argtypes = [ctypes.c_void_p]
    bibliotheque_c.fflush(None)

    descripteur_sauvegarde = os.dup(1)
    with tempfile.TemporaryFile(mode="w+b") as tampon:
        os.dup2(tampon.fileno(), 1)
        try:
            resultat = action()
            bibliotheque_c.fflush(None)
            tampon.seek(0)
            texte = tampon.read().decode("utf-8")
        finally:
            bibliotheque_c.fflush(None)
            os.dup2(descripteur_sauvegarde, 1)
            os.close(descripteur_sauvegarde)
    return resultat, texte


class ModeleBibliotheque:
    """Les 14 actions du menu, telles que le CLI les enchaîne."""

    def __init__(self, dossier_donnees=None):
        if dossier_donnees is not None and os.path.isdir(dossier_donnees):
            fichier_livres = os.path.join(dossier_donnees, "books.txt")
            fichier_utilisateurs = os.path.join(dossier_donnees, "users.txt")
        else:
            fichier_livres = ""
            fichier_utilisateurs = ""

        self.bibliotheque = liaison.Library()
        self.gestionnaire_fichiers = liaison.FileManager(
            fichier_livres, fichier_utilisateurs
        )

    def demarrer(self):
        _, messages = capture_sortie_cpp(
            lambda: self.gestionnaire_fichiers.loadLibraryData(self.bibliotheque)
        )
        return "Chargement des données de la bibliothèque...\n" + messages

    def menu(self):
        return MENU_PRINCIPAL

    def ajouter_livre(self, titre, auteur, isbn):
        if self.bibliotheque.findBookByISBN(isbn):
            return f"Erreur : Un livre avec l'ISBN {isbn} existe déjà.\n"
        self.bibliotheque.addBook(liaison.Book(titre, auteur, isbn))
        return "Livre ajouté avec succès !\n"

    def supprimer_livre(self, isbn):
        if self.bibliotheque.removeBook(isbn):
            return "Livre supprimé avec succès !\n"
        return "Livre non trouvé.\n"

    def _formater_resultats(self, livres):
        if not livres:
            return ""
        texte = "\n=== RÉSULTATS DE RECHERCHE ===\n"
        for position, livre in enumerate(livres, 1):
            texte += f"\nRésultat {position} :\n"
            texte += livre.toString() + "\n"
            texte += "-----------------------------\n"
        return texte

    def rechercher_par_titre(self, titre):
        livres = self.bibliotheque.searchBooksByTitle(titre)
        if not livres:
            return "Aucun livre trouvé avec ce titre.\n"
        return self._formater_resultats(livres)

    def rechercher_par_auteur(self, auteur):
        livres = self.bibliotheque.searchBooksByAuthor(auteur)
        if not livres:
            return "Aucun livre trouvé de cet auteur.\n"
        return self._formater_resultats(livres)

    def afficher_tous_les_livres(self):
        _, texte = capture_sortie_cpp(lambda: self.bibliotheque.displayAllBooks())
        return texte

    def afficher_livres_disponibles(self):
        _, texte = capture_sortie_cpp(
            lambda: self.bibliotheque.displayAvailableBooks()
        )
        return texte

    def ajouter_utilisateur(self, nom, identifiant):
        if self.bibliotheque.findUserById(identifiant):
            return f"Erreur : Un utilisateur avec l'ID {identifiant} existe déjà.\n"
        self.bibliotheque.addUser(liaison.User(nom, identifiant))
        return "Utilisateur ajouté avec succès !\n"

    def afficher_tous_les_utilisateurs(self):
        _, texte = capture_sortie_cpp(lambda: self.bibliotheque.displayAllUsers())
        return texte

    def emprunter_livre(self, isbn, identifiant):
        if self.bibliotheque.checkOutBook(isbn, identifiant):
            return "Livre emprunté avec succès !\n"
        return (
            "Erreur : Impossible d'emprunter le livre. "
            "Vérifiez l'ISBN, l'ID utilisateur et la disponibilité du livre.\n"
        )

    def retourner_livre(self, isbn):
        if self.bibliotheque.returnBook(isbn):
            return "Livre retourné avec succès !\n"
        return (
            "Erreur : Impossible de retourner le livre. "
            "Vérifiez l'ISBN et que le livre est bien emprunté.\n"
        )

    def statistiques(self):
        return (
            "\n=== STATISTIQUES DE LA BIBLIOTHÈQUE ===\n"
            f"Total des Livres : {self.bibliotheque.getTotalBooks()}\n"
            f"Livres Disponibles : {self.bibliotheque.getAvailableBookCount()}\n"
            f"Livres Empruntés : {self.bibliotheque.getCheckedOutBookCount()}\n"
            f"Total des Utilisateurs : {len(self.bibliotheque.getAllUsers())}\n"
        )

    def sauvegarder(self):
        reussi, messages = capture_sortie_cpp(
            lambda: self.gestionnaire_fichiers.saveLibraryData(self.bibliotheque)
        )
        if reussi:
            return messages + "Données de la bibliothèque sauvegardées avec succès !\n"
        return messages + "Erreur lors de la sauvegarde des données de la bibliothèque.\n"

    def creer_sauvegarde(self):
        _, messages = capture_sortie_cpp(
            lambda: self.gestionnaire_fichiers.createBackup()
        )
        return messages

    def quitter(self):
        _, messages = capture_sortie_cpp(
            lambda: self.gestionnaire_fichiers.saveLibraryData(self.bibliotheque)
        )
        return (
            "Sauvegarde des données avant la fermeture...\n"
            + messages
            + "Merci d'avoir utilisé le Système de Gestion de Bibliothèque Personnelle !\n"
        )
