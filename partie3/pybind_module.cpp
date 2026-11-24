// Fichier d'interface C++ : expose UNIQUEMENT les classes et methodes
// publiques du gestionnaire de bibliotheque original (dossier agent/).
// Aucune logique metier n'est ajoutée ici.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

namespace py = pybind11;

PYBIND11_MODULE(bibliotheque_binding, m) {
    m.doc() = "Liaison pybind11 des classes originales de la bibliotheque (agent/)";

    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string &, const std::string &, const std::string &>())
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
        .def(py::init<const std::string &, const std::string &>())
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

    py::class_<Library>(m, "Library")
        .def(py::init<>())
        .def("addBook", &Library::addBook)
        .def("removeBook", &Library::removeBook)
        .def("findBookByISBN", &Library::findBookByISBN,
             py::return_value_policy::reference_internal)
        // Les methodes originales retournent vector<Book*> sur des objets detenus
        // par Library. On retourne des copies par valeur : memes donnees, aucune
        // ambiguite de propriete cote Python.
        .def("searchBooksByTitle", [](Library &self, const std::string &title) {
            std::vector<Book> resultats;
            for (Book *livre : self.searchBooksByTitle(title)) {
                resultats.push_back(*livre);
            }
            return resultats;
        })
        .def("searchBooksByAuthor", [](Library &self, const std::string &author) {
            std::vector<Book> resultats;
            for (Book *livre : self.searchBooksByAuthor(author)) {
                resultats.push_back(*livre);
            }
            return resultats;
        })
        .def("getAvailableBooks", [](Library &self) {
            std::vector<Book> resultats;
            for (Book *livre : self.getAvailableBooks()) {
                resultats.push_back(*livre);
            }
            return resultats;
        })
        .def("getAllBooks", [](Library &self) {
            std::vector<Book> resultats;
            for (Book *livre : self.getAllBooks()) {
                resultats.push_back(*livre);
            }
            return resultats;
        })
        .def("addUser", &Library::addUser)
        .def("findUserById", &Library::findUserById,
             py::return_value_policy::reference_internal)
        .def("getAllUsers", [](Library &self) {
            std::vector<User> resultats;
            for (User *utilisateur : self.getAllUsers()) {
                resultats.push_back(*utilisateur);
            }
            return resultats;
        })
        .def("checkOutBook", &Library::checkOutBook)
        .def("returnBook", &Library::returnBook)
        .def("displayAllBooks", &Library::displayAllBooks)
        .def("displayAvailableBooks", &Library::displayAvailableBooks)
        .def("displayAllUsers", &Library::displayAllUsers)
        .def("getTotalBooks", &Library::getTotalBooks)
        .def("getAvailableBookCount", &Library::getAvailableBookCount)
        .def("getCheckedOutBookCount", &Library::getCheckedOutBookCount);

    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string &, const std::string &>())
        .def("saveLibraryData", &FileManager::saveLibraryData)
        .def("loadLibraryData", &FileManager::loadLibraryData)
        .def("saveBooksToFile", &FileManager::saveBooksToFile)
        .def("saveUsersToFile", &FileManager::saveUsersToFile)
        .def("loadBooksFromFile", &FileManager::loadBooksFromFile)
        .def("loadUsersFromFile", &FileManager::loadUsersFromFile)
        .def("fileExists", &FileManager::fileExists)
        .def("createBackup", &FileManager::createBackup);
}
