import sys
#sys.path.insert(0, '../src')
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import unittest
from operacje import Ksiazka

class TestKsiazka(unittest.TestCase):
    def test_ksiazka_repr(self):
        ksiazka = Ksiazka(
            autor="Autor Testowy",
            tytul="Tytul Testowy",
            rok_wydania=2020)
        ksiazka.id = 1
        self.assertEqual(
            repr(ksiazka),
            f"Ksiazka(id=1, autor='Autor Testowy', "
            f"tytul='Tytul Testowy', rok_wydania=2020)")

    def test_rok_wydania_positive(self):
        with self.assertRaises(ValueError):
            Ksiazka(
                autor="Autor Testowy",
                tytul="Tytul Testowy",
                rok_wydania=-2020)

    def test_autor_not_empty(self):
        with self.assertRaises(ValueError):
            Ksiazka(autor="", tytul="Tytul Testowy", rok_wydania=2020)


if __name__ == "__main__":
    unittest.main()
