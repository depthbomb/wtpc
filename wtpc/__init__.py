from pathlib import Path
from PySide6.QtCore import QStandardPaths

VERSION = (1, 0, 0, 0)
VERSION_STRING = '.'.join(str(v) for v in VERSION)

GITHUB_URL = 'https://github.com/depthbomb/wtpc'

APP_NAME = 'wtpc'
APP_DISPLAY_NAME = 'WoW Token Price Checker'
APP_ORG = 'Caprine Logic'
APP_USER_MODEL_ID = u'CaprineLogic.Wtpc'

BINARY_DIR = Path(__file__).parent.parent.absolute()
APPDATA_DIR = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
DATA_DIR = APPDATA_DIR / APP_ORG / APP_NAME
APP_SETTINGS_FILE_PATH = DATA_DIR / 'app.settings'
USER_SETTINGS_FILE_PATH = DATA_DIR / 'user.settings'
NOTIFICATION_HERO_PATH = DATA_DIR / 'background.webp'
NOTIFICATION_ICON_PATH = DATA_DIR / 'icon.ico'

NOTIFICATION_ASSETS = {
    NOTIFICATION_HERO_PATH: ':images/background.webp',
    NOTIFICATION_ICON_PATH: ':icons/icon.ico',
}
