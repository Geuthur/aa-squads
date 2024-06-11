"""Forms for the Squads app."""

import bleach
from bleach.css_sanitizer import CSSSanitizer

from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

from .models import Groups


class CustomClearableFileInput(ClearableFileInput):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value and hasattr(value, "url"):
            context["widget"]["is_initial"] = False
        return context


class SquadsGroupForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = ["name", "description", "require_approval", "image"]
        widgets = {
            "image": CustomClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "maxlength": "26", "required": True}
        )
        self.fields["description"].widget.attrs.update({"class": "form-control"})
        self.fields["description"].max_length = 1000
        self.fields["require_approval"].widget.attrs.update(
            {"class": "form-check-input"}
        )
        if self.instance.pk:
            self.fields["is_active"] = forms.BooleanField(
                required=False, label="Is Active", initial=self.instance.is_active
            )
            self.fields["is_active"].widget.attrs.update({"class": "form-check-input"})

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and len(name) > 26:
            raise ValidationError("The name must be at most 26 characters long.")
        return name

    # Prvent Security Issues
    def clean_description(self):
        allowed_tags = [
            "p",
            "b",
            "i",
            "u",
            "a",
            "ul",
            "ol",
            "li",
            "br",
            "img",
            "strong",
            "em",
            "iframe",
            "div",
            "blockquote",
            "span",
        ]
        allowed_attrs = {
            "a": ["href", "title", "style"],
            "img": ["src", "alt", "style"],
            "iframe": ["src", "allowfullscreen", "width", "height", "style"],
            "p": ["style"],
            "div": ["style"],
            "span": ["style"],
        }

        allowed_styles = [
            "color",
            "font-family",
            "font-size",
            "font-style",
            "font-weight",
            "text-align",
            "text-decoration",
            "text-indent",
            "background-color",
            "background-image",
            "background-repeat",
            "background-size",
            "border",
            "border-bottom",
            "border-left",
            "border-radius",
            "border-right",
            "border-top",
            "margin",
            "margin-bottom",
            "margin-left",
            "margin-right",
            "margin-top",
            "padding",
            "padding-bottom",
            "padding-left",
            "padding-right",
            "padding-top",
            "line-height",
            "letter-spacing",
            "word-spacing",
            "width",
            "height",
            "max-width",
            "max-height",
            "min-width",
        ]

        css_santizer = CSSSanitizer(allowed_css_properties=allowed_styles)

        cleaned_data = bleach.clean(
            self.cleaned_data["description"],
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True,
            css_sanitizer=css_santizer,
        )

        if len(cleaned_data) > 1000:
            raise ValidationError(
                "The Description is too long. Please keep it under 1000 characters."
            )

        return cleaned_data

    def clean_image(self):
        try:
            image = self.cleaned_data.get("image")
            if image:
                max_size = 2 * 1024 * 1024  # 2 MB
                if image.size > max_size:
                    raise ValidationError(
                        _(
                            "The image file is too large ( > 2 MB ). Please choose a smaller file."
                        )
                    )
        # TODO Fix this in correct way
        # Bad Fix but works for now
        except FileNotFoundError:
            return None
        return image


class CommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "rows": 1,
                "maxlength": 200,
                "placeholder": "comment...",
            }
        ),
        required=False,
    )
