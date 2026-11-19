# AGENTS.md

Small ML workshop repo: all logic lives in Jupyter notebooks under `apprentissage/`. No application entrypoint, package, or test suite.

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

- No `requirements.txt`, `pyproject.toml`, lockfile, CI, or test/lint/build config. The only dependency definition is `.devcontainer/devcontainer.json` → `postCreateCommand`: `pip3 install --user pandas matplotlib seaborn ipykernel joblib scikit-learn tensorflow keras-preprocessing` (Python 3.12 image). `test_modele.ipynb` also imports Pillow, which is absent from that list.
- `.venv/bin/python` currently symlinks to system Python 3.9 while the installed site-packages are 3.12; use `/usr/local/bin/python3.12` (the Jupyter kernel) for ad-hoc checks.
- `classification.ipynb` forces CPU with `tf.config.set_visible_devices([], 'GPU')` and runs 10 + 50 epochs; re-running it is slow.
