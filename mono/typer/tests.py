import pytest

from .models import KeyPress, Lesson, Record


class TestModels:
    def test_key_press(self, db, user):
        lesson = Lesson.objects.create(
            name="Test", text="Test", created_by=user
        )
        record = Record.objects.create(
            lesson=lesson,
            number=1,
            accuracy=0.0,
            chars_per_minute=0.0,
            created_by=user,
        )
        key_press = KeyPress.objects.create(
            record=record, character="a", milliseconds=0
        )
        assert key_press.character == "a"
        assert str(key_press) == "a"


class TestViews:
    def test_get_lessons(self, client, user):
        response = client.get("/lessons/")
        assert response.status_code == 200
