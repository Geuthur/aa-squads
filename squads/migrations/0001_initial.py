# Generated by Django 4.2.11 on 2024-06-10 19:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import squads.view_helpers.core


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("memberaudit", "0018_charactercloneinfo"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("eveuniverse", "0010_alter_eveindustryactivityduration_eve_type_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="General",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "permissions": (
                    ("basic_access", "Can access this app, Squads."),
                    ("squad_manager", "Can Create / Manage Squads."),
                    ("squad_admin", "Can View All Squads."),
                ),
                "managed": False,
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Groups",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("require_approval", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "image",
                    models.ImageField(
                        blank=True, null=True, upload_to="squads/groups_images/"
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="group_owner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="SquadFilter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object_id", models.PositiveIntegerField(editable=False)),
                (
                    "content_type",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Squad Filter",
            },
        ),
        migrations.CreateModel(
            name="SquadGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, default="", max_length=500),
                ),
                ("enabled", models.BooleanField(default=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("filters", models.ManyToManyField(to="squads.squadfilter")),
                (
                    "group",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="squads.groups"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SkillSetFilter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "description",
                    models.CharField(help_text="Filter Name.", max_length=500),
                ),
                (
                    "skill_sets",
                    models.ManyToManyField(
                        help_text="Users must possess the selected skill sets with at least <strong>one</strong> character.",
                        related_name="squads_skill_sets",
                        to="memberaudit.skillset",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ShipFilter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "description",
                    models.CharField(help_text="Filter Name.", max_length=500),
                ),
                (
                    "ship",
                    models.ManyToManyField(
                        help_text="Users must have at least <strong>one</strong> of the selected Ship Type with <strong>one</strong> character.",
                        to="eveuniverse.evegroup",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Pending",
            fields=[
                ("approved", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("application", models.TextField(blank=True)),
                (
                    "application_id",
                    models.CharField(
                        default=squads.view_helpers.core.generate_unique_id,
                        editable=False,
                        max_length=12,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="squads.groups"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="Memberships",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("has_required_skills", models.BooleanField(default=False)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                (
                    "application_id",
                    models.CharField(
                        blank=True,
                        default=squads.view_helpers.core.generate_unique_id,
                        max_length=12,
                        unique=True,
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="squads.groups"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "default_permissions": (),
            },
        ),
        migrations.CreateModel(
            name="AssetsFilter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "description",
                    models.CharField(help_text="Filter Name.", max_length=500),
                ),
                (
                    "assets",
                    models.ManyToManyField(
                        help_text="Users must have at least <strong>one</strong> of the selected assets with <strong>one</strong> character.",
                        to="eveuniverse.evetype",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
