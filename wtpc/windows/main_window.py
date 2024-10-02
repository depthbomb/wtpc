from random import random
from datetime import datetime, timedelta
from wtpc.notifier import show_notification
from wtpc.widgets.square_button import SquareButton
from wtpc.price_check_worker import PriceCheckWorker
from PySide6.QtCore import Qt, Slot, QTimer, QProcess
from PySide6.QtGui import QFont, QIcon, QFontDatabase
from wtpc.windows.settings_window import SettingsWindow
from wtpc import APP_DISPLAY_NAME, NOTIFICATION_HERO_PATH
from wtpc.settings import user_settings, UserSettingsKeys
from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QDialog,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QApplication
)

class MainWindow(QWidget):
    _first_check = True
    _last_price = 0
    _next_update = 0

    def __init__(self):
        super().__init__()

        # Worker setup
        self.worker = PriceCheckWorker()
        self.worker.error.connect(self._on_worker_error)
        self.worker.price_updated.connect(self._on_token_price_updated)

        # Time display timer setup
        self.next_update_timer = QTimer()
        self.next_update_timer.setInterval(1_000)
        self.next_update_timer.setSingleShot(False)
        self.next_update_timer.timeout.connect(self._on_next_update_timer_timeout)

        # Load custom font
        self.display_font = QFontDatabase.applicationFontFamilies(
            QFontDatabase.addApplicationFont(':fonts/frizquadrata.ttf')
        )

        # Create the main frame in which all other widgets are parented to
        frame = QFrame(self)
        frame.setFixedSize(960, 540)
        frame.setStyleSheet('background-image: url(:images/background.webp);background-repeat: no-repeat')

        # Create the layout within the frame
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self._create_header_controls(frame))
        layout.addSpacerItem(QSpacerItem(0, 350, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        layout.addWidget(self._create_status_label(frame))
        layout.addWidget(self._create_timestamp_label(frame))
        layout.addWidget(self._create_error_label(frame))

        # Set window properties
        self.setLayout(layout)
        self.setWindowTitle('WoW Token Price Checker')
        self.setWindowIcon(QIcon(':icons/icon.ico'))
        self.setFixedSize(frame.size())

        # Call the initial price check
        self.worker.check_price()

        # Start next update time display timer
        self.next_update_timer.start()

    #region Signal Handlers
    @Slot(str)
    def _on_worker_error(self, error_message: str):
        self.error_label.setText(f'{error_message}')

    @Slot(int, int)
    def _on_token_price_updated(self, price: int, last_updated: int):
        date = datetime.fromtimestamp(last_updated)

        self._next_update = date + timedelta(minutes=20)

        has_changed = self._last_price != price
        should_notify = user_settings.value(UserSettingsKeys.SEND_NOTIFICATIONS, False, bool)

        self.status.setText(f'{price:,}')
        self.timestamp.setText(f'Updated: {date}')
        self.error_label.setText('')

        if should_notify and has_changed and not self._first_check:
            self._send_notification(f'Current Price: {price:,}')

        if self._first_check:
            self._first_check = False

        self._last_price = price

    @Slot()
    def _on_next_update_timer_timeout(self):
        now = datetime.now()
        next_update_time_remaining = self._next_update - now
        next_update_total_seconds = int(next_update_time_remaining.total_seconds())
        next_update_minutes = next_update_total_seconds // 60
        next_update_seconds = next_update_total_seconds % 60
        use_silly_prefix = random() < (50 / 100)

        if next_update_total_seconds <= 0:
            self.setWindowTitle(f'[{'Soon™' if use_silly_prefix else 'Waiting...'}] {APP_DISPLAY_NAME}')
        else:
            self.setWindowTitle(f'[{next_update_minutes:02}:{next_update_seconds:02}] {APP_DISPLAY_NAME}')

    @Slot()
    def _on_settings_button_clicked(self):
        sw = SettingsWindow()
        if sw.exec() == QDialog.DialogCode.Accepted:
            if sw.should_restart:
                args = QApplication.arguments()
                QApplication.quit()
                QProcess.startDetached(args[0], args)
    #endregion

    #region UI Setup
    def _create_header_controls(self, parent: QFrame) -> QWidget:
        widget = QWidget(parent)
        layout = QHBoxLayout()

        self.settings_button = SquareButton(':images/options.png', shortcut='ALT+S')
        self.settings_button.clicked.connect(self._on_settings_button_clicked)

        layout.addSpacerItem(QSpacerItem(0, 16, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.settings_button)

        widget.setLayout(layout)

        return widget

    def _create_status_label(self, parent: QFrame) -> QLabel:
        self.status = QLabel('Loading...', parent)
        self.status.setFont(QFont(self.display_font, 36))
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet('color: #fff')

        return self.status

    def _create_timestamp_label(self, parent: QFrame) -> QLabel:
        self.timestamp = QLabel('...', parent)
        self.timestamp.setFont(QFont(self.display_font, 12))
        self.timestamp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timestamp.setStyleSheet('margin-top: 10px;color: #fff')

        return self.timestamp

    def _create_error_label(self, parent: QFrame) -> QLabel:
        self.error_label = QLabel(parent)
        self.error_label.setFont(QFont(self.display_font, 11))
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet('color: red')

        return self.error_label
    #endregion

    def _send_notification(self, message: str) -> None:
        show_notification(title = message, image_path=NOTIFICATION_HERO_PATH)
