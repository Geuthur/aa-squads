# Squads module for AllianceAuth.<a name="aa-squads"></a>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/aa-squads/master.svg)](https://results.pre-commit.ci/latest/github/Geuthur/aa-squads/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checks](https://github.com/Geuthur/aa-squads/actions/workflows/autotester.yml/badge.svg)](https://github.com/Geuthur/aa-squads/actions/workflows/autotester.yml)
[![codecov](https://codecov.io/gh/Geuthur/aa-squads/graph/badge.svg?token=yPAkMfj3cD)](https://codecov.io/gh/Geuthur/aa-squads)

- [AA Squads](#aa-squads)
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

- Detailed Squad Information (html)
- Squad Filters
- Overview of Members in Squads

## Upcoming<a name="upcoming"></a>

- Updating Squad Membership on state change.
- Updating Members State on Filter changes.
- More Filters.

## Installation<a name="installation"></a>

> \[!NOTE\]
> AA Squads needs at least Alliance Auth v4.0.0
> Please make sure to update your Alliance Auth before you install this APP

### Step 1 - Install the Package<a name="step1"></a>

Make sure you're in your virtual environment (venv) of your Alliance Auth then install the pakage.

```shell
pip install aa-squads
```

### Step 2 - Configure Alliance Auth<a name="step2"></a>

Configure your Alliance Auth settings (`local.py`) as follows:

- Add `'eveuniverse',` to `INSTALLED_APPS`
- Add `'memberaudit',` to `INSTALLED_APPS`
- Add `'squads',` to `INSTALLED_APPS`

### Step 3 - Add the Scheduled Tasks<a name="step3"></a>

At the Moment it is not implemented yet.

### Step 4 - Migration to AA<a name="step4"></a>

```shell
python manage.py collectstatic
python manage.py migrate
```

### Step 5 - Setting up Permissions<a name="step5"></a>

With the Following IDs you can set up the permissions for the Squads

| ID              | Description                  |                                                                        |
| :-------------- | :--------------------------- | :--------------------------------------------------------------------- |
| `basic_access`  | Can access the Squads module | All Members with the Permission can access the Squads.                 |
| `squad_manager` | Can Create / Manage Squads   | Manage Squads like Edit, Create Squads, Approve, Decline Request, etc. |
| `squad_admin`   | Can View All Squads          | Can View all Squads.                                                   |

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

![Screenshot 2024-06-09 164402](https://github.com/Geuthur/aa-squads/assets/761682/5bf9eb99-1d61-4562-9bb3-02f9d3ae3ac2)
![Screenshot 2024-06-09 164408](https://github.com/Geuthur/aa-squads/assets/761682/5a79ca79-145a-4558-befc-2b0529675712)
![Screenshot 2024-06-09 164431](https://github.com/Geuthur/aa-squads/assets/761682/b79f1519-0a70-483b-9def-3ec120e4cd46)
![Screenshot 2024-06-09 164502](https://github.com/Geuthur/aa-squads/assets/761682/1249d415-9d72-4cf0-8c62-d1ac4db72986)
![Screenshot 2024-06-09 164516](https://github.com/Geuthur/aa-squads/assets/761682/66608190-42db-4780-9b10-c8832d96cb2d)
![Screenshot 2024-06-09 164508](https://github.com/Geuthur/aa-squads/assets/761682/c989d2ed-6602-441b-b903-b7f22ecf69c0)
![Screenshot 2024-06-10 235804](https://github.com/Geuthur/aa-squads/assets/761682/e0c816e6-2b5b-421f-add3-57628ad05004)

> \[!NOTE\]
> Contributing
> You want to improve the project?
> Just Make a [Pull Request](https://github.com/Geuthur/aa-squads/pulls) with the Guidelines.
> We Using pre-commit
