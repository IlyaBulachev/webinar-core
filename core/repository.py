"""Репозиторий для работы с SQLite"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.database import Database
from core.models import Seminar, Participant
from core.exceptions import (
    SeminarNotFoundError,
    ParticipantAlreadyRegisteredError,
    SeminarFullError,
    DatabaseError
)


class SQLiteRepository:
    """Репозиторий с использованием SQLite"""

    def __init__(self, db_path: str = "seminars.db"):
        self.db = Database(db_path)

    def _row_to_seminar(self, row: Dict[str, Any], participants: List[Participant] = None) -> Seminar:
        """Преобразовать строку БД в объект Seminar"""
        return Seminar(
            id=row['id'],
            title=row['title'],
            speaker=row['speaker'],
            date=datetime.fromisoformat(row['date']) if row['date'] else None,
            max_participants=row['max_participants'],
            description=row['description'] or "",
            created_at=datetime.fromisoformat(row['created_at']) if row.get('created_at') else None,
            participants=participants or []
        )

    def _row_to_participant(self, row: Dict[str, Any]) -> Participant:
        """Преобразовать строку БД в объект Participant"""
        return Participant(
            id=row['id'],
            name=row['name'],
            email=row.get('email'),
            seminar_id=row['seminar_id'],
            registered_at=datetime.fromisoformat(row['registered_at']) if row.get('registered_at') else None
        )

    def get_all_seminars(self) -> List[Dict[str, Any]]:
        """Получить все семинары"""
        try:
            rows = self.db.execute_query("""
                SELECT s.*, 
                       COUNT(p.id) as participants_count
                FROM seminars s
                LEFT JOIN participants p ON s.id = p.seminar_id
                GROUP BY s.id
                ORDER BY s.date DESC
            """)

            result = []
            for row in rows:
                seminar = self._row_to_seminar(row)
                # Добавляем количество участников напрямую
                seminar_dict = seminar.to_dict(include_participants=False)
                seminar_dict['participants_count'] = row['participants_count'] or 0
                result.append(seminar_dict)

            return result
        except Exception as e:
            raise DatabaseError(f"Ошибка получения семинаров: {str(e)}")

    def get_seminar_by_id(self, seminar_id: int) -> Optional[Dict[str, Any]]:
        """Получить семинар по ID с участниками"""
        try:
            # Получаем семинар
            rows = self.db.execute_query(
                "SELECT * FROM seminars WHERE id = ?",
                (seminar_id,)
            )

            if not rows:
                return None

            # Получаем участников
            participant_rows = self.db.execute_query(
                "SELECT * FROM participants WHERE seminar_id = ? ORDER BY registered_at",
                (seminar_id,)
            )

            participants = [self._row_to_participant(row) for row in participant_rows]

            seminar = self._row_to_seminar(rows[0], participants)
            return seminar.to_dict(include_participants=True)

        except Exception as e:
            raise DatabaseError(f"Ошибка получения семинара: {str(e)}")

    def add_seminar(self, seminar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Добавить новый семинар"""
        try:
            query = """
                INSERT INTO seminars (title, speaker, date, max_participants, description)
                VALUES (?, ?, ?, ?, ?)
            """

            seminar_id = self.db.execute_insert(
                query,
                (
                    seminar_data['title'],
                    seminar_data['speaker'],
                    seminar_data['date'],
                    seminar_data.get('max_participants', 50),
                    seminar_data.get('description', '')
                )
            )

            return self.get_seminar_by_id(seminar_id)

        except Exception as e:
            raise DatabaseError(f"Ошибка добавления семинара: {str(e)}")

    def update_seminar(self, seminar_id: int, seminar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить данные семинара"""
        try:
            # Проверяем существование
            if not self.db.execute_query("SELECT id FROM seminars WHERE id = ?", (seminar_id,)):
                raise SeminarNotFoundError(seminar_id)

            # Собираем поля для обновления
            update_fields = []
            params = []

            if 'title' in seminar_data:
                update_fields.append("title = ?")
                params.append(seminar_data['title'])
            if 'speaker' in seminar_data:
                update_fields.append("speaker = ?")
                params.append(seminar_data['speaker'])
            if 'date' in seminar_data:
                update_fields.append("date = ?")
                params.append(seminar_data['date'])
            if 'max_participants' in seminar_data:
                update_fields.append("max_participants = ?")
                params.append(seminar_data['max_participants'])
            if 'description' in seminar_data:
                update_fields.append("description = ?")
                params.append(seminar_data['description'])

            if update_fields:
                params.append(seminar_id)
                query = f"UPDATE seminars SET {', '.join(update_fields)} WHERE id = ?"
                self.db.execute_update(query, tuple(params))

            return self.get_seminar_by_id(seminar_id)

        except Exception as e:
            raise DatabaseError(f"Ошибка обновления семинара: {str(e)}")

    def delete_seminar(self, seminar_id: int) -> bool:
        """Удалить семинар (участники удалятся каскадно)"""
        try:
            rows_affected = self.db.execute_delete(
                "DELETE FROM seminars WHERE id = ?",
                (seminar_id,)
            )
            return rows_affected > 0
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления семинара: {str(e)}")

    def add_participant(self, seminar_id: int, participant_name: str, email: str = None) -> Dict[str, Any]:
        """Добавить участника на семинар"""
        try:
            # Проверяем существование семинара и количество участников
            seminar_row = self.db.execute_query(
                """SELECT s.*, COUNT(p.id) as current_participants 
                   FROM seminars s
                   LEFT JOIN participants p ON s.id = p.seminar_id
                   WHERE s.id = ?
                   GROUP BY s.id""",
                (seminar_id,)
            )

            if not seminar_row:
                raise SeminarNotFoundError(seminar_id)

            seminar_data = seminar_row[0]
            current_count = seminar_data['current_participants'] or 0
            max_participants = seminar_data['max_participants']

            if current_count >= max_participants:
                raise SeminarFullError(seminar_id, max_participants)

            # Добавляем участника
            try:
                query = """
                    INSERT INTO participants (seminar_id, name, email)
                    VALUES (?, ?, ?)
                """
                self.db.execute_insert(
                    query,
                    (seminar_id, participant_name.strip(), email)
                )
            except sqlite3.IntegrityError:
                raise ParticipantAlreadyRegisteredError(seminar_id, participant_name)

            return self.get_seminar_by_id(seminar_id)

        except Exception as e:
            if isinstance(e, (SeminarNotFoundError, SeminarFullError, ParticipantAlreadyRegisteredError)):
                raise
            raise DatabaseError(f"Ошибка добавления участника: {str(e)}")

    def remove_participant(self, seminar_id: int, participant_name: str) -> bool:
        """Удалить участника с семинара"""
        try:
            rows_affected = self.db.execute_delete(
                "DELETE FROM participants WHERE seminar_id = ? AND name = ?",
                (seminar_id, participant_name.strip())
            )
            return rows_affected > 0
        except Exception as e:
            raise DatabaseError(f"Ошибка удаления участника: {str(e)}")

    def get_participants(self, seminar_id: int) -> List[str]:
        """Получить список участников семинара"""
        try:
            rows = self.db.execute_query(
                "SELECT name FROM participants WHERE seminar_id = ? ORDER BY registered_at",
                (seminar_id,)
            )
            return [row['name'] for row in rows]
        except Exception as e:
            raise DatabaseError(f"Ошибка получения участников: {str(e)}")

    def search_seminars(self, query: str) -> List[Dict[str, Any]]:
        """Поиск семинаров"""
        try:
            search_pattern = f"%{query}%"
            rows = self.db.execute_query("""
                SELECT s.*, COUNT(p.id) as participants_count
                FROM seminars s
                LEFT JOIN participants p ON s.id = p.seminar_id
                WHERE s.title LIKE ? OR s.speaker LIKE ? OR s.description LIKE ?
                GROUP BY s.id
                ORDER BY s.date DESC
            """, (search_pattern, search_pattern, search_pattern))

            result = []
            for row in rows:
                seminar = self._row_to_seminar(row)
                seminar_dict = seminar.to_dict(include_participants=False)
                seminar_dict['participants_count'] = row['participants_count'] or 0
                result.append(seminar_dict)

            return result

        except Exception as e:
            raise DatabaseError(f"Ошибка поиска: {str(e)}")

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        try:
            stats = self.db.execute_query("""
                SELECT 
                    COUNT(DISTINCT s.id) as total_seminars,
                    COUNT(p.id) as total_participants,
                    SUM(CASE WHEN s.date > datetime('now') THEN 1 ELSE 0 END) as upcoming_seminars,
                    SUM(CASE WHEN (SELECT COUNT(*) FROM participants WHERE seminar_id = s.id) >= s.max_participants THEN 1 ELSE 0 END) as full_seminars,
                    AVG((SELECT COUNT(*) FROM participants WHERE seminar_id = s.id)) as avg_participants
                FROM seminars s
                LEFT JOIN participants p ON s.id = p.seminar_id
            """)

            if stats:
                stat = stats[0]
                return {
                    'total_seminars': stat['total_seminars'] or 0,
                    'total_participants': stat['total_participants'] or 0,
                    'upcoming_seminars': stat['upcoming_seminars'] or 0,
                    'full_seminars': stat['full_seminars'] or 0,
                    'average_participants': round(stat['avg_participants'] or 0, 1)
                }

            return {
                'total_seminars': 0,
                'total_participants': 0,
                'upcoming_seminars': 0,
                'full_seminars': 0,
                'average_participants': 0
            }

        except Exception as e:
            raise DatabaseError(f"Ошибка получения статистики: {str(e)}")


# Импортируем sqlite3 для обработки ошибок
import sqlite3