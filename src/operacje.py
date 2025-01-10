from __future__ import annotations
from datetime import datetime
import json
from sqlalchemy import CheckConstraint, ForeignKeyConstraint
from sqlalchemy import create_engine, Column, Integer, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, relationship
import argparse
from sqlalchemy.engine import Engine

def create_engine_sqlalchemy() -> Engine:
    """
    Tworzy silnik do połączenia z bazą danych SQL Server.

    :return: Obiekt silnika SQLAlchemy (engine).
    """
    server = 'LAPTOP-KS5QVHTA\\SQLEXPRESS'
    database = 'Python'
    engine = create_engine(
        f'mssql+pyodbc://{server}/{database}?'
        f'driver=ODBC+Driver+17+for+SQL+Server'
        )
    return engine


class Base(DeclarativeBase):
    """
    Bazowa klasa dla wszystkich modeli SQLAlchemy.
    """
    pass


class Ksiazka(Base):
    """
    Reprezentuje tabelę 'Ksiazki' w bazie danych.

    :param id: Klucz główny (unikalny identyfikator książki).
    :param autor: Autor książki (tekst, wymagany).
    :param tytul: Tytuł książki (tekst, wymagany).
    :param rok_wydania: Rok wydania książki (liczba całkowita, musi być > 0).
    """
    __tablename__ = 'Ksiazki'
    id: Column[int] = Column(Integer, primary_key=True)
    autor: Column[str] = Column(String, nullable=False)
    tytul: Column[str] = Column(String, nullable=False)
    rok_wydania: Column[int] = Column(Integer, nullable=False)

    wypozyczenia = relationship('Wypozyczenie', back_populates='ksiazka')

    __table_args__ = (CheckConstraint(
        rok_wydania > 0, name='check_rok_wydania_positive'),)

    def __repr__(self):
        return (
            f"Ksiazka("
            f"id={self.id}, autor='{self.autor}', "
            f"tytul='{self.tytul}', "
            f"rok_wydania={self.rok_wydania})"
            )

    def __init__(self, autor: Column[str], tytul: Column[str], rok_wydania: Column[int]):
        """
        Konstruktor klasy Ksiazka.

        :param autor: Autor książki.
        :param tytul: Tytuł książki.
        :param rok_wydania: Rok wydania książki (musi być > 0).
        :raises ValueError: Jeśli rok wydania jest niedodatni lub autor jest pusty.
        """
        if rok_wydania <= 0:
            raise ValueError("Rok wydania musi być dodatni.")
        if not autor.strip():
            raise ValueError("Autor nie może być pusty.")
        self.autor = autor
        self.tytul = tytul
        self.rok_wydania = rok_wydania


class Przyjaciel(Base):
    """
    Reprezentuje tabelę 'Przyjaciele' w bazie danych.

    :param id: Klucz główny (unikalny identyfikator przyjaciela).
    :param imie: Imię przyjaciela (tekst, wymagany).
    :param email: Email przyjaciela (tekst, wymagany, unikalny).
    """
    __tablename__ = 'Przyjaciele'
    id: Column[int] = Column(Integer, primary_key=True)
    imie: Column[str] = Column(String(255), nullable=False)
    email: Column[str] = Column(String(255), nullable=False, unique=True)

    wypozyczenia = relationship('Wypozyczenie', back_populates='przyjaciel')

    __table_args__ = (CheckConstraint(
        "email LIKE '%@%._%'", name='check_email_format'),)

    def __repr__(self):
        return (
            f"Przyjaciel("
            f"id={self.id}, imie='{self.imie}', "
            f"email='{self.email}')"
            )

    def __init__(self, imie: Column[str], email: Column[str]):
        """
        Konstruktor klasy Przyjaciel.

        :param imie: Imię przyjaciela.
        :param email: Email przyjaciela.
        :raises ValueError: Jeśli imię lub email są puste.
        """
        if not imie.strip():
            raise ValueError("Imie nie może być puste.")
        if not email:
            raise ValueError("Email nie może być pusty.")
        self.imie = imie
        self.email = email


class Wypozyczenie(Base):
    """
    Reprezentuje tabelę 'Wypozyczenia' w bazie danych.

    :param id: Klucz główny (unikalny identyfikator wypożyczenia).
    :param ksiazka_id: Id książki powiązanej z wypożyczeniem.
    :param przyjaciel_id: Id przyjaciela powiązanego z wypożyczeniem.
    :param data_wypozyczenia: Data wypożyczenia książki (domyślnie bieżąca data).
    """
    __tablename__ = 'Wypozyczenia'
    id: Column[int] = Column(Integer, primary_key=True)
    ksiazka_id: Column[int] = Column(Integer, ForeignKey('Ksiazki.id'), nullable=False)
    przyjaciel_id: Column[int] = Column(Integer, ForeignKey(
        'Przyjaciele.id'), nullable=False)
    data_wypozyczenia: Column[str] = Column(
        String, nullable=False, default=datetime.now().strftime("%Y-%m-%d"))

    ksiazka = relationship('Ksiazka', back_populates='wypozyczenia')
    przyjaciel = relationship('Przyjaciel', back_populates='wypozyczenia')

    __table_args__ = (ForeignKeyConstraint(['przyjaciel_id'], [
                      'Przyjaciele.id'], name='fk_przyjaciel_exists'),)

    def __repr__(self):
        return (
            f"Wypozyczenie("
            f"id={self.id}, ksiazka_id={self.ksiazka_id}, "
            f"przyjaciel_id={self.przyjaciel_id}, "
            f"data_wypozyczenia='{self.data_wypozyczenia}', "
        )


def stworz_tabele(engine: Engine) -> None:
    """
    Tworzy wszystkie tabele w bazie danych na podstawie zdefiniowanych modeli.

    :param engine: Obiekt silnika SQLAlchemy.
    """
    Base.metadata.create_all(engine)


def dodaj_ksiazke(session, autor: Column[str], tytul: Column[str], rok_wydania: Column[int]) -> None:
    """
    Dodaje nową książkę do bazy danych i zapisuje dane do pliku JSON.

    :param session: Sesja bazy danych SQLAlchemy.
    :param autor: Autor książki.
    :param tytul: Tytuł książki.
    :param rok_wydania: Rok wydania książki.
    """
    ksiazka = Ksiazka(autor=autor, tytul=tytul, rok_wydania=rok_wydania)
    session.add(ksiazka)
    session.commit()
    print(f"Ksiazka {ksiazka.tytul} zostala dodana.")
    ksiazki = session.query(Ksiazka).all()
    ksiazki_json = [{"id": k.id, "autor": k.autor, "tytul": k.tytul,
                     "rok_wydania": k.rok_wydania} for k in ksiazki]
    with open('ksiazki.json', 'w', encoding='utf-8') as f:
        json.dump(ksiazki_json, f, ensure_ascii=False, indent=4)


def dodaj_przyjaciela(session, imie: Column[str], email: Column[str]) -> None:
    """
    Dodaje nowego przyjaciela do bazy danych, zapisuje zmiany 
    i aktualizuje plik JSON z listą przyjaciół.

    :param session: Sesja bazy danych SQLAlchemy.
    :param imie: Imię nowego przyjaciela.
    :param email: Adres email nowego przyjaciela.
    """
    przyjaciel = Przyjaciel(imie=imie, email=email)
    session.add(przyjaciel)
    session.commit()
    print(f"Przyjaciel {przyjaciel.imie} zostal dodany.")
    przyjaciele = session.query(Przyjaciel).all()
    przyjaciele_json = [{"id": p.id, "imie": p.imie,
                         "email": p.email} for p in przyjaciele]
    with open('przyjaciele.json', 'w', encoding='utf-8') as f:
        json.dump(przyjaciele_json, f, ensure_ascii=False, indent=4)


def wypozycz_ksiazke(session, ksiazka_id: Column[int], przyjaciel_id: Column[int]) -> None:
    """
    Wypożycza książkę przyjacielowi, jeśli książka nie jest już wypożyczona.
    
    :param session: Sesja bazy danych SQLAlchemy.
    :param ksiazka_id: ID książki do wypożyczenia.
    :param przyjaciel_id: ID przyjaciela wypożyczającego książkę.
    """
    czy_wypozyczona = session.query(Wypozyczenie).filter_by(
        ksiazka_id=ksiazka_id).first()
    if czy_wypozyczona:
        ksiazka = session.get(Ksiazka, ksiazka_id)
        print(f"Ksiazka '{ksiazka.tytul}' jest juz wypozyczona.")
        return
    wypozyczenie = Wypozyczenie(
        ksiazka_id=ksiazka_id, przyjaciel_id=przyjaciel_id)
    session.add(wypozyczenie)
    session.commit()
    ksiazka = session.get(Ksiazka, ksiazka_id)
    przyjaciel = session.get(Przyjaciel, przyjaciel_id)

    print(
        f"Wypozyczono ksiazke: {ksiazka.tytul} "
        f"od {przyjaciel.imie} ({przyjaciel.email})")
    wypozyczenia = session.query(Wypozyczenie).all()
    wypozyczenia_json = [
        {
            "id": w.id,
            "ksiazka_id": w.ksiazka_id,
            "przyjaciel_id": w.przyjaciel_id,
            "data_wypozyczenia": w.data_wypozyczenia
        }
        for w in wypozyczenia]
    with open('wypozyczenia.json', 'w', encoding='utf-8') as f:
        json.dump(wypozyczenia_json, f, ensure_ascii=False, indent=4)


def oddaj_ksiazke(session, ksiazka_id: Column[int]) -> None:
    """
    Przyjmuje sesję bazy danych oraz identyfikator książki,
    a następnie sprawdza, czy książka jest wypożyczona. Jeśli tak, dokonuje zwrotu
    książki, aktualizuje bazę danych oraz plik JSON z wypożyczeniami.

    :param session: Sesja bazy danych SQLAlchemy.
    :param ksiazka_id: Identyfikator książki do zwrotu.
    """
    czy_wypozyczona = session.query(Wypozyczenie).filter_by(
        ksiazka_id=ksiazka_id).first()
    if czy_wypozyczona:
        session.commit()
        ksiazka = session.get(Ksiazka, ksiazka_id)
        print(f"Oddano ksiazke: {ksiazka.tytul}")
        with open('wypozyczenia.json', 'r', encoding='utf-8') as f:
            wypozyczenia_json = json.load(f)

        wypozyczenia_json = [
            w for w in wypozyczenia_json if w["ksiazka_id"] != ksiazka_id]

        with open('wypozyczenia.json', 'w', encoding='utf-8') as f:
            json.dump(wypozyczenia_json, f, ensure_ascii=False, indent=4)
    else:
        print("Ksiazka nie jest aktualnie wypozyczona.")


def lista_ksiazek(session) -> None:
    """
    Pobiera listę wszystkich książek z bazy danych i wypisuje je na konsolę.

    :param session: Sesja bazy danych SQLAlchemy.
    """
    ksiazki = session.query(Ksiazka).all()
    for ksiazka in ksiazki:
        print(ksiazka)


def lista_przyjaciol(session) -> None:
    """
    Pobiera listę wszystkich przyjaciół z bazy danych i wypisuje ich na konsolę.

    :param session: Sesja bazy danych SQLAlchemy.

    """
    przyjaciele = session.query(Przyjaciel).all()
    for przyjaciel in przyjaciele:
        print(przyjaciel)


def zaladuj_dane_z_plikow(session) -> None:
    """
    Ładuje dane z plików JSON i dodaje je do sesji.
    Otwiera trzy pliki JSON: 'ksiazki.json', 'przyjaciele.json' oraz 'wypozyczenia.json'.
    Następnie ładuje dane z tych plików i dodaje je do sesji za pomocą odpowiednich funkcji:
    `dodaj_ksiazke`, `dodaj_przyjaciela` oraz `wypozycz_ksiazke`.

    :param session: Sesja bazy danych SQLAlchemy.
    """
    with open('ksiazki.json', 'r', encoding='utf-8') as f:
        ksiazki = json.load(f)
    with open('przyjaciele.json', 'r', encoding='utf-8') as f:
        przyjaciele = json.load(f)
    with open('wypozyczenia.json', 'r', encoding='utf-8') as f:
        wypozyczenia = json.load(f)

    for ksiazka in ksiazki:
        dodaj_ksiazke(session, ksiazka["autor"],
                      ksiazka["tytul"], ksiazka["rok_wydania"])

    for przyjaciel in przyjaciele:
        dodaj_przyjaciela(session, przyjaciel["imie"], przyjaciel["email"])

    for wypozyczenie in wypozyczenia:
        wypozycz_ksiazke(
            session, wypozyczenie["ksiazka_id"], wypozyczenie["przyjaciel_id"])


def stworz_parser() -> argparse.ArgumentParser:
    """
    Tworzy parser argumentów wykorzystywany w aplikacji
    """
    parser = argparse.ArgumentParser(
        description='Przyjacielskie wypozyczenia ksiazek')
    subparsers = parser.add_subparsers(
        dest='command', help='Dostepne polecenia')

    use_api_parser = subparsers.add_parser('api', help='Używaj api')

    dodaj_ksiazke_parser = subparsers.add_parser(
        'dodaj_ksiazke', help='Dodaj nowa ksiazke')
    dodaj_ksiazke_parser.add_argument(
        '--autor', required=True, help='Autor ksiazki')
    dodaj_ksiazke_parser.add_argument(
        '--tytul', required=True, help='Tytul ksiazki')
    dodaj_ksiazke_parser.add_argument(
        '--rok', required=True, type=int, help='Rok wydania')

    dodaj_przyjaciela_parser = subparsers.add_parser(
        'dodaj_przyjaciela', help='Dodaj nowego przyjaciela')
    dodaj_przyjaciela_parser.add_argument(
        '--imie', required=True, help='Imie przyjaciela')
    dodaj_przyjaciela_parser.add_argument(
        '--email', required=True, help='Email przyjaciela')

    wypozycz_ksiazke_parser = subparsers.add_parser(
        'wypozycz_ksiazke', help='Wypozycz ksiazke')
    wypozycz_ksiazke_parser.add_argument(
        '--ksiazka_id',
        required=True,
        type=int,
        help='ID ksiazki do wypozyczenia')
    wypozycz_ksiazke_parser.add_argument(
        '--przyjaciel_id',
        required=True,
        type=int,
        help='ID przyjaciela wypozyczajacego ksiazke')

    zwroc_ksiazke_parser = subparsers.add_parser(
        'oddaj_ksiazke', help='Oddaj wypozyczona ksiazke')
    zwroc_ksiazke_parser.add_argument(
        '--ksiazka_id', required=True, type=int, help='ID ksiazki do oddania')

    wypisz_ksiazki_parser = subparsers.add_parser(
        'lista_ksiazek', help='Wyswietl wszystkie ksiazki')

    wypisz_przyjaciol_parser = subparsers.add_parser(
        'lista_przyjaciol', help='Wyswietl wszystkich przyjaciol')

    return parser
