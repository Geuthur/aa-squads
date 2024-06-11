from unittest import TestCase
from unittest.mock import MagicMock

from django.core.exceptions import ValidationError

from app_utils.testing import create_user_from_evecharacter

from squads.forms import SquadsGroupForm
from squads.models import Groups
from squads.tests.testdata.load_allianceauth import load_allianceauth


class TestCleanImage(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        load_allianceauth()
        cls.user, cls.character_ownership = create_user_from_evecharacter(
            1001,
            permissions=[
                "squads.basic_access",
            ],
        )
        cls.form = SquadsGroupForm()
        cls.group = Groups(
            owner=cls.user,
            name="Test Group",
            description="Test Description",
            req_approve=True,
        )
        cls.group.save()
        cls.form = SquadsGroupForm(instance=cls.group)

    def test_init_with_instance_pk(self):
        self.assertIn("is_active", self.form.fields)
        self.assertFalse(self.form.fields["is_active"].required)
        self.assertEqual(self.form.fields["is_active"].initial, self.group.is_active)
        self.assertEqual(
            self.form.fields["is_active"].widget.attrs, {"class": "form-check-input"}
        )

    def test_clean_image_valid_size(self):
        # Mock image with size less than 2 MB
        image_mock = MagicMock()
        image_mock.size = 1 * 1024 * 1024  # 1 MB

        self.form.cleaned_data = {"image": image_mock}

        try:
            result = self.form.clean_image()
            self.assertEqual(result, image_mock)
        except ValidationError:
            self.fail("clean_image() raised ValidationError unexpectedly!")

    def test_clean_image_too_large(self):
        # Mock image with size greater than 2 MB
        image_mock = MagicMock()
        image_mock.size = 3 * 1024 * 1024  # 3 MB

        self.form.cleaned_data = {"image": image_mock}

        with self.assertRaises(ValidationError):
            self.form.clean_image()

    def test_clean_image_no_image(self):
        self.form.cleaned_data = {"image": None}

        result = self.form.clean_image()
        self.assertIsNone(result)
