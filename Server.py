from flask import Flask, jsonify, request
from flask import send_from_directory
from flask_cors import CORS, cross_origin
import psycopg2
import datetime

app = Flask(__name__)
cors = CORS(app)

database = psycopg2.connect(database='library', user='postgres', password=' ', host='127.0.0.1', port=5432)
database_cursor = database.cursor()


@app.route('/hack', methods=['GET'])
def cafe():
    print(request.args)
    headers = {'content-type': 'application/json'}
    return jsonify("Wow you are hacker!")


@app.route('/authentication', methods=['POST'])
def authentication():
    try:
        app.config['CORS_HEADERS'] = 'Content-Type'
        app.config['Access-Control-Allow-Origin'] = '*'
        app.config['Access-Control-Allow-Credentials'] = 'true'
        print(request.get_json())
        data = request.get_json()
        database_cursor.execute(f"select name, readerid from client "
                                f"where login = '{data['login']}' and password = '{data['password']}'")
        user_info = []
        for row in database_cursor:
            print(row)
            user_info.append(row)
        return_answer = {'answer': 'success',
                         'name': str(user_info[0][0]).strip(),
                         'readerid': str(user_info[0][1]).strip()}
        return jsonify(return_answer)
    except IndexError:
        return_answer = {'answer': 'fail'}
        return jsonify(return_answer)


@app.route('/registration', methods=['POST'])
def registration():
    try:
        app.config['CORS_HEADERS'] = 'Content-Type'
        app.config['Access-Control-Allow-Origin'] = '*'
        app.config['Access-Control-Allow-Credentials'] = 'true'
        print(request.get_json())
        data = request.get_json()
        database_cursor.execute(f"select login from client where login = '{data['login']}'")
        for row in database_cursor:
            if row is not None:
                return jsonify({'answer': 'login is already used'})
        database_cursor.execute(f"select max(id) from readers")
        new_id = 0
        for row in database_cursor:
            new_id = 0 if row[0] is None else int(row[0]) + 1
        database_cursor.execute(
            f"insert into readers values ({new_id},{data['dateofbirth']},{data['address']})")
        database.commit()
        return_answer = {'answer': 'success'}
        return jsonify(return_answer)
    except SyntaxError:
        return_answer = {'answer': 'fail'}
        return jsonify(return_answer)


@app.route('/recomendation', methods=['POST'])
def recomendation():
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config['Access-Control-Allow-Origin'] = '*'
    app.config['Access-Control-Allow-Credentials'] = 'true'
    data = request.get_json()
    print(data)
    database_cursor.execute(f"select readerId, bookId,"
                            f" rubric_id from history inner join book on book.id "
                            f"= history.bookId where readerId = {data['UserId']};")
    history = []
    rubrics = []
    for row in database_cursor:
        history.append(row[1])
        rubrics.append(row[2])
    freq_map = {rubrics.count(val): val for val in set(rubrics)}
    best_rub = freq_map[max(freq_map.keys())]
    database_cursor.execute(f"select book.id, popularity, title, author from book inner join history on book.id"
                            f" = history.bookId where rubric_id = '{best_rub}' group by popularity, book.id "
                            f"order by popularity desc")
    answer = []
    for row in database_cursor:
        if row[0] not in history and len(answer) < 5:
            answer.append({"book_id": row[0], "title": row[2], "author": row[3]})
    return jsonify(answer)


if __name__ == "__main__":
    app.run(debug=True)
