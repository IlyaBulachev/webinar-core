"""Сервисы бизнес-логики с использованием SQLite"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.repository import SQLiteRepository
from core.exceptions import (
    SeminarNotFoundError,
    InvalidSeminarDataError,
    SeminarFullError,
    ParticipantAlreadyRegisteredError
)


class SeminarService:
    """Сервис для управления семинарами"""

    def __init__(self, db_path: str = "seminars.db"):
        self.repository = SQLiteRepository(db_path)

    def get_all_seminars(self) -> List[Dict[str, Any]]:
        """Получить все семинары"""
        return self.repository.get_all_seminars()

    def get_upcoming_seminars(self) -> List[Dict[str, Any]]:
        """Получить предстоящие семинары"""
        all_seminars = self.repository.get_all_seminars()
        return [s for s in all_seminars if s.get('is_upcoming', False)]

    def get_seminar_by_id(self, seminar_id: int) -> Dict[str, Any]:
        """Получить семинар по ID"""
        seminar = self.repository.get_seminar_by_id(seminar_id)
        if not seminar:
            raise SeminarNotFoundError(seminar_id)
        return seminar

    def create_seminar(self, title: str, speaker: str, date: str,
                       max_participants: int = 50, description: str = "") -> Dict[str, Any]:
        """Создать новый семинар"""
        # Валидация
        if not title or len(title.strip()) < 3:
            raise InvalidSeminarDataError("Название семинара должно содержать минимум 3 символа")
        if not speaker or len(speaker.strip()) < 2:
            raise InvalidSeminarDataError("Имя спикера должно содержать минимум 2 символа")
        if max_participants < 1:
            raise InvalidSeminarDataError("Максимальное количество участников должно быть больше 0")

        # Проверка даты
        try:
            seminar_date = datetime.fromisoformat(date)
            if seminar_date < datetime.now():
                raise InvalidSeminarDataError("Дата семинара не может быть в прошлом")
        except ValueError:
            raise InvalidSeminarDataError("Некорректный формат даты. Используйте YYYY-MM-DD")

        seminar_data = {
            'title': title.strip(),
            'speaker': speaker.strip(),
            'date': date,
            'max_participants': max_participants,
            'description': description.strip()
        }

        return self.repository.add_seminar(seminar_data)

    def update_seminar(self, seminar_id: int, **kwargs) -> Dict[str, Any]:
        """Обновить данные семинара"""
        # Проверяем существование
        self.get_seminar_by_id(seminar_id)

        # Валидация
        if 'max_participants' in kwargs and kwargs['max_participants'] < 1:
            raise InvalidSeminarDataError("Максимальное количество участников должно быть больше 0")

        if 'date' in kwargs:
            try:
                seminar_date = datetime.fromisoformat(kwargs['date'])
                if seminar_date < datetime.now():
                    raise InvalidSeminarDataError("Дата семинара не может быть в прошлом")
            except ValueError:
                raise InvalidSeminarDataError("Некорректный формат даты. Используйте YYYY-MM-DD")

        return self.repository.update_seminar(seminar_id, kwargs)

    def delete_seminar(self, seminar_id: int) -> bool:
        """Удалить семинар"""
        return self.repository.delete_seminar(seminar_id)

    def register_participant(self, seminar_id: int, participant_name: str, email: str = None) -> Dict[str, Any]:
        """Зарегистрировать участника"""
        if not participant_name or len(participant_name.strip()) < 2:
            raise InvalidSeminarDataError("Имя участника должно содержать минимум 2 символа")

        return self.repository.add_participant(seminar_id, participant_name.strip(), email)

    def unregister_participant(self, seminar_id: int, participant_name: str) -> bool:
        """Отменить регистрацию"""
        return self.repository.remove_participant(seminar_id, participant_name)

    def get_participants(self, seminar_id: int) -> List[str]:
        """Получить список участников"""
        return self.repository.get_participants(seminar_id)

    def search_seminars(self, query: str) -> List[Dict[str, Any]]:
        """Поиск семинаров"""
        return self.repository.search_seminars(query)

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику"""
        return self.repository.get_statistics()