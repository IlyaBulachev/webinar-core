"""Собственные исключения для системы семинаров"""

class SeminarError(Exception):
    """Базовое исключение"""
    pass

class SeminarNotFoundError(SeminarError):
    """Семинар не найден"""
    def __init__(self, seminar_id: int):
        self.seminar_id = seminar_id
        super().__init__(f"Семинар с ID {seminar_id} не найден")

class ParticipantAlreadyRegisteredError(SeminarError):
    """Участник уже зарегистрирован"""
    def __init__(self, seminar_id: int, participant_name: str):
        self.seminar_id = seminar_id
        self.participant_name = participant_name
        super().__init__(f"Участник '{participant_name}' уже зарегистрирован на семинар {seminar_id}")

class SeminarFullError(SeminarError):
    """Семинар заполнен"""
    def __init__(self, seminar_id: int, max_participants: int):
        self.seminar_id = seminar_id
        self.max_participants = max_participants
        super().__init__(f"Семинар {seminar_id} заполнен (максимум {max_participants} участников)")

class InvalidSeminarDataError(SeminarError):
    """Некорректные данные"""
    pass

class DatabaseError(SeminarError):
    """Ошибка базы данных"""
    pass