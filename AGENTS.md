# AGENTS.md

Small ML workshop repo: all logic lives in Jupyter notebooks under `apprentissage/`. No application entrypoint, package, or test suite.

## Partie 3 — interface graphique C++ / Python (en cours)

- `agent/` is the original C++ library program copied unchanged from `Ludidj/420-5G4-ML` (sources, `CMakeLists.txt`, `data/books.txt`, `data/users.txt`, `.devcontainer/`). Do not change its logic: the Python GUI must reuse these classes through pybind11 and reproduce the original menu labels and behavior.
- The original CLI is `main.cpp` (menu 1..13 + 0 to quit). It saves both data files on exit, so test it on a copy of `agent/data/`, not on the tracked files. `g++ -std=c++17 -Wall -Wextra -Wpedantic agent/*.cpp -o <sortie>` compiles it here; `cmake` is only available via `agent/.devcontainer/`. The generated `agent/bibliotheque` binary is gitignored.
- Keep the notebooks in `apprentissage/` untouched; they are the delivered parties 1 and 2. Work in progress order: A C++ integration → B Python deps → C pybind11 binding → D Python/C++ checks → E CustomTkinter GUI → F tests → G `chatsLogs/` Markdown exports + AGENTS.md → H final `[REMISE] Partie 3` commit and PR.

## Two independent notebook pipelines

- Pokémon win prediction: `apprentissage/partie1_2.ipynb` → `partie3_entrainement.ipynb` → `partie3_predictions.ipynb`, in that order. The first writes `datas/dataset.csv`; the second trains a RandomForest and writes `apprentissage/modele/modele_pokemon.mod` (joblib); the third loads that model plus `datas/pokedex.csv`.
- Fashion-MNIST CNN: `apprentissage/analyse_image/classification.ipynb` trains and writes `modele/modele.json` + `modele/modele.weights.h5`; `test_modele.ipynb` loads them to classify one `image.png`.

## Paths and data quirks

- No single working directory works for every notebook. The three `apprentissage/*.ipynb` files use paths relative to `apprentissage/` (`../datas/...`, `modele/...`); the two `analyse_image/` files use paths relative to their own folder (`../../datas/...`, `../modele/...`). `test_modele.ipynb` even mixes styles (`../modele/modele.json` vs `modele/modele.weights.h5`) — verify paths before blaming code.
- `datas/dataset.csv` is tab-separated despite the `.csv` extension: written with `sep='\t'` and read with `delimiter='\t'`.
- Only `datas/pokedex.csv`, `datas/combats.csv`, and `datas/dataset.csv` are tracked. Fashion-MNIST CSVs/IDX files are gitignored, so a fresh clone cannot run `classification.ipynb` without supplying them locally.

## Current artifact state

- `apprentissage/modele/modele.json` is tracked but empty (0 bytes); there is no `modele.weights.h5` or `image.png` in the repo. `test_modele.ipynb` currently fails at `model_from_json` — regenerate artifacts via `classification.ipynb` and provide an image.
- `apprentissage/modele/modele_pokemon.mod` is checked in (~2.6 MB), so `partie3_predictions.ipynb` can run without retraining.

## Environment / verification

- No `requirements.txt`, `pyproject.toml`, lockfile, CI, or test/lint/build config. The only dependency definition is `.devcontainer/devcontainer.json` → `postCreateCommand`: `pip3 install --user pandas matplotlib seaborn ipykernel joblib scikit-learn tensorflow keras-preprocessing customtkinter pybind11` (Python 3.12 image; the two last packages were added for Partie 3). `test_modele.ipynb` also imports Pillow, which is absent from that list.
- Partie 3 dependencies checked with `/usr/local/bin/python3.12`: `tkinter` 8.6 (already present), `customtkinter` 6.0.0, `pybind11` 3.1.0, `PIL` 13.0.0. The `agent/.devcontainer/Dockerfile` (C++ container) already installs `python3-pybind11`, `pybind11-dev` and `python3-tk`.
- `.venv/bin/python` currently symlinks to system Python 3.9 while the installed site-packages are 3.12; use `/usr/local/bin/python3.12` (the Jupyter kernel) for ad-hoc checks.
- `classification.ipynb` forces CPU with `tf.config.set_visible_devices([], 'GPU')` and runs 10 + 50 epochs; re-running it is slow.
