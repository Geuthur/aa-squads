# Squads module for AllianceAuth.<a name="aa-squads"></a>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/aa-squads/master.svg)](https://results.pre-commit.ci/latest/github/Geuthur/aa-squads/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/Geuthur/aa-squads/actions/workflows/autotester.yml/badge.svg)](https://github.com/Geuthur/aa-squads/actions/workflows/autotester.yml)
[![codecov](https://codecov.io/gh/Geuthur/aa-squads/graph/badge.svg?token=5CWREOQKGZ)](https://codecov.io/gh/Geuthur/aa-squads)

- [AA Squads](#aa-ledger)
  - [Features](#features)
  - [Upcoming](#upcoming)
  - [Installation](#features)
    - [Step 1 - Install the Package](#step1)
    - [Step 2 - Configure Alliance Auth](#step2)
    - [Step 3 - Add the Scheduled Tasks and Settings](#step3)
    - [Step 4 - Migration to AA](#step4)
    - [Step 5 - Setting up Permissions](#step5)
    - [Step 6 - (Optional) Setting up Compatibilies](#step6)
  - [Highlights](#highlights)

## Features<a name="features"></a>

- Squads with Icons
- Req. Skills Check
- Html Supportive Description
- Overview which User has Req. Skills for Skillsets
-

## Upcoming<a name="upcoming"></a>

- Asset Check (If the User has the Hull of the Ship).
- Updating squad membership on state change.

## Installation<a name="installation"></a>

> \[!NOTE\]
> AA Ledger needs at least Alliance Auth v4.0.0
> Please make sure to update your Alliance Auth before you install this APP

### Step 1 - Install the Package<a name="step1"></a>

Make sure you're in your virtual environment (venv) of your Alliance Auth then install the pakage.

```shell
pip install aa-squads
```

### Step 2 - Configure Alliance Auth<a name="step2"></a>

Configure your Alliance Auth settings (`local.py`) as follows:

- Add `'allianceauth.corputils',` to `INSTALLED_APPS`
- Add `'eveuniverse',` to `INSTALLED_APPS`
- Add `'memberaudit',` to `INSTALLED_APPS`
- Add `'ledger',` to `INSTALLED_APPS`

### Step 3 - Add the Scheduled Tasks<a name="step3"></a>

At the Moment it is not implemented yet.

### Step 4 - Migration to AA<a name="step4"></a>

```shell
python manage.py collectstatic
python manage.py migrate
```

### Step 5 - Setting up Permissions<a name="step5"></a>

With the Following IDs you can set up the permissions for the Ledger

| ID              | Description                           |                                                                        |
| :-------------- | :------------------------------------ | :--------------------------------------------------------------------- |
| `basic_access`  | Can access the Squads module          | All Members with the Permission can access the Squads.                 |
| `admin_access`  | Can Manage Squads                     | Manage Squads Module.                                                  |
| `squad_manager` | Can Create Squads & Manage own Squads | Manage Squads like Edit, Create Squads, Approve, Decline Request, etc. |

### Step 6 - (Optional) Setting up Compatibilies<a name="step6"></a>

The Following Settings can be setting up in the `local.py`

- SQUADS_APP_NAME:          `"YOURNAME"`     - Set the name of the APP
- SQUADS_LOGGER_USE:        `True / False`   - Set to use own Logger File

If you set up SQUADS_LOGGER_USE to `True` you need to add the following code below:

```python
LOGGING_SQUADS = {
    "handlers": {
        "squads_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "log/squads.log"),
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 5,
        },
    },
    "loggers": {
        "squads": {
            "handlers": ["squads_file", "console"],
            "level": "INFO",
        },
    },
}
LOGGING["handlers"].update(LOGGING_SQUADS["handlers"])
LOGGING["loggers"].update(LOGGING_SQUADS["loggers"])
```

## Highlights<a name="highlights"></a>

> \[!NOTE\]
> Contributing
> You want to improve the project?
> Just Make a [Pull Request](https://github.com/Geuthur/aa-squads/pulls) with the Guidelines.
> We Using pre-commit
