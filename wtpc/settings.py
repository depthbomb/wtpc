from enum import auto, StrEnum
from PySide6.QtCore import QSettings
from wtpc import APP_SETTINGS_FILE_PATH, USER_SETTINGS_FILE_PATH

app_settings = QSettings(str(APP_SETTINGS_FILE_PATH), QSettings.Format.IniFormat)
user_settings = QSettings(str(USER_SETTINGS_FILE_PATH), QSettings.Format.IniFormat)

class AppSettingsKeys(StrEnum):
    ACCESS_TOKEN = auto()
    ACCESS_TOKEN_EXPIRES = auto()

class UserSettingsKeys(StrEnum):
    CLIENT_ID = auto()
    CLIENT_SECRET = auto()
    REGION = auto()
    SEND_NOTIFICATIONS = auto()
