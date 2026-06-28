"""Модуль для работы с базой данных SQLite"""
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class Database:
    """Класс для управления подключением к SQLite"""

    def __init__(self, db_path: str = "seminars.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Создание таблиц, если их нет"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Таблица семинаров
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS seminars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    speaker TEXT NOT NULL,
                    date TEXT NOT NULL,
                    max_participants INTEGER DEFAULT 50,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Таблица участников
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seminar_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (seminar_id) REFERENCES seminars (id) ON DELETE CASCADE,
                    UNIQUE(seminar_id, name)
                )
            """)

            # Индексы для производительности
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_seminar_date ON seminars(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_participant_seminar ON participants(seminar_id)")

            conn.commit()

    def get_connection(self):
        """Получить соединение с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Возвращает строки как словари
        return conn

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Выполнить запрос и вернуть результаты"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Выполнить INSERT и вернуть ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Выполнить UPDATE и вернуть количество измененных строк"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """Выполнить DELETE и вернуть количество удаленных строк"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_many(self, query: str, params_list: List[tuple]):
        """Выполнить массовую вставку"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()