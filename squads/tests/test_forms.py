from unittest import TestCase
from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.db.models.fields.files import ImageField, ImageFieldFile

from app_utils.testing import create_user_from_evecharacter

from squads.forms import CustomClearableFileInput, SquadsGroupForm
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

    def test_form_image_valid_size(self):
        image_mock = MagicMock()
        image_mock.size = 1 * 1024 * 1024

        self.form.cleaned_data = {"image": image_mock}

        result = self.form.clean_image()
        self.assertEqual(result, image_mock)

    def test_form_image_too_large(self):
        image_mock = MagicMock()
        image_mock.size = 3 * 1024 * 1024

        self.form.cleaned_data = {"image": image_mock}

        with self.assertRaises(ValidationError):
            self.form.clean_image()

    def test_form_no_image(self):
        self.form.cleaned_data = {"image": None}

        result = self.form.clean_image()
        self.assertIsNone(result)

    def test_form_image_not_found(self):
        image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x64\x00\x00\x00\x64\x08\x06\x00\x00\x00\x70\xe2\x95n\x00\x00\x00\x0bIDATx\x9cc```\xf8\xff\xff?\x03\x00\x18\x0d\x04\x04Q\xd4\xe8v\x00\x00\x00\x00IEND\xaeB`\x82"
        uploaded_image = SimpleUploadedFile(
            name="test_image.png", content=image_content, content_type="image/png"
        )

        image_field = ImageField()

        image_field_file = ImageFieldFile(
            instance=None, field=image_field, name=uploaded_image.name
        )
        image_field_file.file = uploaded_image

        self.form.cleaned_data = {"image": image_field_file}
        result = self.form.clean_image()
        self.assertIsNone(result)

    def test_form_text_to_long(self):
        self.form.cleaned_data = {"name": "a" * 27}
        with self.assertRaises(ValidationError):
            self.form.clean_name()


class CustomClearableFileInputTest(TestCase):
    def test_is_initial_set_to_false_if_value_has_url(self):
        widget = CustomClearableFileInput()
        value = MagicMock(url="http://example.com/image.png")
        context = widget.get_context("image", value, {})
        self.assertFalse(context["widget"]["is_initial"])

    def test_is_initial_true_or_not_set_if_value_has_no_url(self):
        widget = CustomClearableFileInput()
        value = MagicMock(spec=[])
        context = widget.get_context("image", value, {})
        is_initial = context["widget"].get("is_initial", False)
        self.assertFalse(is_initial)
