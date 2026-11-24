"""Interface graphique CustomTkinter remplaçant le menu CLI.

La fenêtre ne contient aucune logique métier : elle affiche les libellés du
programme original et transmet les saisies à ModeleBibliotheque.
"""

import os
import sys

import customtkinter as ctk

from bibliotheque import (
    LIBELLES_MENU,
    PROMPT_AUTEUR_LIVRE,
    PROMPT_AUTEUR_RECHERCHE,
    PROMPT_ID_EMPRUNT,
    PROMPT_ID_UTILISATEUR,
    PROMPT_ISBN_EMPRUNT,
    PROMPT_ISBN_LIVRE,
    PROMPT_ISBN_RETOUR,
    PROMPT_ISBN_SUPPRESSION,
    PROMPT_NOM_UTILISATEUR,
    PROMPT_TITRE_LIVRE,
    PROMPT_TITRE_RECHERCHE,
    ModeleBibliotheque,
)

CHAMPS_PAR_ACTION = {
    1: [PROMPT_TITRE_LIVRE, PROMPT_AUTEUR_LIVRE, PROMPT_ISBN_LIVRE],
    2: [PROMPT_ISBN_SUPPRESSION],
    3: [PROMPT_TITRE_RECHERCHE],
    4: [PROMPT_AUTEUR_RECHERCHE],
    7: [PROMPT_NOM_UTILISATEUR, PROMPT_ID_UTILISATEUR],
    9: [PROMPT_ISBN_EMPRUNT, PROMPT_ID_EMPRUNT],
    10: [PROMPT_ISBN_RETOUR],
}

METHODE_PAR_ACTION = {
    1: "ajouter_livre",
    2: "supprimer_livre",
    3: "rechercher_par_titre",
    4: "rechercher_par_auteur",
    5: "afficher_tous_les_livres",
    6: "afficher_livres_disponibles",
    7: "ajouter_utilisateur",
    8: "afficher_tous_les_utilisateurs",
    9: "emprunter_livre",
    10: "retourner_livre",
    11: "statistiques",
    12: "sauvegarder",
    13: "creer_sauvegarde",
    0: "quitter",
}


class Formulaire(ctk.CTkToplevel):
    """Dialogue de saisie dont les libellés sont ceux du CLI."""

    def __init__(self, parent, titre, invites, callback):
        super().__init__(parent)
        self.title(titre)
        self.callback = callback
        self.entrees = []

        for rang, invite in enumerate(invites):
            etiquette = ctk.CTkLabel(self, text=invite)
            etiquette.grid(row=rang, column=0, padx=12, pady=(12, 0), sticky="w")
            entree = ctk.CTkEntry(self, width=320)
            entree.grid(row=rang, column=1, padx=12, pady=(12, 0), sticky="ew")
            entree.bind("<Return>", lambda _evenement: self.valider())
            self.entrees.append(entree)

        ligne_boutons = len(invites)
        bouton_valider = ctk.CTkButton(self, text=titre, command=self.valider)
        bouton_valider.grid(row=ligne_boutons, column=0, padx=12, pady=12)
        bouton_annuler = ctk.CTkButton(
            self, text=LIBELLES_MENU[13], command=self.annuler
        )
        bouton_annuler.grid(row=ligne_boutons, column=1, padx=12, pady=12)

        self.transient(parent)
        self.after(100, lambda: self.entrees[0].focus_set())

    def valider(self):
        valeurs = tuple(entree.get() for entree in self.entrees)
        self.destroy()
        self.callback(valeurs)

    def annuler(self):
        self.destroy()


class BibliothequeApp(ctk.CTk):
    def __init__(self, dossier_donnees=None):
        super().__init__()
        self.title("SYSTÈME DE GESTION DE BIBLIOTHÈQUE PERSONNELLE")
        self.geometry("900x620")

        self.modele = ModeleBibliotheque(dossier_donnees)
        self.formulaire_courant = None
        self.en_quittement = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.cadre_boutons = ctk.CTkFrame(self)
        self.cadre_boutons.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        for rang, libelle in enumerate(LIBELLES_MENU):
            numero = rang + 1 if rang < 13 else 0
            bouton = ctk.CTkButton(
                self.cadre_boutons,
                text=libelle,
                command=lambda n=numero: self.executer_action(n),
            )
            bouton.grid(row=rang, column=0, padx=8, pady=4, sticky="ew")

        self.zone_sortie = ctk.CTkTextbox(self, wrap="word")
        self.zone_sortie.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self._quitter)
        self._afficher(self.modele.demarrer())
        self._afficher(self.modele.menu())

    def _afficher(self, texte):
        self.zone_sortie.configure(state="normal")
        self.zone_sortie.insert("end", texte)
        self.zone_sortie.configure(state="disabled")
        self.zone_sortie.see("end")

    def _quitter(self):
        if not self.en_quittement:
            self.executer_action(0)

    def executer_action(self, numero, valeurs=None):
        """Exécute une action du menu. `valeurs` permet de sauter le dialogue."""
        if numero == 0:
            self.en_quittement = True
            texte = self.modele.quitter()
            self._afficher(texte)
            self.after(200, self.destroy)
            return texte

        invites = CHAMPS_PAR_ACTION.get(numero)
        if invites and valeurs is None:
            self.formulaire_courant = Formulaire(
                self,
                LIBELLES_MENU[numero - 1],
                invites,
                lambda saisies: self.executer_action(numero, saisies),
            )
            return None

        methode = getattr(self.modele, METHODE_PAR_ACTION[numero])
        texte = methode(*(valeurs or ()))
        self._afficher(texte)
        return texte


def analyser_arguments(argv):
    """Reprend la gestion de -d/--data-dir du programme original."""
    dossier = None
    index = 1
    while index < len(argv):
        argument = argv[index]
        if argument in ("--data-dir", "-d"):
            if index + 1 >= len(argv):
                print(
                    "Erreur : " + argument + " nécessite un répertoire.",
                    file=sys.stderr,
                )
                print(
                    "Usage: " + argv[0] + " [--data-dir|-d <répertoire>]",
                    file=sys.stderr,
                )
                return None, 1
            dossier = argv[index + 1]
            index += 2
        else:
            print("Erreur : argument inconnu '" + argument + "'.", file=sys.stderr)
            print(
                "Usage: " + argv[0] + " [--data-dir|-d <répertoire>]",
                file=sys.stderr,
            )
            return None, 1
    return dossier, 0


def main(argv=None):
    argv = sys.argv if argv is None else argv
    dossier, code = analyser_arguments(argv)
    if code:
        return code
    if dossier is not None and not os.path.isdir(dossier):
        print("Erreur : le répertoire " + dossier + " n'existe pas.", file=sys.stderr)
        print(
            "Usage: " + argv[0] + " [--data-dir|-d <répertoire>]",
            file=sys.stderr,
        )
        return 1

    application = BibliothequeApp(dossier)
    application.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
