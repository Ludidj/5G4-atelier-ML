"""Fenêtre minimale pour vérifier l'environnement graphique de l'atelier.

Ce script ne contient aucune logique de bibliothèque : il sert uniquement à
confirmer que Tkinter/CustomTkinter s'ouvrent et se ferment correctement.
"""


import customtkinter as ctk


def creer_fenetre():
    """Construit une fenêtre simple avec un bouton de fermeture."""
    fenetre = ctk.CTk()
    fenetre.title("Test de l'environnement graphique")
    fenetre.geometry("320x120")
    bouton = ctk.CTkButton(fenetre, text="Fermer", command=fenetre.destroy)
    bouton.pack(pady=24)
    return fenetre


def main():
    creer_fenetre().mainloop()


if __name__ == "__main__":
    main()
