from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QPushButton(QPushButton):
    base_font = QFont("맑은 고딕")

    def __init__(self, *__args):
        self.size = None
        super(QPushButton, self).__init__(*__args)
        self.icon_size = (self.iconSize().width(), self.iconSize().height())
        self.pressed.connect(self.decrease_size)
        self.released.connect(self.reset_size)

    def decrease_size(self):
        self.size = self.font().pointSize()
        self.base_font.setPointSize(self.size - 1)
        self.setFont(self.base_font)
        self.setIconSize(QSize(self.icon_size[0] - 1, self.icon_size[1] - 1))

    def reset_size(self):
        self.base_font.setPointSize(self.size)
        self.setFont(self.base_font)
        self.setIconSize(QSize(self.icon_size[0], self.icon_size[1]))
