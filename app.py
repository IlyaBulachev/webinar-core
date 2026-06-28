"""Веб-приложение с использованием ядра и SQLite"""
from flask import Flask, render_template, request, redirect, url_for, jsonify
from core import SeminarService, SeminarNotFoundError, InvalidSeminarDataError, SeminarFullError, \
    ParticipantAlreadyRegisteredError
import socket
import os

app = Flask(__name__)

# Инициализация сервиса с SQLite
db_path = os.path.join(os.path.dirname(__file__), 'seminars.db')
seminar_service = SeminarService(db_path)


@app.route('/')
def index():
    """Главная страница"""
    seminars = seminar_service.get_all_seminars()
    statistics = seminar_service.get_statistics()
    return render_template('index.html', seminars=seminars, statistics=statistics)


@app.route('/seminar/<int:seminar_id>')
def seminar_detail(seminar_id):
    """Страница семинара"""
    try:
        seminar = seminar_service.get_seminar_by_id(seminar_id)
        return render_template('seminar.html', seminar=seminar)
    except SeminarNotFoundError:
        return "Семинар не найден", 404


@app.route('/register/<int:seminar_id>', methods=['POST'])
def register(seminar_id):
    """Регистрация участника"""
    participant_name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()

    try:
        seminar_service.register_participant(seminar_id, participant_name, email or None)
        return redirect(url_for('seminar_detail', seminar_id=seminar_id))
    except SeminarNotFoundError:
        return "Семинар не найден", 404
    except ParticipantAlreadyRegisteredError as e:
        return f"Ошибка: {str(e)}", 400
    except SeminarFullError as e:
        return f"Ошибка: {str(e)}", 400
    except InvalidSeminarDataError as e:
        return f"Ошибка: {str(e)}", 400


@app.route('/unregister/<int:seminar_id>', methods=['POST'])
def unregister(seminar_id):
    """Отмена регистрации"""
    participant_name = request.form.get('name', '').strip()

    try:
        seminar_service.unregister_participant(seminar_id, participant_name)
        return redirect(url_for('seminar_detail', seminar_id=seminar_id))
    except SeminarNotFoundError:
        return "Семинар не найден", 404


@app.route('/add_seminar', methods=['GET', 'POST'])
def add_seminar():
    """Добавление семинара"""
    if request.method == 'POST':
        try:
            seminar_service.create_seminar(
                title=request.form['title'],
                speaker=request.form['speaker'],
                date=request.form['date'],
                max_participants=int(request.form.get('max_participants', 50)),
                description=request.form.get('description', '')
            )
            return redirect(url_for('index'))
        except InvalidSeminarDataError as e:
            return render_template('add_seminar.html', error=str(e))

    return render_template('add_seminar.html')


@app.route('/edit_seminar/<int:seminar_id>', methods=['GET', 'POST'])
def edit_seminar(seminar_id):
    """Редактирование семинара"""
    try:
        if request.method == 'POST':
            seminar_service.update_seminar(
                seminar_id,
                title=request.form['title'],
                speaker=request.form['speaker'],
                date=request.form['date'],
                max_participants=int(request.form.get('max_participants', 50)),
                description=request.form.get('description', '')
            )
            return redirect(url_for('seminar_detail', seminar_id=seminar_id))

        seminar = seminar_service.get_seminar_by_id(seminar_id)
        return render_template('edit_seminar.html', seminar=seminar)
    except SeminarNotFoundError:
        return "Семинар не найден", 404
    except InvalidSeminarDataError as e:
        seminar = seminar_service.get_seminar_by_id(seminar_id)
        return render_template('edit_seminar.html', seminar=seminar, error=str(e))


@app.route('/delete_seminar/<int:seminar_id>', methods=['POST'])
def delete_seminar(seminar_id):
    """Удаление семинара"""
    try:
        seminar_service.delete_seminar(seminar_id)
        return redirect(url_for('index'))
    except SeminarNotFoundError:
        return "Семинар не найден", 404


# API endpoints
@app.route('/api/seminars')
def api_seminars():
    return jsonify(seminar_service.get_all_seminars())


@app.route('/api/seminar/<int:seminar_id>')
def api_seminar(seminar_id):
    try:
        return jsonify(seminar_service.get_seminar_by_id(seminar_id))
    except SeminarNotFoundError:
        return jsonify({'error': 'Seminar not found'}), 404


@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    return jsonify(seminar_service.search_seminars(query))


@app.route('/api/statistics')
def api_statistics():
    return jsonify(seminar_service.get_statistics())


def find_free_port(start_port=5000):
    """Поиск свободного порта"""
    port = start_port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            port += 1


if __name__ == '__main__':
    port = find_free_port()
    print(f"🚀 Запуск сервера на http://127.0.0.1:{port}")
    print(f"📊 API: http://127.0.0.1:{port}/api/seminars")
    print(f"📁 База данных: {db_path}")
    app.run(debug=True, host='0.0.0.0', port=port)