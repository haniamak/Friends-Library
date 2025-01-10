import sys
#sys.path.insert(0, '../src')
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import unittest
from operacje import Przyjaciel



class TestPrzyjaciel(unittest.TestCase):    
    def test_przyjaciel_repr(self):
        przyjaciel = Przyjaciel(imie='Imie Testowe', email='Email Testowy')
        przyjaciel.id = 2
        self.assertEqual(
            repr(przyjaciel),
            "Przyjaciel(id=2, imie='Imie Testowe', email='Email Testowy')")

    def test_email_not_empty(self):
        with self.assertRaises(ValueError):
            Przyjaciel(imie="Imie Testowe", email="")

    def test_imie_not_empty(self):
        with self.assertRaises(ValueError):
            Przyjaciel(imie="", email="Email Testowy")


if __name__ == "__main__":
    unittest.main()
