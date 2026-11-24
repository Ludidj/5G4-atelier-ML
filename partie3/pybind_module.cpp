#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

// En-têtes du programme C++ original : aucune logique n'est modifiée ici.
// Ce fichier ne fait qu'exposer au Python les classes et méthodes déjà définies
// dans agent/. main.cpp n'est pas inclus : son menu CLI est remplacé par la GUI.
#include "book.h"
#include "user.h"
#include "library.h"
#include "filemanager.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_binding, m) {
    m.doc() = "Interface pybind11 vers les classes C++ originales de la bibliothèque";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>())
        .def("getTitle", &Book::getTitle)
        .def("getAuthor", &Book::getAuthor)
        .def("getISBN", &Book::getISBN)
        .def("getAvailability", &Book::getAvailability)
        .def("getBorrowerId", &Book::getBorrowerId)
        .def("setTitle", &Book::setTitle)
        .def("setAuthor", &Book::setAuthor)
        .def("setISBN", &Book::setISBN)
        .def("setAvailability", &Book::setAvailability)
        .def("setBorrowerId", &Book::setBorrowerId)
        .def("checkOut", &Book::checkOut)
        .def("returnBook", &Book::returnBook)
        .def("toString", &Book::toString)
        .def("toFileFormat", &Book::toFileFormat)
        .def("fromFileFormat", &Book::fromFileFormat);

    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>())
        .def("getName", &User::getName)
        .def("getUserId", &User::getUserId)
        .def("getBorrowedBooks", &User::getBorrowedBooks)
        .def("setName", &User::setName)
        .def("setUserId", &User::setUserId)
        .def("borrowBook", &User::borrowBook)
        .def("returnBook", &User::returnBook)
        .def("hasBorrowedBook", &User::hasBorrowedBook)
        .def("getNumberOfBorrowedBooks", &User::getNumberOfBorrowedBooks)
        .def("toString", &User::toString)
        .def("toFileFormat", &User::toFileFormat)
        .def("fromFileFormat", &User::fromFileFormat);

    // Les méthodes qui rendent un pointeur vers un élément possédé par Library
    // utilisent reference_internal : la durée de vie de l'objet Python reste liée
    // à celle de la bibliothèque, comme dans le programme C++ d'origine.
    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("addBook", &Library::addBook)
        .def("removeBook", &Library::removeBook)
        .def("findBookByISBN", &Library::findBookByISBN, py::return_value_policy::reference_internal)
        .def("searchBooksByTitle", &Library::searchBooksByTitle, py::return_value_policy::reference_internal)
        .def("searchBooksByAuthor", &Library::searchBooksByAuthor, py::return_value_policy::reference_internal)
        .def("getAvailableBooks", &Library::getAvailableBooks, py::return_value_policy::reference_internal)
        .def("getAllBooks", &Library::getAllBooks, py::return_value_policy::reference_internal)
        .def("addUser", &Library::addUser)
        .def("findUserById", &Library::findUserById, py::return_value_policy::reference_internal)
        .def("getAllUsers", &Library::getAllUsers, py::return_value_policy::reference_internal)
        .def("checkOutBook", &Library::checkOutBook)
        .def("returnBook", &Library::returnBook)
        .def("displayAllBooks", &Library::displayAllBooks)
        .def("displayAvailableBooks", &Library::displayAvailableBooks)
        .def("displayAllUsers", &Library::displayAllUsers)
        .def("getTotalBooks", &Library::getTotalBooks)
        .def("getAvailableBookCount", &Library::getAvailableBookCount)
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>())
        .def("saveLibraryData", &FileManager::saveLibraryData)
        .def("loadLibraryData", &FileManager::loadLibraryData)
        .def("saveBooksToFile", &FileManager::saveBooksToFile)
        .def("saveUsersToFile", &FileManager::saveUsersToFile)
        .def("loadBooksFromFile", &FileManager::loadBooksFromFile)
        .def("loadUsersFromFile", &FileManager::loadUsersFromFile)
        .def("fileExists", &FileManager::fileExists)
        .def("createBackup", &FileManager::createBackup);
}
