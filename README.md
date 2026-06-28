# Ядро системы «Онлайн система семинаров»

Дипломная работа по специальности 09.02.07 «Информационные системы и программирование».

## Описание

Программное ядро для проведения онлайн-семинаров в образовательных организациях. Реализовано на Python с использованием фреймворка Flask и базы данных SQLite.

## Технологии

- Язык: Python 3
- Фреймворк: Flask
- База данных: SQLite (файл seminars.db)
- ORM: SQLAlchemy
- Шаблоны: Jinja2
- Стили: CSS

## Структура проекта
├── app.py
├── requirements.txt
├── seminars.db
├── core/
│ ├── init.py
│ ├── models.py
│ ├── services.py
│ ├── repository.py
│ ├── database.py
│ └── exceptions.py
├── templates/
│ ├── index.html
│ ├── seminar.html
│ ├── add_seminar.html
│ └── edit_seminar.html
└── static/
└── style.css##
Установка и запуск

1. Клонировать репозиторий:
git clone https://github.com/IlyaBulachev/webinar-core.git
cd webinar-core
2. Установить зависимости:
pip install -r requirements.txt
3. Запустить приложение:
python app.py
4. Открыть в браузере: http://127.0.0.1:5000/

## Основные функции

- Просмотр списка семинаров
- Добавление нового семинара
- Редактирование семинара
- Удаление семинара

## Автор

Булачев Илья Александрович, 2026 г.