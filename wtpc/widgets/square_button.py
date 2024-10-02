from typing import Optional
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtGui import QPixmap, QShortcut, QMouseEvent, QKeySequence

class SquareButton(QLabel):
    clicked = Signal()

    def __init__(self, icon: str, *, shortcut: Optional[str] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)

        if shortcut is not None:
            self.shortcut = QShortcut(QKeySequence(shortcut), self)
            self.shortcut.activated.connect(self._on_shortcut_activated)

        self.up_image = QPixmap(':images/button_up.png')
        self.down_image = QPixmap(':images/button_down.png')
        self.disabled_image = QPixmap(':images/button_disabled.png')
        self.icon_image = QPixmap(icon)

        self.button_frame = QLabel(self)
        self.button_frame.setPixmap(self.up_image)
        self.button_frame.setFixedSize(32, 32)
        self.button_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon = QLabel(self)
        self.icon.setPixmap(self.icon_image)
        self.icon.setFixedSize(16, 16)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon.move(8, 9)

        self.setFixedSize(32, 32)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    #region Signal Handlers
    @Slot()
    def _on_shortcut_activated(self):
        self.clicked.emit()
    #endregion

    #region Overrides
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.icon.move(7, 10)
            self.button_frame.setPixmap(self.down_image)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.icon.move(8, 9)
            self.button_frame.setPixmap(self.up_image)
            self.clicked.emit()

        super().mouseReleaseEvent(event)
    #endregion
