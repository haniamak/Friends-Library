# import sys
# sys.path.insert(0, '../src')
# import unittest
# from src.operacje import Przyjaciel

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from src.operacje import Przyjaciel

class TestPrzyjaciel(unittest.TestCase):
  def test_przyjaciel_repr(self):
    przyjaciel = Przyjaciel(imie="Imie Testowe", email="Email Testowy")
    przyjaciel.id = 1
    self.assertEqual(repr(przyjaciel), "Przyjaciel(id=1, imie='Imie Testowe', email='Email Testowy')")

  def test_email_not_empty(self):
    with self.assertRaises(ValueError):
      Przyjaciel(imie="Imie Testowe", email="")
  
  def test_imie_not_empty(self):
    with self.assertRaises(ValueError):
      Przyjaciel(imie="", email="Email Testowy")

if __name__ == "__main__":
  unittest.main()