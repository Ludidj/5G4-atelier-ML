"""Compilation du module pybind11 pour la Partie 3.

Les sources C++ originales restent dans agent/ et ne sont pas modifiées :
ce script les compile telles quelles avec le nouveau fichier d'interface.

    cd partie3
    python3.12 setup.py build_ext --inplace
"""

from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

AGENT_DIR = Path(__file__).resolve().parent.parent / "agent"

# main.cpp est volontairement absent : son menu en ligne de commande est
# remplacé par l'interface graphique CustomTkinter de la Partie 3.
SOURCES = ["pybind_module.cpp"] + [
    str(AGENT_DIR / f"{name}.cpp")
    for name in ("book", "user", "library", "filemanager")
]

setup(
    name="bibliotheque_binding",
    version="1.0",
    ext_modules=[
        Pybind11Extension(
            "bibliotheque_binding",
            SOURCES,
            include_dirs=[str(AGENT_DIR)],
            cxx_std=17,
        )
    ],
    cmdclass={"build_ext": build_ext},
)
