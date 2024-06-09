"""
App Settings
"""

# Django
from app_utils.app_settings import clean_setting

TESTING_MODE = False
# Set Test Mode True or False

# Set Naming on Auth Hook
SQUADS_APP_NAME = clean_setting("SQUADS_APP_NAME", "Squads")

# Caching Key for Caching System
STORAGE_BASE_KEY = "squads_storage_"

# zKillboard - https://zkillboard.com/
EVE_BASE_URL = "https://esi.evetech.net/"
EVE_API_URL = "https://esi.evetech.net/latest/"
EVE_BASE_URL_REGEX = r"^http[s]?:\/\/esi.evetech\.net\/"

# If True you need to set up the Logger
SQUADS_LOGGER_USE = clean_setting("SQUADS_LOGGER_USE", False)
