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

- No lockfile, CI, or test/lint config. The only build config is `partie3/pyproject.toml`; the dependency source of truth is `.devcontainer/devcontainer.json` → `postCreateCommand`, which now also installs `customtkinter pybind11` (Python 3.12 image). `test_modele.ipynb` also imports Pillow, which is absent from that list.
- `.venv/bin/python` currently symlinks to system Python 3.9 while the installed site-packages are 3.12; use `/usr/local/bin/python3.12` (the Jupyter kernel) for ad-hoc checks.
- `classification.ipynb` forces CPU with `tf.config.set_visible_devices([], 'GPU')` and runs 10 + 50 epochs; re-running it is slow.

## Partie 3 — interface graphique C++ / Python (reprise depuis zéro)

- `agent/` is the original C++ library program copied unchanged from `Ludidj/420-5G4-ML` (sources, `CMakeLists.txt`, `data/books.txt`, `data/users.txt`, `.devcontainer/`). Do not change its logic: the Python GUI reuses these classes through pybind11 and reproduces the original menu labels and behaviour.
- The original CLI is `main.cpp` (menu 1..13 + 0 to quit). It saves both data files on exit, so test it on a copy of `agent/data/`, not on the tracked files. `g++ -std=c++17 -Wall -Wextra -Wpedantic agent/*.cpp -o <sortie>` compiles it here; `cmake` is only available via `agent/.devcontainer/`. The generated `agent/bibliotheque` binary is gitignored.
- `partie3/` was written from scratch on branch `partie3-reprise` (the old implementation was not reused). `pybind_module.cpp` exposes the original `Book`, `User`, `Library` and `FileManager` methods only. Build with `cd partie3 && /usr/local/bin/python3.12 setup.py build_ext --inplace`; generated `build/` and `.so` are gitignored. Import from that directory with `import bibliotheque_binding`.
- `Library` owns `unique_ptr` and returns raw pointers. Single pointers are exposed with `reference_internal`; methods returning `vector<Book*>`/`vector<User*>` return copies by value in the binding so Python never owns C++ objects.
- `partie3/bibliotheque.py` is the facade holding the 14 menu actions and the original CLI strings. `partie3/app.py` is the CustomTkinter GUI and only displays them. `capture_sortie_cpp()` redirects fd 1 and flushes libc stdio so the original `displayAllBooks`/`displayAvailableBooks`/`displayAllUsers`/load messages appear verbatim. The GUI accepts the original `-d`/`--data-dir` option; without it, it starts empty like the CLI. See `partie3/README.md`.
- Tests run from `partie3/`: `/usr/local/bin/python3.12 -m unittest -v test_binding test_parite test_interface` (26 tests). They compile the original CLI on the fly and use temporary copies of `agent/data/`; `test_interface.py` needs a working `DISPLAY` (`:3` here).
- `chatsLogs/` contains OpenCode conversations exported as Markdown (one file per session, user/assistant messages; tool calls and reasoning omitted). Regenerate with `/usr/local/bin/python3.12 partie3/exporter_chats.py`, especially just before the final commit.
- The final commit on the branch must be exactly `[REMISE] Partie 3`, followed by the Pull Request with no additional commit.
