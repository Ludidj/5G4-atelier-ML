# Partie 3 — interface graphique de la bibliothèque

Reprise depuis zéro sur la branche `partie3-reprise` : l’ancienne implémentation n’a pas été réutilisée.

## Principe

- `../agent/` contient le programme C++ original, **inchangé**. Sa CLI (`main.cpp`, menu 1 à 13 + 0) reste la référence exacte des libellés et des messages.
- `pybind_module.cpp` est le fichier d’interface C++ : il expose uniquement `Book`, `User`, `Library` et `FileManager`.
- `bibliotheque.py` est la façade Python : elle enchaîne les 14 actions du menu et renvoie les textes du CLI.
- `app.py` est l’interface CustomTkinter : elle affiche les boutons et les résultats, sans logique métier.

## Compiler le module pybind11

```sh
cd partie3
/usr/local/bin/python3.12 setup.py build_ext --inplace
```

Cela compile `../agent/*.cpp` avec le module et produit `bibliotheque_binding.cpython-312-*.so` (ignoré par Git).

## Lancer l’interface

```sh
cd partie3
/usr/local/bin/python3.12 app.py -d ../agent/data
```

L’option `-d` / `--data-dir` est celle du CLI d’origine. Sans elle, l’application démarre avec une bibliothèque vide, comme le CLI. La fenêtre se ferme comme le menu `0. Quitter` : les données sont sauvegardées à la fermeture.

## Tests

```sh
cd partie3
/usr/local/bin/python3.12 -m unittest -v test_binding test_parite test_interface
```

26 tests, aucun ignoré. Ils compilent la CLI originale à la volée et travaillent sur des copies temporaires de `../agent/data/`. `test_interface.py` nécessite un `DISPLAY` valide.

## Traçabilité

```sh
/usr/local/bin/python3.12 partie3/exporter_chats.py
```

Les conversations OpenCode sont exportées en Markdown dans `chatsLogs/` (une par session, messages utilisateur/assistant seulement).
