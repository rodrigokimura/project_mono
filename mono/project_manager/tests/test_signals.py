from unittest.mock import MagicMock, patch

from __mono.decorators import ignore_warnings
from django.test import TestCase

from ..signals import delete_background_image, delete_card_file


class FakeImage:
    def __init__(self):
        self.path = "path"


class FakeBucket:
    def touch(self) -> None:
        pass


class FakeObject:
    def __init__(self) -> None:
        background_image = FakeImage()
        self.id = 1
        self.background_image = background_image
        self.bucket = FakeBucket()


class FakeCardFile:
    def __init__(self) -> None:
        file = FakeImage()
        self.id = 1
        self.file = file
        self.card = FakeObject()


class SignalsTest(TestCase):
    @patch("os.path.isfile")
    @patch("os.remove")
    def test_delete_background_image(
        self, mock_remove: MagicMock, mock_isfile: MagicMock
    ):
        mock_isfile.return_value = True
        mock_remove.return_value = True
        delete_background_image(None, FakeObject(), None)
        mock_remove.assert_called_once_with("path")

    @ignore_warnings
    @patch("os.path.isfile")
    @patch("os.remove")
    def test_delete_card_file(
        self, mock_remove: MagicMock, mock_isfile: MagicMock
    ):
        mock_isfile.return_value = True
        mock_remove.side_effect = ValueError("test")
        delete_card_file(None, FakeCardFile(), None)
        mock_remove.assert_called_once_with("path")
