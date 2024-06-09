from django.test import TestCase

from squads.forms import SquadsGroupForm


class SquadsGroupFormTest(TestCase):
    def test_clean_description_too_long(self):
        # Erstellen Sie Formulardaten mit einer Beschreibung, die länger als 1000 Zeichen ist
        form_data = {
            "name": "Test Group",
            "description": "a" * 1001,  # 1001 Zeichen lange Beschreibung
            "require_approval": False,
        }
        form = SquadsGroupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)
        self.assertEqual(
            form.errors["description"][0],
            "The Description is too long. Please keep it under 1000 characters.",
        )

    def test_clean_description_valid(self):
        # Erstellen Sie Formulardaten mit einer gültigen Beschreibung
        form_data = {
            "name": "Test Group",
            "description": "<p>This is a valid description.</p>",
            "require_approval": False,
        }
        form = SquadsGroupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_description_invalid_tags(self):
        form_data = {
            "name": "Test Group",
            "description": '<script>alert("Hack!");</script><p>This is a valid part of the description.</p>',
            "require_approval": False,
        }
        form = SquadsGroupForm(data=form_data)
        self.assertTrue(form.is_valid())
        cleaned_description = form.cleaned_data["description"]
        self.assertNotIn("<script>", cleaned_description)
        self.assertIn(
            "<p>This is a valid part of the description.</p>", cleaned_description
        )
