# Partie 3 — interface graphique de la bibliothèque

Le code C++ original se trouve dans `../agent/` et n'est pas modifié.

## Fichiers

- `pybind_module.cpp` : expose à Python les classes `Book`, `User`, `Library` et `FileManager` telles quelles (via pybind11).
- `setup.py` : compile ce module avec les sources C++ originales.
- `app.py` : interface CustomTkinter qui remplace le menu en ligne de commande (`agent/main.cpp`). Les 13 actions et `0.  Quitter` gardent leurs libellés et leurs messages d'origine.
- `test_connexion.py` : comparaison Python/C++ avec le CLI (étape D).
- `test_interface.py` : tests de l'interface et de ses actions (étape F).
- `exporter_chats.py` : convertit les exports JSON d'OpenCode en Markdown dans `../chatsLogs/` (étape G).

## Compilation du module pybind11

```bash
cd partie3
/usr/local/bin/python3.12 setup.py build_ext --inplace
```

## Lancement de l'interface

```bash
cd partie3
/usr/local/bin/python3.12 app.py -d ../agent/data
```

L'option `-d` / `--data-dir` est celle du programme original. Sans elle, le
programme démarre avec une bibliothèque vide, comme le CLI d'origine.
Les fichiers `books.txt` et `users.txt` du répertoire indiqué sont lus au
démarrage et réécrits à la sauvegarde et à la fermeture. Pour les tests, il faut
donc passer une **copie** du répertoire `agent/data/`.
