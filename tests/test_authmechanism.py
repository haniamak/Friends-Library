import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from operacje import Uzytkownik
from base64 import b64encode
from operacje import Base, create_engine_sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from serwer import app

class TestAuthMechanism(unittest.TestCase):
    def setUp(self):
        engine = create_engine_sqlalchemy()
        Base.metadata.create_all(engine)
        SessionLocal = scoped_session(sessionmaker(bind=engine))
        with SessionLocal() as session:
            session.query(Uzytkownik).delete()
            user1 = Uzytkownik(login="test_user", haslo="password123")
            user2 = Uzytkownik(login="user2", haslo="pass456")
            session.add_all([user1, user2])
            session.commit()
        app.testing = True
        self.client = app.test_client()

    def encode_auth(self, username, password):
        """
        Koduje dane uwierzytelnienia w formacie Base64 do nagłówka Authorization.
        """
        credentials = f"{username}:{password}"
        return {
            'Authorization': 'Basic ' + b64encode(credentials.encode()).decode()
        }

    def test_home_access_without_auth(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Access denied", response.data)

    def test_home_access_with_invalid_auth(self):
        headers = self.encode_auth("invalid_user", "wrong_password")
        response = self.client.get('/', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Access denied", response.data)

    def test_get_all_ksiazki_with_auth(self):
        headers = self.encode_auth("test_user", "password123")
        response = self.client.get('/ksiazki', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_get_ksiazka_with_auth(self):
        headers = self.encode_auth("test_user", "password123")
        response = self.client.get('/ksiazka/1', headers=headers)
        self.assertIn(response.status_code, [200, 404])

    def test_get_ksiazki_without_auth(self):
        response = self.client.get('/ksiazki')
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Access denied", response.data)

if __name__ == "__main__":
    unittest.main()
