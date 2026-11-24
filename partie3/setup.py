"""Compilation du module pybind11 à partir du code C++ original (agent/)."""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

# Les sources C++ ne sont pas copiees : elles restent celles du projet original.
SOURCES = [
    "pybind_module.cpp",
    "../agent/book.cpp",
    "../agent/user.cpp",
    "../agent/library.cpp",
    "../agent/filemanager.cpp",
]

setup(
    ext_modules=[
        Pybind11Extension(
            "bibliotheque_binding",
            SOURCES,
            include_dirs=["../agent"],
            cxx_std=17,
        )
    ],
    cmdclass={"build_ext": build_ext},
)
