from __future__ import annotations
import os
from sqlalchemy.orm import Session
import webbrowser
from operacje import create_engine_sqlalchemy, stworz_tabele, Base, stworz_parser, dodaj_ksiazke, dodaj_przyjaciela, wypozycz_ksiazke, oddaj_ksiazke, lista_ksiazek, lista_przyjaciol, zaladuj_dane_z_plikow

def main():
  engine = create_engine_sqlalchemy()
  Base.metadata.drop_all(engine)
  stworz_tabele(engine)  
  print("Tabele zostaly stworzone w MSSQL Server.")
  # with Session(engine) as session:
  #   # Dodajemy przykładową książkę
  #   zaladuj_dane_z_plikow(session)
  #   dodaj_ksiazke(session, autor="Adam kotek", tytul="Pan Tadeusz", rok_wydania=1111)
  #   dodaj_przyjaciela(session, imie="kania", email="kania@mak.com")
  #   wypozycz_ksiazke(session, ksiazka_id=1, przyjaciel_id=1)
  #   oddaj_ksiazke(session, 1)
  #   wypozycz_ksiazke(session, ksiazka_id=1, przyjaciel_id=1)
  #   lista_ksiazek(session)
  #   lista_przyjaciol(session)
  with Session(engine) as session:
    zaladuj_dane_z_plikow(session)
    os.system('cls' if os.name == 'nt' else 'clear')

    parser = stworz_parser()
    args = parser.parse_args()

    if args.command == 'api':
      url = 'http://127.0.0.1:5000'
      print(f"Przekierowywanie do API: {url}")
      webbrowser.open(url)
    elif args.command == 'dodaj_ksiazke':
      dodaj_ksiazke(session, args.autor, args.tytul, args.rok)
    elif args.command == 'dodaj_przyjaciela':
      dodaj_przyjaciela(session, args.imie, args.email)
    elif args.command == 'wypozycz_ksiazke':
      wypozycz_ksiazke(session, args.ksiazka_id, args.przyjaciel_id)
    elif args.command == 'oddaj_ksiazke':
      oddaj_ksiazke(session, args.ksiazka_id)
    elif args.command == 'lista_ksiazek':
      lista_ksiazek(session)
    elif args.command == 'lista_przyjaciol':
      lista_przyjaciol(session)
    else:
      parser.print_help()
    

main()