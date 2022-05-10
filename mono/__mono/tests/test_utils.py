import pytest
from __mono.utils import validate_file_size
from django.core.exceptions import ValidationError


class TestUtils:

    class FakeFile:
        size: int

        def __init__(self, size):
            self.size = size

    def test_validate_file_size_should_succeed(self):
        file = self.FakeFile(10 * 1024 * 1024)
        assert validate_file_size(file, 10) == file

    def test_validate_file_size_should_fail(self):
        file = self.FakeFile(10 * 1024 * 1024)
        with pytest.raises(ValidationError):
            validate_file_size(file, 9)
