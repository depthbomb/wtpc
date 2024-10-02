from ctypes import windll
from sys import argv, exit
from wtpc.windows.main_window import MainWindow
from contextlib import suppress, contextmanager
from PySide6.QtCore import QFile, QSharedMemory
from PySide6.QtWidgets import QDialog, QApplication
from wtpc.windows.settings_window import SettingsWindow
from wtpc.settings import user_settings, UserSettingsKeys
from wtpc.notifier import install_aumid, is_aumid_installed, clear_notifications
from wtpc import (
    APP_ORG,
    APP_NAME,
    DATA_DIR,
    VERSION_STRING,
    APP_DISPLAY_NAME,
    APP_USER_MODEL_ID,
    NOTIFICATION_ASSETS
)

def _start(args: list[str]) -> int:
    with _single_instance():
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        app = QApplication(args)
        app.setApplicationName(APP_NAME)
        app.setApplicationDisplayName(APP_DISPLAY_NAME)
        app.setApplicationVersion(VERSION_STRING)
        app.setOrganizationName(APP_ORG)
        app.aboutToQuit.connect(lambda: clear_notifications())

        # noinspection PyUnresolvedReferences
        import wtpc.fonts
        # noinspection PyUnresolvedReferences
        import wtpc.icons
        # noinspection PyUnresolvedReferences
        import wtpc.images

        # Copy some resources to the disk so we can use them in toast notifications.
        for asset_path, resource_name in NOTIFICATION_ASSETS.items():
            if not asset_path.exists():
                hero_resource = QFile(resource_name)
                hero_resource.copy(asset_path)

        # Add the app's AUMID to the registry
        if not is_aumid_installed():
            install_aumid()

        # Show the settings dialog if either client credential is missing
        has_credentials = None not in [
            user_settings.value(UserSettingsKeys.CLIENT_ID, None),
            user_settings.value(UserSettingsKeys.CLIENT_SECRET, None)
        ]
        if not has_credentials:
            # Set some default settings
            user_settings.setValue(UserSettingsKeys.REGION, 'dynamic-us')
            user_settings.setValue(UserSettingsKeys.SEND_NOTIFICATIONS, False)
            sw = SettingsWindow(is_intro=True)
            if sw.exec() == QDialog.DialogCode.Rejected:
                # Rejected, in this case, means that the dialog was closed without clicking the save button
                app.quit()
                return 0

        mw = MainWindow()
        mw.show()

        return app.exec()

@contextmanager
def _single_instance():
    shared_mem = QSharedMemory('wtpc_mutex')
    if not shared_mem.create(1):
        QApplication.quit()
        return
    try:
        yield
    finally:
        shared_mem.detach()

if __name__ == '__main__':
    with suppress(Exception):
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)

    exit(_start(argv))
