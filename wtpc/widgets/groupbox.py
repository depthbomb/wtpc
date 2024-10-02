from enum import auto, Flag
from typing import Optional
from PySide6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout

class GroupBox(QGroupBox):
    """
    A wrapper around `QGroupBox` to simplify creating group box widgets.
    """
    class InnerLayout(Flag):
        Vertical = auto()
        Horizontal = auto()
        Form = auto()

    def __init__(self, inner_layout: InnerLayout, *, title: Optional[str] = None, parent: Optional[QWidget] = None):
        super().__init__(title, parent)

        if inner_layout == GroupBox.InnerLayout.Vertical:
            self.layout = QVBoxLayout()
        elif inner_layout == GroupBox.InnerLayout.Horizontal:
            self.layout = QHBoxLayout()
        else:
            self.layout = QFormLayout()

        self.setLayout(self.layout)

    def addWidget(self, widget: QWidget):
        self.layout.addWidget(widget)
