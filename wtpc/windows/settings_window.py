from PySide6.QtCore import Qt, Slot
from wtpc.widgets.groupbox import GroupBox
from PySide6.QtGui import QIcon, QCloseEvent
from wtpc import GITHUB_URL, VERSION_STRING, APP_DISPLAY_NAME
from wtpc.settings import app_settings, user_settings, AppSettingsKeys, UserSettingsKeys
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QDialog,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

class SettingsWindow(QDialog):
    should_restart = False

    def __init__(self, *, is_intro = False):
        super().__init__()

        self.is_intro = is_intro

        layout = QFormLayout()
        layout.addRow('Client ID', self._create_client_id_input())
        layout.addRow('Client Secret', self._create_client_secret_input())
        layout.addRow('Region', self._create_region_input())
        layout.addRow('Access Token', self._create_access_token_display())
        layout.addRow('Access Token Expiration', self._create_access_token_expiration_display())
        layout.addRow(self._create_send_notifications_checkbox())

        if is_intro:
            layout.addRow(self._create_intro())

        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout.addRow(self._create_save_button_row())

        self.setLayout(layout)
        self.setWindowTitle('Settings')
        self.setWindowIcon(QIcon(':images/options.png'))
        self.adjustSize()
        self.setFixedWidth(450)
        self.setFixedSize(self.size())

        self._populate_inputs()

    #region Signal Handlers
    @Slot()
    def _on_inputs_changed(self):
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        should_disable_buttons = len(client_id) == 0 or len(client_secret) == 0

        if not self.is_intro:
            self.reset_button.setDisabled(should_disable_buttons)

        self.save_button.setDisabled(should_disable_buttons)

    @Slot()
    def _on_reset_button_clicked(self):
        mb = QMessageBox()
        mb.setWindowIcon(QIcon(':icons/icon.ico'))
        mb.setWindowTitle('Reset Settings')
        mb.setIcon(QMessageBox.Icon.Warning)
        mb.setText('This will clear your settings and restart the application.<br>Would you like to continue?')
        mb.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        if mb.exec() == QMessageBox.StandardButton.No:
            return

        self.reset_button.setDisabled(True)
        self.save_button.setDisabled(True)

        app_settings.clear()
        user_settings.clear()

        self.should_restart = True
        self.accept()

    @Slot()
    def _on_save_button_clicked(self):
        self.save_button.setDisabled(True)

        user_settings.setValue(UserSettingsKeys.CLIENT_ID, self.client_id_input.text().strip())
        user_settings.setValue(UserSettingsKeys.CLIENT_SECRET, self.client_secret_input.text().strip())
        user_settings.setValue(UserSettingsKeys.REGION, str(self.region_input.currentData()))
        user_settings.setValue(UserSettingsKeys.SEND_NOTIFICATIONS, self.send_notifications_checkbox.isChecked())

        self.accept()
    #endregion

    #region Overrides
    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.reject()
    #endregion

    #region UI Setup
    def _create_intro(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        groupbox = GroupBox(GroupBox.InnerLayout.Vertical, title='Info')
        intro = QLabel(f'<i>{APP_DISPLAY_NAME}</i> gets its data directly from Blizzard\'s World of Warcraft API. '
                       'Because of this, you\'ll need to create a "client" and provide its credentials.<br><br>Click '
                       '<a href="https://develop.battle.net/access/clients">here</a> to '
                       'visit the client management page.')
        intro.setWordWrap(True)
        intro.setOpenExternalLinks(True)
        groupbox.addWidget(intro)

        layout.addWidget(groupbox)

        widget.setLayout(layout)

        return widget

    def _create_client_id_input(self) -> QLineEdit:
        self.client_id_input = QLineEdit()
        self.client_id_input.setMaxLength(32)
        self.client_id_input.setPlaceholderText('Battle.net Client ID')
        self.client_id_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.client_id_input.textChanged.connect(self._on_inputs_changed)

        return self.client_id_input

    def _create_client_secret_input(self) -> QLineEdit:
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setMaxLength(32)
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_secret_input.setPlaceholderText('Battle.net Client Secret')
        self.client_secret_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.client_secret_input.textChanged.connect(self._on_inputs_changed)

        return self.client_secret_input

    def _create_region_input(self) -> QComboBox:
        self.region_input = QComboBox()
        self.region_input.addItem('North America', 'dynamic-us')
        self.region_input.addItem('Europe', 'dynamic-eu')
        self.region_input.addItem('Korea', 'dynamic-kr')
        self.region_input.addItem('Taiwan', 'dynamic-tw')

        return self.region_input

    def _create_access_token_display(self) -> QLineEdit:
        self.access_token_input = QLineEdit()
        self.access_token_input.setDisabled(True)
        self.access_token_input.setPlaceholderText('No access token set')

        return self.access_token_input

    def _create_access_token_expiration_display(self) -> QLineEdit:
        self.access_token_expiration_input = QLineEdit()
        self.access_token_expiration_input.setDisabled(True)
        self.access_token_expiration_input.setPlaceholderText('No access token expiration set')

        return self.access_token_expiration_input

    def _create_send_notifications_checkbox(self) -> QCheckBox:
        self.send_notifications_checkbox = QCheckBox('Send toast notifications on price change')

        return self.send_notifications_checkbox

    def _create_save_button_row(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        about_info = QLabel(f'<a href="{GITHUB_URL}">{VERSION_STRING}</a>')
        about_info.setOpenExternalLinks(True)

        self.reset_button = QPushButton('&Reset')
        self.reset_button.clicked.connect(self._on_reset_button_clicked)
        self.reset_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.reset_button.setEnabled(False)

        self.save_button = QPushButton('&Save')
        self.save_button.clicked.connect(self._on_save_button_clicked)
        self.save_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.save_button.setEnabled(False)

        layout.addWidget(about_info)
        layout.addStretch()
        layout.addWidget(self.reset_button)
        layout.addWidget(self.save_button)

        widget.setLayout(layout)

        return widget
    #endregion

    def _populate_inputs(self):
        self.client_id_input.setText(user_settings.value(UserSettingsKeys.CLIENT_ID))
        self.client_secret_input.setText(user_settings.value(UserSettingsKeys.CLIENT_SECRET))
        self.region_input.setCurrentIndex(
            self.region_input.findData(
                user_settings.value(UserSettingsKeys.REGION)
            )
        )
        self.access_token_input.setText(app_settings.value(AppSettingsKeys.ACCESS_TOKEN))
        self.access_token_expiration_input.setText(str(app_settings.value(AppSettingsKeys.ACCESS_TOKEN_EXPIRES)))
        self.send_notifications_checkbox.setChecked(user_settings.value(UserSettingsKeys.SEND_NOTIFICATIONS, False, bool))
