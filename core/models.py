"""Модели данных системы семинаров"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Participant:
    """Модель участника"""
    id: Optional[int] = None
    name: str = ""
    email: Optional[str] = None
    seminar_id: Optional[int] = None
    registered_at: Optional[datetime] = None

    def __post_init__(self):
        if self.name and len(self.name.strip()) < 2:
            raise ValueError("Имя участника должно содержать минимум 2 символа")
        if self.name:
            self.name = self.name.strip()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "seminar_id": self.seminar_id,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None
        }


@dataclass
class Seminar:
    """Модель семинара"""
    id: Optional[int] = None
    title: str = ""
    speaker: str = ""
    date: Optional[datetime] = None
    max_participants: int = 50
    description: str = ""
    created_at: Optional[datetime] = None
    participants: List[Participant] = field(default_factory=list)

    def __post_init__(self):
        if self.title and len(self.title.strip()) < 3:
            raise ValueError("Название семинара должно содержать минимум 3 символа")
        if self.speaker and len(self.speaker.strip()) < 2:
            raise ValueError("Имя спикера должно содержать минимум 2 символа")

        if self.title:
            self.title = self.title.strip()
        if self.speaker:
            self.speaker = self.speaker.strip()

    @property
    def is_full(self) -> bool:
        return len(self.participants) >= self.max_participants

    @property
    def participants_count(self) -> int:
        return len(self.participants)

    @property
    def is_upcoming(self) -> bool:
        if not self.date:
            return False
        return self.date > datetime.now()

    def to_dict(self, include_participants: bool = True) -> dict:
        result = {
            "id": self.id,
            "title": self.title,
            "speaker": self.speaker,
            "date": self.date.isoformat() if self.date else None,
            "max_participants": self.max_participants,
            "description": self.description,
            "participants_count": self.participants_count,
            "is_full": self.is_full,
            "is_upcoming": self.is_upcoming,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

        if include_participants:
            result["participants"] = [p.to_dict() for p in self.participants]

        return result