from flask import Response, make_response, request
from flask.typing import ResponseReturnValue
from flask import Flask, jsonify, request
from sqlalchemy import Column
from sqlalchemy.orm import sessionmaker, scoped_session
from operacje import create_engine_sqlalchemy, Ksiazka, Base, Uzytkownik
from functools import wraps

app = Flask(__name__)

engine = create_engine_sqlalchemy()
Base.metadata.create_all(engine)
SessionLocal = scoped_session(sessionmaker(bind=engine))

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if auth:
            with SessionLocal() as session:
                user = session.query(Uzytkownik).filter_by(
                login=auth.username, haslo=auth.password).first()
            if user:
                return f(*args, **kwargs)
        return make_response("<h1>Access denied</h1>", 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})
    return decorated_function

@app.route('/')
@auth_required
def home() -> str:
    """
    Endpoint dla strony głównej z logowaniem.
    Sprawdza dane użytkownika w tabeli Uzytkownicy.
    """
    # auth = request.authorization
    # if auth:
    #     with SessionLocal() as session:
    #         user = session.query(Uzytkownik).filter_by(
    #             login=auth.username, haslo=auth.password).first()
    #         if user:
    #             return "<h1>Przyjacielskie wypożyczenia książek!</h1>"
    return make_response("<h1>Access denied</h1>", 401, {'WWW-Authenticate': 'Basic realm="Login Required!"'})


@app.route('/ksiazki', methods=['GET'])
@auth_required
def get_all_ksiazki() -> ResponseReturnValue:
    """
    Endpoint do pobierania listy wszystkich książek.
    :return: Lista książek w formacie JSON.
    """
    with SessionLocal() as session:
        ksiazki = session.query(Ksiazka).all()
        ksiazki_list = [{
            "id": ksiazka.id,
            "autor": ksiazka.autor,
            "tytul": ksiazka.tytul,
            "rok_wydania": ksiazka.rok_wydania
        } for ksiazka in ksiazki]
        return jsonify(ksiazki_list), 200


@app.route('/ksiazka/<int:id>', methods=['GET'])
@auth_required
def get_ksiazka(id: int) -> ResponseReturnValue:
    """
    Endpoint do pobierania szczegółów konkretnej książki na podstawie jej ID.
    :param id: ID książki.
    :return: Szczegóły książki w formacie JSON lub komunikat o błędzie,
    jeśli książka nie istnieje.
    """
    with SessionLocal() as session:
        ksiazka = session.query(Ksiazka).filter_by(id=id).first()
        if ksiazka:
            return jsonify({
                "id": ksiazka.id,
                "autor": ksiazka.autor,
                "tytul": ksiazka.tytul,
                "rok_wydania": ksiazka.rok_wydania
            }), 200
        else:
            return jsonify({"message": "Ksiazka nie istnieje."}), 404


@app.route('/ksiazka/<int:id>', methods=['DELETE'])
def delete_ksiazka(id: int) -> ResponseReturnValue:
    """
    Endpoint do usuwania książki na podstawie jej ID.
    :param id: ID książki do usunięcia.
    :return: Status operacji w formacie JSON lub komunikat o błędzie,
    jeśli książka nie istnieje.
    """
    with SessionLocal() as session:
        ksiazka = session.query(Ksiazka).get(id)
        if ksiazka:
            session.delete(ksiazka)
            session.commit()
            print(f"Usunieto ksiazke: {ksiazka}")
            return jsonify({'message': 'OK'}), 204
        else:
            return jsonify({"message": "Ksiazka nie istnieje."}), 404


@app.route('/ksiazka/<string:autor>/<string:tytul>/<int:rok_wydania>',
           methods=['POST'])
def dodaj_ksiazke(
        autor: Column[str],
        tytul: Column[str],
        rok_wydania: Column[int]) -> ResponseReturnValue:
    """
    Endpoint do dodawania nowej książki.
    :param autor: Autor książki.
    :param tytul: Tytuł książki.
    :param rok_wydania: Rok wydania książki.
    :return: Status operacji w formacie JSON.
    """
    with SessionLocal() as session:
        ksiazka = Ksiazka(autor=autor, tytul=tytul, rok_wydania=rok_wydania)
        session.add(ksiazka)
        session.commit()
        print(f"Dodano ksiazke: {ksiazka}")
        return jsonify({'message': 'OK'}), 204


@app.route('/ksiazka/<int:id>', methods=['PUT'])
def update_ksiazka(id: int) -> ResponseReturnValue:
    """
    Endpoint do aktualizowania szczegółów istniejącej książki.
    :param id: ID książki do zaktualizowania.
    :return: Status operacji w formacie JSON lub komunikat o błędzie,
    jeśli książka nie istnieje.
    """
    with SessionLocal() as session:
        ksiazka = session.query(Ksiazka).get(id)
        if ksiazka:
            if request.json is not None:
                data = request.json
                autor = data.get('autor', ksiazka.autor)
                tytul = data.get('tytul', ksiazka.tytul)
                rok_wydania = data.get('rok_wydania', ksiazka.rok_wydania) 
                ksiazka.autor = autor
                ksiazka.tytul = tytul
                ksiazka.rok_wydania = rok_wydania
                session.commit()
                print(f"Zaktualizowano ksiazke: {ksiazka}")
                return jsonify({'message': 'OK'}), 204
            else:
                return jsonify(
                    {'message': 'Brak danych do aktualizacji.'}), 400
        else:
            return jsonify({"message": "Ksiazka nie istnieje."}), 404


if __name__ == "__main__":
    """
    Uruchamia aplikację Flask na domyślnym porcie 5000.
    """
    app.run()
