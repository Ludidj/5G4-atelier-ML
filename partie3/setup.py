
"""Compilation du module pybind11 à partir du code C++ original (agent/)."""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

SOURCES = [
    "pybind_module.cpp",
    "../agent/book.cpp",
    "../agent/user.cpp",
    "../agent/library.cpp",
    "../agent/filemanager.cpp",
]

setup(
    packages=[],
    py_modules=[],
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
